import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models.binance_key import BinanceAPIKey
from app.models.bot import Bot, BotRuntimeState
from app.models.order import Order
from app.services.binance_service import BinanceService, BinanceAPIError
from app.services.encryption_service import decrypt_text
from app.services.risk_manager import calculate_exit_prices, calculate_usable_amount
from app.services.safety_lock import enforce_safety_lock
from app.services.strategy_engine import check_trend_breakout_signal, check_volatility
from app.services.trade_logger import log_trade, log_safety_event

settings = get_settings()


def get_or_create_state(db: Session, bot_id: int) -> BotRuntimeState:
    state = db.query(BotRuntimeState).filter(BotRuntimeState.bot_id == bot_id).first()
    if not state:
        state = BotRuntimeState(bot_id=bot_id)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def _get_usdt_balance(account: dict) -> float:
    for asset in account.get("balances", []):
        if asset.get("asset") == "USDT":
            return float(asset.get("free", 0.0))
    return 0.0


def _parse_order_avg(order_data: dict, fallback_price: float, quote_qty: float) -> tuple[float, float, float, str]:
    executed_qty = float(order_data.get("executedQty") or order_data.get("executed_qty") or 0.0)
    quote = float(order_data.get("cummulativeQuoteQty") or order_data.get("cumulative_quote_qty") or quote_qty)
    avg = quote / executed_qty if executed_qty > 0 else fallback_price
    order_id = str(order_data.get("orderId") or order_data.get("order_id") or "PAPER")
    return avg, executed_qty, quote, order_id


async def run_bot_once(db: Session, bot: Bot) -> dict:
    api_key_row: Optional[BinanceAPIKey] = db.query(BinanceAPIKey).filter(BinanceAPIKey.user_id == bot.user_id).order_by(BinanceAPIKey.id.desc()).first()
    if not api_key_row:
        log_safety_event(db, "NO_API_KEY", "No Binance API key found", "Bot skipped", bot.id)
        return {"ok": False, "message": "No Binance API key found"}

    api_key = decrypt_text(api_key_row.api_key_encrypted)
    secret_key = decrypt_text(api_key_row.secret_key_encrypted)
    client = BinanceService(api_key, secret_key, api_key_row.is_testnet)
    state = get_or_create_state(db, bot.id)

    try:
        permissions = await client.api_restrictions()
        account = await client.account()
        available_usdt = _get_usdt_balance(account)
        klines = await client.klines(bot.symbol, interval="5m", limit=30)
        price_data = await client.ticker_price(bot.symbol)
        current_price = float(price_data["price"])
    except BinanceAPIError as exc:
        log_safety_event(db, "BINANCE_API_ERROR", str(exc), "Bot skipped", bot.id)
        return {"ok": False, "message": str(exc)}
    except Exception as exc:
        log_safety_event(db, "BOT_ERROR", str(exc), "Bot skipped", bot.id)
        return {"ok": False, "message": str(exc)}

    volatility = check_volatility(klines)
    if volatility > bot.max_allowed_volatility_percent_5m:
        log_safety_event(db, "VOLATILITY_BLOCK", f"5m volatility {volatility:.2f}% too high", "Blocked new trade", bot.id)
        return {"ok": False, "message": "Volatility too high"}

    decision = enforce_safety_lock(db, bot, state, available_usdt, permissions)
    if not decision.ok:
        return {"ok": False, "message": decision.reason}

    # Exit monitor for existing paper/live position.
    if state.current_position == "long" and state.entry_price > 0:
        stop_price, tp_price = calculate_exit_prices(state.entry_price, bot.stop_loss_percent, bot.take_profit_percent)
        if current_price <= stop_price or current_price >= tp_price:
            is_loss = current_price <= stop_price
            pnl = (current_price - state.entry_price) * state.entry_quantity
            state.today_pnl += pnl
            state.unrealized_pnl = 0
            state.current_position = "none"
            state.last_trade_at = datetime.utcnow()
            state.consecutive_losses = state.consecutive_losses + 1 if is_loss else 0
            if state.consecutive_losses >= 3:
                state.cooldown_until = datetime.utcnow() + timedelta(hours=24)
            else:
                state.cooldown_until = datetime.utcnow() + timedelta(minutes=bot.cooldown_minutes if is_loss else 0)

            if not bot.paper_trading and settings.enable_live_trading:
                try:
                    sell_order = await client.place_market_sell_qty(bot.symbol, state.entry_quantity)
                    log_trade(db, "Live exit order executed", bot.id, "INFO", sell_order)
                except Exception as exc:
                    log_safety_event(db, "LIVE_SELL_ERROR", str(exc), "Manual review required", bot.id)
                    return {"ok": False, "message": str(exc)}

            db.add(state)
            db.commit()
            event = "STOP_LOSS_TRIGGERED" if is_loss else "TAKE_PROFIT_TRIGGERED"
            log_safety_event(db, event, f"Exit at {current_price}; PnL={pnl:.8f}", "Position closed", bot.id)
            return {"ok": True, "message": event, "pnl": pnl}

        state.unrealized_pnl = (current_price - state.entry_price) * state.entry_quantity
        db.add(state)
        db.commit()
        return {"ok": True, "message": "Position monitored", "unrealized_pnl": state.unrealized_pnl}

    signal = check_trend_breakout_signal(klines)
    if not signal.get("buy"):
        log_trade(db, f"No entry: {signal.get('reason')}", bot.id, "INFO", signal)
        return {"ok": True, "message": "No valid signal", "signal": signal}

    usable_amount = calculate_usable_amount(available_usdt, bot.max_usable_percent)
    if usable_amount <= 0:
        log_safety_event(db, "NO_USABLE_BALANCE", "Usable USDT is zero", "Blocked new trade", bot.id)
        return {"ok": False, "message": "No usable balance"}

    if bot.paper_trading or not settings.enable_live_trading:
        executed_qty = usable_amount / current_price
        order_data = {"order_id": "PAPER", "executed_qty": executed_qty, "cumulative_quote_qty": usable_amount, "price": current_price}
        status = "PAPER_FILLED"
    else:
        order_data = await client.place_market_buy_quote(bot.symbol, usable_amount)
        status = order_data.get("status", "FILLED")

    avg_price, executed_qty, quote, order_id = _parse_order_avg(order_data, current_price, usable_amount)
    order = Order(
        bot_id=bot.id,
        binance_order_id=order_id,
        symbol=bot.symbol,
        side="BUY",
        order_type="MARKET",
        price=avg_price,
        quantity=executed_qty,
        quote_order_qty=quote,
        status=status,
        executed_qty=executed_qty,
        cummulative_quote_qty=quote,
    )
    db.add(order)
    state.current_position = "long"
    state.entry_price = avg_price
    state.entry_quantity = executed_qty
    state.used_capital = quote
    state.today_trade_count += 1
    state.last_trade_at = datetime.utcnow()
    state.safety_lock_status = "OK"
    db.add(state)
    db.commit()
    log_trade(db, "Entry order executed", bot.id, "INFO", {"order": order_data, "signal": signal})
    return {"ok": True, "message": "Entry executed", "paper_trading": bot.paper_trading, "entry_price": avg_price, "quantity": executed_qty}


async def bot_loop(session_factory):
    while True:
        db = session_factory()
        try:
            bots = db.query(Bot).filter(Bot.status == "running").all()
            for bot in bots:
                try:
                    await run_bot_once(db, bot)
                except Exception as exc:
                    log_safety_event(db, "BOT_LOOP_ERROR", str(exc), "Bot loop continued", bot.id)
        finally:
            db.close()
        await asyncio.sleep(settings.bot_loop_interval_seconds)

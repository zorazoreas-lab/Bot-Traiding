from datetime import datetime
from app.config import get_settings
from app.models.bot import Bot, BotRuntimeState

settings = get_settings()


class RiskDecision:
    def __init__(self, ok: bool, reason: str, event_type: str = "OK"):
        self.ok = ok
        self.reason = reason
        self.event_type = event_type


def calculate_usable_amount(total_usdt: float, max_usable_percent: float) -> float:
    percent = min(max_usable_percent, settings.max_allowed_usable_percent)
    return max(total_usdt * percent / 100.0, 0.0)


def check_basic_risk(bot: Bot, state: BotRuntimeState, available_usdt: float, api_permission: dict) -> RiskDecision:
    if api_permission.get("enableWithdrawals") is True:
        return RiskDecision(False, "Withdrawal permission is enabled", "WITHDRAWAL_PERMISSION_BLOCKED")

    trading_enabled = api_permission.get("enableSpotAndMarginTrading") or api_permission.get("enableTrading")
    if trading_enabled is False:
        return RiskDecision(False, "Trading permission is disabled", "TRADING_PERMISSION_BLOCKED")

    if bot.max_usable_percent > settings.max_allowed_usable_percent:
        return RiskDecision(False, f"Max usable percent cannot exceed {settings.max_allowed_usable_percent}%", "MAX_USABLE_PERCENT_BLOCK")

    if bot.stop_loss_percent <= 0:
        return RiskDecision(False, "Stop loss is required", "STOP_LOSS_REQUIRED")

    if bot.take_profit_percent <= 0:
        return RiskDecision(False, "Take profit is required", "TAKE_PROFIT_REQUIRED")

    if bot.emergency_stop:
        return RiskDecision(False, "Emergency stop is active", "EMERGENCY_STOP")

    if state.cooldown_until and datetime.utcnow() < state.cooldown_until:
        return RiskDecision(False, f"Bot is in cooldown until {state.cooldown_until}", "COOLDOWN_ACTIVE")

    capital_basis = max(available_usdt, state.used_capital, 1.0)
    daily_loss_percent = abs(min(state.today_pnl, 0.0)) / capital_basis * 100.0
    if daily_loss_percent >= bot.daily_loss_limit_percent:
        return RiskDecision(False, "Daily loss limit reached", "DAILY_LOSS_LIMIT_HIT")

    if state.today_trade_count >= bot.max_trade_per_day:
        return RiskDecision(False, "Max trades per day reached", "MAX_TRADE_PER_DAY_HIT")

    reserve_required = available_usdt * bot.reserve_percent / 100.0
    usable = calculate_usable_amount(available_usdt, bot.max_usable_percent)
    if available_usdt - usable < reserve_required - 0.000001:
        return RiskDecision(False, "Reserve balance protection triggered", "RESERVE_BALANCE_PROTECTION")

    return RiskDecision(True, "Safe to trade")


def calculate_exit_prices(entry_price: float, stop_loss_percent: float, take_profit_percent: float) -> tuple[float, float]:
    stop_loss_price = entry_price * (1 - stop_loss_percent / 100.0)
    take_profit_price = entry_price * (1 + take_profit_percent / 100.0)
    return stop_loss_price, take_profit_price

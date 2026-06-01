from datetime import datetime, timedelta
from app.models.bot import Bot, BotRuntimeState
from app.services.risk_manager import calculate_usable_amount, check_basic_risk


def test_calculate_usable_amount_caps_at_70_percent():
    assert calculate_usable_amount(1000, 80) == 700


def test_blocks_withdrawal_permission():
    bot = Bot(max_usable_percent=50, stop_loss_percent=3, take_profit_percent=5, emergency_stop=False, daily_loss_limit_percent=5, max_trade_per_day=3, reserve_percent=50)
    state = BotRuntimeState(today_pnl=0, today_trade_count=0)
    decision = check_basic_risk(bot, state, 1000, {"enableWithdrawals": True, "enableSpotAndMarginTrading": True})
    assert decision.ok is False
    assert decision.event_type == "WITHDRAWAL_PERMISSION_BLOCKED"


def test_blocks_cooldown():
    bot = Bot(max_usable_percent=50, stop_loss_percent=3, take_profit_percent=5, emergency_stop=False, daily_loss_limit_percent=5, max_trade_per_day=3, reserve_percent=50)
    state = BotRuntimeState(today_pnl=0, today_trade_count=0, cooldown_until=datetime.utcnow()+timedelta(minutes=5))
    decision = check_basic_risk(bot, state, 1000, {"enableWithdrawals": False, "enableSpotAndMarginTrading": True})
    assert decision.ok is False
    assert decision.event_type == "COOLDOWN_ACTIVE"

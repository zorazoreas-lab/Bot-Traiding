from sqlalchemy.orm import Session
from app.models.bot import Bot, BotRuntimeState
from app.services.risk_manager import RiskDecision, check_basic_risk
from app.services.trade_logger import log_safety_event


def enforce_safety_lock(db: Session, bot: Bot, state: BotRuntimeState, available_usdt: float, api_permission: dict) -> RiskDecision:
    decision = check_basic_risk(bot, state, available_usdt, api_permission)
    if not decision.ok:
        state.safety_lock_status = decision.event_type
        db.add(state)
        db.commit()
        log_safety_event(db, decision.event_type, decision.reason, "Blocked new trade", bot.id)
    return decision

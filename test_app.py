import json
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.models.trade_log import TradeLog
from app.models.safety_event import SafetyEvent


def log_trade(db: Session, message: str, bot_id: Optional[int] = None, level: str = "INFO", data: Any = None):
    row = TradeLog(bot_id=bot_id, level=level, message=message, data_json=json.dumps(data, default=str) if data is not None else None)
    db.add(row)
    db.commit()
    return row


def log_safety_event(db: Session, event_type: str, reason: str, action_taken: str, bot_id: Optional[int] = None):
    row = SafetyEvent(bot_id=bot_id, event_type=event_type, reason=reason, action_taken=action_taken)
    db.add(row)
    db.commit()
    return row

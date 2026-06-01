from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order
from app.models.trade_log import TradeLog
from app.models.safety_event import SafetyEvent
from app.models.user import User
from app.schemas import ApiResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.get("/orders", response_model=ApiResponse)
def orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Order).order_by(Order.id.desc()).limit(100).all()
    data = [{
        "id": r.id, "bot_id": r.bot_id, "symbol": r.symbol, "side": r.side,
        "price": r.price, "quantity": r.quantity, "quote_order_qty": r.quote_order_qty,
        "status": r.status, "created_at": r.created_at.isoformat()
    } for r in rows]
    return ApiResponse(ok=True, message="Orders loaded", data=data)


@router.get("/logs", response_model=ApiResponse)
def logs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(TradeLog).order_by(TradeLog.id.desc()).limit(100).all()
    data = [{"id": r.id, "bot_id": r.bot_id, "level": r.level, "message": r.message, "data_json": r.data_json, "created_at": r.created_at.isoformat()} for r in rows]
    return ApiResponse(ok=True, message="Logs loaded", data=data)


@router.get("/safety-events", response_model=ApiResponse)
def safety_events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(SafetyEvent).order_by(SafetyEvent.id.desc()).limit(100).all()
    data = [{"id": r.id, "bot_id": r.bot_id, "event_type": r.event_type, "reason": r.reason, "action_taken": r.action_taken, "created_at": r.created_at.isoformat()} for r in rows]
    return ApiResponse(ok=True, message="Safety events loaded", data=data)

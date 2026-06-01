from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models.bot import Bot
from app.models.user import User
from app.schemas import ApiResponse, BotCreateRequest, BotOut
from app.utils.security import get_current_user
from app.services.bot_engine import get_or_create_state, run_bot_once
from app.services.trade_logger import log_safety_event, log_trade

router = APIRouter(prefix="/api/bots", tags=["bots"])
settings = get_settings()


@router.post("", response_model=ApiResponse)
def create_bot(payload: BotCreateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.max_usable_percent > settings.max_allowed_usable_percent:
        raise HTTPException(status_code=400, detail=f"Max usable percent cannot exceed {settings.max_allowed_usable_percent}%")
    if payload.stop_loss_percent <= 0 or payload.take_profit_percent <= 0:
        raise HTTPException(status_code=400, detail="Stop loss and take profit are required")
    bot = Bot(
        user_id=user.id,
        bot_name=payload.bot_name,
        symbol=payload.symbol.upper(),
        strategy_type=payload.strategy_type,
        paper_trading=payload.paper_trading,
        max_usable_percent=payload.max_usable_percent,
        reserve_percent=100 - payload.max_usable_percent,
        stop_loss_percent=payload.stop_loss_percent,
        take_profit_percent=payload.take_profit_percent,
        daily_loss_limit_percent=payload.daily_loss_limit_percent,
        max_trade_per_day=payload.max_trade_per_day,
        cooldown_minutes=payload.cooldown_minutes,
        status="stopped",
    )
    db.add(bot)
    db.commit()
    db.refresh(bot)
    get_or_create_state(db, bot.id)
    return ApiResponse(ok=True, message="Bot created", data=BotOut.model_validate(bot).model_dump())


@router.get("", response_model=ApiResponse)
def list_bots(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bots = db.query(Bot).filter(Bot.user_id == user.id).order_by(Bot.id.desc()).all()
    return ApiResponse(ok=True, message="Bots loaded", data=[BotOut.model_validate(b).model_dump() for b in bots])


@router.post("/{bot_id}/start", response_model=ApiResponse)
def start_bot(bot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot.status = "running"
    bot.emergency_stop = False
    db.add(bot)
    db.commit()
    log_trade(db, "Bot started", bot.id)
    return ApiResponse(ok=True, message="Bot started", data=BotOut.model_validate(bot).model_dump())


@router.post("/{bot_id}/pause", response_model=ApiResponse)
def pause_bot(bot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot.status = "paused"
    db.add(bot)
    db.commit()
    log_trade(db, "Bot paused", bot.id)
    return ApiResponse(ok=True, message="Bot paused")


@router.post("/{bot_id}/stop", response_model=ApiResponse)
def stop_bot(bot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot.status = "stopped"
    db.add(bot)
    db.commit()
    log_trade(db, "Bot stopped", bot.id)
    return ApiResponse(ok=True, message="Bot stopped")


@router.post("/{bot_id}/emergency-stop", response_model=ApiResponse)
def emergency_stop(bot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot.status = "locked"
    bot.emergency_stop = True
    db.add(bot)
    db.commit()
    log_safety_event(db, "EMERGENCY_STOP", "Manual emergency stop pressed", "Bot locked and new trades blocked", bot.id)
    return ApiResponse(ok=True, message="Emergency stop activated")


@router.post("/{bot_id}/run-once", response_model=ApiResponse)
async def run_once(bot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bot = db.query(Bot).filter(Bot.id == bot_id, Bot.user_id == user.id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    result = await run_bot_once(db, bot)
    return ApiResponse(ok=bool(result.get("ok")), message=result.get("message", "Run complete"), data=result)

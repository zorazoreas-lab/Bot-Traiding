from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.binance_key import BinanceAPIKey
from app.schemas import BinanceConnectRequest, ApiResponse
from app.utils.security import get_current_user
from app.services.encryption_service import encrypt_text, decrypt_text
from app.services.binance_service import BinanceService, BinanceAPIError

router = APIRouter(prefix="/api/binance", tags=["binance"])


def _latest_key(db: Session, user_id: int):
    return db.query(BinanceAPIKey).filter(BinanceAPIKey.user_id == user_id).order_by(BinanceAPIKey.id.desc()).first()


@router.post("/connect", response_model=ApiResponse)
async def connect_binance(payload: BinanceConnectRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    client = BinanceService(payload.api_key, payload.secret_key, payload.is_testnet)
    try:
        await client.account()
        restrictions = await client.api_restrictions()
    except BinanceAPIError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    row = BinanceAPIKey(
        user_id=user.id,
        api_key_encrypted=encrypt_text(payload.api_key),
        secret_key_encrypted=encrypt_text(payload.secret_key),
        is_testnet=payload.is_testnet,
        enable_reading=bool(restrictions.get("enableReading", True)),
        enable_trading=bool(restrictions.get("enableSpotAndMarginTrading", True)),
        enable_withdrawals=bool(restrictions.get("enableWithdrawals", False)),
        enable_internal_transfer=bool(restrictions.get("enableInternalTransfer", False)),
        ip_restrict=bool(restrictions.get("ipRestrict", False)),
        status="unsafe" if restrictions.get("enableWithdrawals") else "connected",
        last_checked_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    return ApiResponse(ok=True, message="Binance API connected", data={"status": row.status, "permissions": restrictions})


@router.get("/permission-check", response_model=ApiResponse)
async def permission_check(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = _latest_key(db, user.id)
    if not row:
        raise HTTPException(status_code=404, detail="No Binance API key found")
    client = BinanceService(decrypt_text(row.api_key_encrypted), decrypt_text(row.secret_key_encrypted), row.is_testnet)
    restrictions = await client.api_restrictions()
    row.enable_reading = bool(restrictions.get("enableReading", True))
    row.enable_trading = bool(restrictions.get("enableSpotAndMarginTrading", True))
    row.enable_withdrawals = bool(restrictions.get("enableWithdrawals", False))
    row.enable_internal_transfer = bool(restrictions.get("enableInternalTransfer", False))
    row.ip_restrict = bool(restrictions.get("ipRestrict", False))
    row.status = "unsafe" if row.enable_withdrawals else "connected"
    row.last_checked_at = datetime.utcnow()
    db.add(row)
    db.commit()
    return ApiResponse(ok=True, message="Permission checked", data=restrictions)


@router.get("/balance", response_model=ApiResponse)
async def balance(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = _latest_key(db, user.id)
    if not row:
        raise HTTPException(status_code=404, detail="No Binance API key found")
    client = BinanceService(decrypt_text(row.api_key_encrypted), decrypt_text(row.secret_key_encrypted), row.is_testnet)
    account = await client.account()
    non_zero = [b for b in account.get("balances", []) if float(b.get("free", 0)) > 0 or float(b.get("locked", 0)) > 0]
    return ApiResponse(ok=True, message="Balance loaded", data=non_zero)


@router.get("/price/{symbol}", response_model=ApiResponse)
async def price(symbol: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = _latest_key(db, user.id)
    if not row:
        # Public endpoint can still be called with empty client values in testnet mode.
        client = BinanceService("", "", True)
    else:
        client = BinanceService(decrypt_text(row.api_key_encrypted), decrypt_text(row.secret_key_encrypted), row.is_testnet)
    data = await client.ticker_price(symbol.upper())
    return ApiResponse(ok=True, message="Price loaded", data=data)

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.binance_key import BinanceAPIKey
from app.services.encryption_service import decrypt_text
from app.services.binance_service import BinanceService

settings = get_settings()


@dataclass
class BinanceCredentialBundle:
    client: BinanceService
    source: str
    is_testnet: bool
    row: Optional[BinanceAPIKey] = None


def latest_binance_key_row(db: Session, user_id: int) -> Optional[BinanceAPIKey]:
    return (
        db.query(BinanceAPIKey)
        .filter(BinanceAPIKey.user_id == user_id)
        .order_by(BinanceAPIKey.id.desc())
        .first()
    )


def get_binance_credentials(db: Session, user_id: int) -> Optional[BinanceCredentialBundle]:
    """Return Binance credentials from ENV first when requested, otherwise DB.

    This keeps the original web/database key flow while supporting Railway
    Variables:
      BINANCE_API_KEY_SOURCE=env
      BINANCE_API_KEY=...
      BINANCE_SECRET_KEY=...
    """
    if settings.binance_api_key_source.lower() == "env" and settings.binance_api_key and settings.binance_secret_key:
        return BinanceCredentialBundle(
            client=BinanceService(settings.binance_api_key, settings.binance_secret_key, settings.binance_use_testnet),
            source="env",
            is_testnet=settings.binance_use_testnet,
            row=None,
        )

    row = latest_binance_key_row(db, user_id)
    if not row:
        return None
    return BinanceCredentialBundle(
        client=BinanceService(decrypt_text(row.api_key_encrypted), decrypt_text(row.secret_key_encrypted), row.is_testnet),
        source="database",
        is_testnet=row.is_testnet,
        row=row,
    )


def update_db_permission_snapshot(db: Session, row: BinanceAPIKey, restrictions: dict) -> BinanceAPIKey:
    row.enable_reading = bool(restrictions.get("enableReading", True))
    row.enable_trading = bool(restrictions.get("enableSpotAndMarginTrading", True))
    row.enable_withdrawals = bool(restrictions.get("enableWithdrawals", False))
    row.enable_internal_transfer = bool(restrictions.get("enableInternalTransfer", False))
    row.ip_restrict = bool(restrictions.get("ipRestrict", False))
    row.status = "unsafe" if row.enable_withdrawals else "connected"
    row.last_checked_at = datetime.utcnow()
    db.add(row)
    db.commit()
    return row

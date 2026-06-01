from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from app.database import Base


class BinanceAPIKey(Base):
    __tablename__ = "binance_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    api_key_encrypted = Column(Text, nullable=False)
    secret_key_encrypted = Column(Text, nullable=False)
    is_testnet = Column(Boolean, default=True, nullable=False)
    enable_reading = Column(Boolean, default=False, nullable=False)
    enable_trading = Column(Boolean, default=False, nullable=False)
    enable_withdrawals = Column(Boolean, default=False, nullable=False)
    enable_internal_transfer = Column(Boolean, default=False, nullable=False)
    ip_restrict = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="unchecked", nullable=False)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from app.database import Base


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    bot_name = Column(String(120), nullable=False)
    symbol = Column(String(30), nullable=False, default="BTCUSDT")
    strategy_type = Column(String(80), nullable=False, default="TREND_BREAKOUT")
    mode = Column(String(80), nullable=False, default="AUTO_AGGRESSIVE")
    status = Column(String(50), nullable=False, default="stopped")
    paper_trading = Column(Boolean, default=True, nullable=False)
    max_usable_percent = Column(Float, default=50.0, nullable=False)
    reserve_percent = Column(Float, default=50.0, nullable=False)
    stop_loss_percent = Column(Float, default=3.0, nullable=False)
    take_profit_percent = Column(Float, default=5.0, nullable=False)
    daily_loss_limit_percent = Column(Float, default=5.0, nullable=False)
    max_trade_per_day = Column(Integer, default=3, nullable=False)
    cooldown_minutes = Column(Integer, default=360, nullable=False)
    max_allowed_volatility_percent_5m = Column(Float, default=3.0, nullable=False)
    emergency_stop = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BotRuntimeState(Base):
    __tablename__ = "bot_runtime_state"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), unique=True, nullable=False, index=True)
    current_position = Column(String(50), default="none", nullable=False)
    entry_price = Column(Float, default=0.0, nullable=False)
    entry_quantity = Column(Float, default=0.0, nullable=False)
    used_capital = Column(Float, default=0.0, nullable=False)
    unrealized_pnl = Column(Float, default=0.0, nullable=False)
    today_pnl = Column(Float, default=0.0, nullable=False)
    today_trade_count = Column(Integer, default=0, nullable=False)
    consecutive_losses = Column(Integer, default=0, nullable=False)
    last_trade_at = Column(DateTime, nullable=True)
    cooldown_until = Column(DateTime, nullable=True)
    safety_lock_status = Column(String(80), default="OK", nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=False, index=True)
    binance_order_id = Column(String(100), nullable=True, index=True)
    symbol = Column(String(30), nullable=False)
    side = Column(String(20), nullable=False)
    order_type = Column(String(30), nullable=False, default="MARKET")
    price = Column(Float, default=0.0, nullable=False)
    quantity = Column(Float, default=0.0, nullable=False)
    quote_order_qty = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default="NEW", nullable=False)
    executed_qty = Column(Float, default=0.0, nullable=False)
    cummulative_quote_qty = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

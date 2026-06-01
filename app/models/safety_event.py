from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.database import Base


class SafetyEvent(Base):
    __tablename__ = "safety_events"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False)
    reason = Column(Text, nullable=False)
    action_taken = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

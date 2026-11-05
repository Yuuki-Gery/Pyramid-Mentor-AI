from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class GrowthRecord(Base):
    """成长记录 - 4.0.4 成长报告的基础数据"""
    __tablename__ = "growth_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    record_type = Column(String(50), nullable=False)  # problem_solved, skill_gained, mindset_change, goal_set
    title = Column(String(200), default="")
    description = Column(Text, default="")
    related_conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
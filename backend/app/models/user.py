from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), default="")

    # Profile
    background = Column(Text, default="")
    skills = Column(Text, default="[]")  # JSON array
    interests = Column(Text, default="[]")
    goal = Column(Text, default="")
    resources = Column(Text, default="[]")

    # Meta
    is_active = Column(Boolean, default=True)
    is_vip = Column(Boolean, default=False)

    # Quota Management
    quota_limit = Column(Integer, default=50)  # 每月可用次数
    quota_used = Column(Integer, default=0)    # 已使用次数
    quota_reset_at = Column(DateTime(timezone=True), nullable=True)  # 额度重置时间
    model_tier = Column(String(20), default="standard")  # standard | premium | unlimited

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def profile_dict(self):
        import json
        return {
            "background": self.background or "",
            "skills": json.loads(self.skills) if self.skills else [],
            "interests": json.loads(self.interests) if self.interests else [],
            "goal": self.goal or "",
            "resources": json.loads(self.resources) if self.resources else [],
        }
"""
成长记忆API
基于Redis的高级成长记忆系统
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.models.user import User
from app.memory.growth_memory import growth_memory
from app.core.config import settings

router = APIRouter(prefix="/api/growth-memory", tags=["成长记忆"])


# ---- Request Models ----

class MilestoneCreate(BaseModel):
    title: str
    description: str
    milestone_type: str = "认知提升"


class GoalCreate(BaseModel):
    goal: str
    context: str = ""
    status: str = "进行中"


class DecisionCreate(BaseModel):
    topic: str
    choice: str
    reason: str
    options: list = []
    outcome: str = "待评估"


# 开发模式：无需认证，使用匿名ID
def get_user_id() -> str:
    """获取用户ID，无认证直接返回匿名ID"""
    return "anonymous_dev_user"


# ---- Milestones ----

@router.get("/milestones")
async def get_milestones():
    """获取成长里程碑"""
    uid = get_user_id()
    milestones = growth_memory.get_milestones(uid)
    return {"milestones": milestones, "total": len(milestones)}


@router.post("/milestones")
async def add_milestone(body: MilestoneCreate):
    """添加成长里程碑"""
    uid = get_user_id()
    import datetime
    milestones = growth_memory.add_milestone(uid, {
        "type": body.milestone_type,
        "title": body.title,
        "description": body.description,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    })
    return {"milestones": milestones, "message": "里程碑已记录"}


# ---- Goals ----

@router.get("/goals")
async def get_goals():
    """获取用户目标"""
    uid = get_user_id()
    goals = growth_memory.get_goals(uid)
    return {"goals": goals, "total": len(goals)}


@router.post("/goals")
async def add_goal(body: GoalCreate):
    """添加新目标"""
    uid = get_user_id()
    import datetime
    goals = growth_memory.add_goal(uid, {
        "goal": body.goal,
        "context": body.context,
        "status": body.status,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    })
    return {"goals": goals, "message": "目标已记录"}


# ---- Decisions ----

@router.get("/decisions")
async def get_decisions():
    """获取决策历史"""
    uid = get_user_id()
    decisions = growth_memory.get_decisions(uid)
    return {"decisions": decisions, "total": len(decisions)}


@router.post("/decisions")
async def add_decision(body: DecisionCreate):
    """记录重大决策"""
    uid = get_user_id()
    import datetime
    decisions = growth_memory.add_decision(uid, {
        "topic": body.topic,
        "options": body.options,
        "choice": body.choice,
        "reason": body.reason,
        "outcome": body.outcome,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    })
    return {"decisions": decisions, "message": "决策已记录"}


# ---- Thinking Pattern ----

@router.get("/thinking-pattern")
async def get_thinking_pattern():
    """获取思维模式档案"""
    uid = get_user_id()
    pattern = growth_memory.get_thinking_pattern(uid)
    return {"pattern": pattern}


# ---- Summary ----

@router.get("/summary")
async def get_growth_summary():
    """获取综合成长报告"""
    uid = get_user_id()
    summary = growth_memory.generate_growth_summary(uid)
    return {"summary": summary}
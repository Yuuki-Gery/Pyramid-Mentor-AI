from typing import Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.growth import GrowthRecord
from app.models.user import User


class GrowthService:
    """成长服务 — 追踪用户的成长轨迹，生成成长报告"""

    async def add_record(
        self,
        user_id: int,
        record_type: str,
        title: str,
        description: str = "",
        conversation_id: Optional[int] = None,
    ) -> GrowthRecord:
        """添加一条成长记录"""
        async with async_session() as db:
            record = GrowthRecord(
                user_id=user_id,
                record_type=record_type,
                title=title,
                description=description,
                related_conversation_id=conversation_id,
            )
            db.add(record)
            await db.commit()
            await db.refresh(record)
            return record

    async def get_records(
        self,
        user_id: int,
        record_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[GrowthRecord]:
        """获取用户的成长记录"""
        async with async_session() as db:
            query = select(GrowthRecord).where(GrowthRecord.user_id == user_id)
            if record_type:
                query = query.where(GrowthRecord.record_type == record_type)
            query = query.order_by(GrowthRecord.created_at.desc())
            query = query.offset(offset).limit(limit)
            result = await db.execute(query)
            return list(result.scalars().all())

    async def generate_report(
        self,
        user_id: int,
        days: int = 30,
    ) -> dict:
        """生成成长报告"""
        async with async_session() as db:
            # 获取用户
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user:
                return {"error": "用户不存在"}

            # 获取指定时间范围内的成长记录
            since = datetime.now(timezone.utc) - timedelta(days=days)
            query = select(GrowthRecord).where(
                GrowthRecord.user_id == user_id,
                GrowthRecord.created_at >= since,
            ).order_by(GrowthRecord.created_at.desc())
            result = await db.execute(query)
            records = list(result.scalars().all())

            # 按类型分类统计
            type_count = {}
            for r in records:
                type_count[r.record_type] = type_count.get(r.record_type, 0) + 1

            # 计算连续活跃天数
            all_dates = set()
            for r in records:
                all_dates.add(r.created_at.date())
            active_days = len(all_dates)

            # 生成报告
            return {
                "user_name": user.display_name or user.username,
                "period_days": days,
                "total_records": len(records),
                "active_days": active_days,
                "type_breakdown": type_count,
                "recent_records": [
                    {
                        "id": r.id,
                        "type": r.record_type,
                        "title": r.title,
                        "description": r.description,
                        "created_at": r.created_at.isoformat() if r.created_at else "",
                    }
                    for r in records[:10]
                ],
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }


# 全局单例
growth_service = GrowthService()
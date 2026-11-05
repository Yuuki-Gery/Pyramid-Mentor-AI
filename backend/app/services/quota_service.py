"""
额度管理服务
控制用户API调用次数、模型分级
"""
from datetime import datetime, timedelta
from sqlalchemy import select, update
from app.database import async_session
from app.models.user import User


class QuotaService:
    """用户额度管理"""

    # 模型分级配置
    MODEL_TIERS = {
        "standard": {
            "name": "标准版",
            "monthly_limit": 50,
            "models": ["agnes-2.0-flash"],
            "features": ["金字塔分析", "SCQA", "MECE", "逻辑树"],
        },
        "premium": {
            "name": "高级版",
            "monthly_limit": 200,
            "models": ["agnes-2.0-flash", "agnes-2.0-plus"],
            "features": ["金字塔分析", "SCQA", "MECE", "逻辑树", "专家系统", "成长追踪"],
        },
        "unlimited": {
            "name": "无限版",
            "monthly_limit": 999999,
            "models": ["agnes-2.0-flash", "agnes-2.0-plus", "gpt-4o"],
            "features": ["全部功能"],
        },
    }

    async def check_quota(self, user_id: int) -> dict:
        """检查用户额度"""
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return {"allowed": False, "reason": "用户不存在"}

            # 检查是否需要重置额度
            now = datetime.utcnow()
            if user.quota_reset_at and now > user.quota_reset_at:
                # 重置额度
                tier_config = self.MODEL_TIERS.get(user.model_tier, self.MODEL_TIERS["standard"])
                await session.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(
                        quota_used=0,
                        quota_reset_at=now + timedelta(days=30),
                    )
                )
                await session.commit()
                user.quota_used = 0

            remaining = (user.quota_limit or 50) - (user.quota_used or 0)

            return {
                "allowed": remaining > 0 or (user.quota_limit or 50) <= 0,
                "remaining": max(0, remaining),
                "limit": user.quota_limit or 50,
                "used": user.quota_used or 0,
                "tier": user.model_tier or "standard",
                "tier_name": self.MODEL_TIERS.get(user.model_tier, self.MODEL_TIERS["standard"])["name"],
            }

    async def consume_quota(self, user_id: int, amount: int = 1) -> bool:
        """消耗用户额度"""
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return False

            current_used = user.quota_used or 0
            limit = user.quota_limit or 50

            # 无限制模式
            if limit <= 0:
                return True

            if current_used + amount > limit:
                return False

            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(quota_used=current_used + amount)
            )
            await session.commit()
            return True

    async def get_available_models(self, user_id: int) -> list:
        """获取用户可用的模型列表"""
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                return self.MODEL_TIERS["standard"]["models"]

            tier = user.model_tier or "standard"
            config = self.MODEL_TIERS.get(tier, self.MODEL_TIERS["standard"])
            return config["models"]


quota_service = QuotaService()
"""
额度管理API
控制用户调用次数和模型分级
"""
from fastapi import APIRouter, Depends

from app.api.auth import get_current_user
from app.models.user import User
from app.services.quota_service import quota_service

router = APIRouter(prefix="/api/quota", tags=["额度管理"])


@router.get("/status")
async def get_quota_status(current_user: User = Depends(get_current_user)):
    """获取当前用户的额度状态"""
    status = await quota_service.check_quota(current_user.id)
    return status


@router.get("/models")
async def get_available_models(current_user: User = Depends(get_current_user)):
    """获取当前用户可用的模型列表"""
    models = await quota_service.get_available_models(current_user.id)
    return {"models": models}


@router.post("/consume")
async def consume_quota(
    amount: int = 1,
    current_user: User = Depends(get_current_user),
):
    """消耗额度"""
    success = await quota_service.consume_quota(current_user.id, amount)
    if not success:
        return {"success": False, "message": "额度不足，请升级套餐"}
    status = await quota_service.check_quota(current_user.id)
    return {
        "success": True,
        "message": "额度已消耗",
        "remaining": status["remaining"],
    }
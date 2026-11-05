from fastapi import APIRouter, Depends, HTTPException
from app.services.growth_service import growth_service
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/growth", tags=["成长报告"])


@router.get("/records")
async def get_growth_records(
    record_type: str = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
):
    """获取用户的成长记录"""
    records = await growth_service.get_records(
        user_id=current_user.id,
        record_type=record_type,
        limit=limit,
        offset=offset,
    )
    return {
        "records": [
            {
                "id": r.id,
                "type": r.record_type,
                "title": r.title,
                "description": r.description,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in records
        ],
        "total": len(records),
    }


@router.get("/report")
async def generate_growth_report(
    days: int = 30,
    current_user: User = Depends(get_current_user),
):
    """生成成长报告"""
    report = await growth_service.generate_report(
        user_id=current_user.id,
        days=days,
    )
    return report


@router.post("/record")
async def add_growth_record(
    record_type: str,
    title: str,
    description: str = "",
    current_user: User = Depends(get_current_user),
):
    """手动添加一条成长记录"""
    record = await growth_service.add_record(
        user_id=current_user.id,
        record_type=record_type,
        title=title,
        description=description,
    )
    return {
        "id": record.id,
        "type": record.record_type,
        "title": record.title,
        "message": "成长记录已添加",
    }
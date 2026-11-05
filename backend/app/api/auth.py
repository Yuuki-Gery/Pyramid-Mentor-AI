from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse, ProfileUpdate
from app.services import auth_service
from app.services.auth_service import (
    create_user, authenticate_user, get_user_by_id,
    create_access_token, decode_access_token, user_to_response
)
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT 令牌验证，返回当前用户"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    try:
        parsed_user_id = int(user_id) if user_id is not None else None
    except (TypeError, ValueError):
        parsed_user_id = None
    if parsed_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_id(db, parsed_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用",
        )
    return user


@router.post("/register", response_model=Token)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    existing = await auth_service.get_user_by_username(db, data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用",
        )

    existing_email = await auth_service.get_user_by_email(db, data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )

    user = await create_user(db, data.username, data.email, data.password, data.display_name)
    token = create_access_token({"sub": str(user.id)})

    return Token(
        access_token=token,
        user=UserResponse(**user_to_response(user)),
    )


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    user = await authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.id)})

    return Token(
        access_token=token,
        user=UserResponse(**user_to_response(user)),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(**user_to_response(current_user))


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户画像（背景、技能、兴趣、目标、资源）"""
    import json

    if data.display_name is not None:
        current_user.display_name = data.display_name
    if data.background is not None:
        current_user.background = data.background
    if data.skills is not None:
        current_user.skills = json.dumps(data.skills, ensure_ascii=False)
    if data.interests is not None:
        current_user.interests = json.dumps(data.interests, ensure_ascii=False)
    if data.goal is not None:
        current_user.goal = data.goal
    if data.resources is not None:
        current_user.resources = json.dumps(data.resources, ensure_ascii=False)

    await db.commit()
    await db.refresh(current_user)

    return UserResponse(**user_to_response(current_user))

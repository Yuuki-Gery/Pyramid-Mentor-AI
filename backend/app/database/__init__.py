from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# 使用 SQLite 作为开发环境数据库（方便），生产环境可切换 PostgreSQL
DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """创建所有表"""
    async with engine.begin() as conn:
        from app.models.user import User
        from app.models.conversation import Conversation
        from app.models.growth import GrowthRecord
        await conn.run_sync(Base.metadata.create_all)
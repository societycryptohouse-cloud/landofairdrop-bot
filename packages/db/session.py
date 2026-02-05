from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from packages.common.config import settings


engine = create_async_engine(settings.database_url, future=True, echo=False)
async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

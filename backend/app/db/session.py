from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def create_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(settings.database_url, pool_pre_ping=True)


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("数据库引擎尚未初始化")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("数据库会话工厂尚未初始化")
    return _session_factory


def set_engine(engine: AsyncEngine | None) -> None:
    global _engine, _session_factory
    _engine = engine
    _session_factory = (
        async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        if engine is not None
        else None
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：提供请求级数据库会话。"""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def dispose_engine() -> None:
    if _engine is not None:
        await _engine.dispose()

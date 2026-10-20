from __future__ import annotations

from redis.asyncio import Redis, from_url

from app.core.config import Settings

_client: Redis | None = None


def create_redis_client(settings: Settings) -> Redis:
    """创建全局 Redis 客户端（redis-py 5.x 原生支持 async）。"""
    return from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        health_check_interval=30,
    )


def get_redis() -> Redis:
    if _client is None:
        raise RuntimeError("Redis 客户端尚未初始化")
    return _client


def set_redis_client(client: Redis | None) -> None:
    global _client
    _client = client


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None

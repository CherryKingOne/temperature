from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import UnauthorizedError
from app.core.redis_client import get_redis
from app.core.security import decode_token
from app.db.models.admin import AdminStatus, AdminUser
from app.db.session import get_db
from app.services.admin.auth_service import REVOKED_KEY, AuthService
from app.services.admin.verification_service import VerificationCodeService
from app.services.email_service import EmailService

bearer_scheme = HTTPBearer(auto_error=False, description="管理端访问令牌")


def get_redis_dep() -> Redis:
    return get_redis()


def get_settings_dep() -> Settings:
    return get_settings()


def get_email_service(
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> EmailService:
    return EmailService(settings)


def get_verification_service(
    redis: Annotated[Redis, Depends(get_redis_dep)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> VerificationCodeService:
    return VerificationCodeService(redis, settings, email_service)


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis_dep)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
    verification_service: Annotated[
        VerificationCodeService, Depends(get_verification_service)
    ],
) -> AuthService:
    return AuthService(
        session=session,
        redis=redis,
        settings=settings,
        verification_service=verification_service,
    )


async def get_access_claims(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> dict:
    """解析并校验访问令牌，返回其声明。"""
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("未登录，请先获取访问令牌")
    return decode_token(settings, credentials.credentials, "access")


async def get_lenient_access_claims(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> dict | None:
    """解析访问令牌：请求头缺失时抛出 401，令牌已失效（过期/被吊销）时返回 None。"""
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("未登录，请先获取访问令牌")
    try:
        return decode_token(settings, credentials.credentials, "access")
    except UnauthorizedError:
        return None


async def get_current_admin(
    access_claims: Annotated[dict, Depends(get_access_claims)],
    session: Annotated[AsyncSession, Depends(get_db)],
    redis: Annotated[Redis, Depends(get_redis_dep)],
) -> AdminUser:
    """解析访问令牌并返回当前管理员；令牌无效/被吊销/账号不可用时抛出 401。"""
    claims = access_claims
    jti = str(claims.get("jti", ""))
    session_id = claims.get("sid")

    revoked = await redis.exists(REVOKED_KEY.format(jti=jti))
    if not revoked and session_id:
        revoked = await redis.exists(REVOKED_KEY.format(jti=session_id))
    if revoked:
        raise UnauthorizedError("访问令牌已失效，请重新登录")

    admin = await session.scalar(select(AdminUser).where(AdminUser.id == int(claims["sub"])))
    if admin is None:
        raise UnauthorizedError("管理员不存在")
    if admin.status != AdminStatus.ACTIVE:
        raise UnauthorizedError("账号不可用")
    return admin

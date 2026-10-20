from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import bcrypt
import jwt

from app.core.config import Settings
from app.core.errors import InvalidRefreshTokenError, UnauthorizedError
from app.core.snowflake import next_id

JWT_ALGORITHM = "HS256"
BCRYPT_ROUNDS = 12
MAX_PASSWORD_BYTES = 72

TokenType = Literal["access", "refresh"]


def hash_password(password: str) -> str:
    """使用 bcrypt(cost=12) 对明文密码做单向哈希。"""
    raw = password.encode("utf-8")
    if len(raw) > MAX_PASSWORD_BYTES:
        raise ValueError("password exceeds 72 bytes")
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """校验明文密码与 bcrypt 哈希是否匹配。"""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def generate_email_code(length: int = 6) -> str:
    """生成纯数字邮箱验证码，使用密码学安全随机源。"""
    return "".join(secrets.choice(string.digits) for _ in range(length))


def _encode_token(
    settings: Settings,
    *,
    subject: str,
    token_type: TokenType,
    expires_seconds: int,
    session_id: str | None = None,
    role: str | None = None,
) -> tuple[str, str, datetime]:
    """返回 (token, jti, 过期时间)。"""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=expires_seconds)
    jti = str(next_id())
    payload: dict[str, Any] = {
        "sub": subject,
        "jti": jti,
        "typ": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    if session_id is not None:
        payload["sid"] = session_id
    if role is not None:
        payload["role"] = role
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
    return token, jti, expires_at


def create_access_token(
    settings: Settings,
    *,
    admin_id: int,
    role: str,
    session_id: str,
) -> tuple[str, str, datetime]:
    return _encode_token(
        settings,
        subject=str(admin_id),
        token_type="access",
        expires_seconds=settings.access_token_expire_seconds,
        session_id=session_id,
        role=role,
    )


def create_refresh_token(
    settings: Settings,
    *,
    admin_id: int,
    role: str,
) -> tuple[str, str, datetime]:
    return _encode_token(
        settings,
        subject=str(admin_id),
        token_type="refresh",
        expires_seconds=settings.refresh_token_expire_seconds,
        role=role,
    )


def decode_token(settings: Settings, token: str, expected_type: TokenType) -> dict[str, Any]:
    """解析并校验 JWT；令牌类型不匹配或签名/有效期异常时抛出业务异常。"""
    error_cls = InvalidRefreshTokenError if expected_type == "refresh" else UnauthorizedError
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise error_cls("令牌已过期") from exc
    except jwt.PyJWTError as exc:
        raise error_cls("令牌无效") from exc

    if payload.get("typ") != expected_type:
        raise error_cls("令牌无效")
    return payload

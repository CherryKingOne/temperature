from __future__ import annotations

import logging

from redis.asyncio import Redis

from app.core.config import Settings
from app.core.errors import BusinessError, TooManyRequestsError
from app.core.security import generate_email_code
from app.schemas.admin.auth import EmailCodeScene
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

EMAIL_IP_LIMIT = 30
EMAIL_IP_LIMIT_WINDOW_SECONDS = 600

CODE_KEY_TEMPLATE = "admin:auth:email-code:{scene}:{email}"
RESEND_KEY_TEMPLATE = "admin:auth:email-code:resend:{scene}:{email}"
IP_KEY_TEMPLATE = "admin:auth:email-code:ip:{ip}"
ATTEMPT_KEY_TEMPLATE = "admin:auth:email-code:attempt:{scene}:{email}"


class VerificationCodeService:
    """基于 Redis 的邮箱验证码服务（验证码不落数据库）。"""

    def __init__(self, redis: Redis, settings: Settings, email_service: EmailService) -> None:
        self._redis = redis
        self._settings = settings
        self._email_service = email_service

    async def send_code(self, email: str, scene: EmailCodeScene, client_ip: str) -> int:
        """发送验证码，返回验证码有效期（秒）。"""
        email = email.strip().lower()
        scene_value = scene.value if isinstance(scene, EmailCodeScene) else str(scene)

        await self._check_ip_limit(client_ip)

        code_key = CODE_KEY_TEMPLATE.format(scene=scene_value, email=email)
        resend_key = RESEND_KEY_TEMPLATE.format(scene=scene_value, email=email)
        # 已有有效验证码时需要等待冷却时间；验证码已过期或被消费则可立即重新获取
        if await self._redis.exists(code_key):
            ttl = await self._redis.ttl(resend_key)
            if ttl is not None and ttl > 0:
                raise TooManyRequestsError(f"验证码发送过于频繁，请 {ttl} 秒后再试")

        code = generate_email_code()
        await self._email_service.send_verification_code(email, code, scene_value)

        pipe = self._redis.pipeline(transaction=False)
        pipe.set(
            CODE_KEY_TEMPLATE.format(scene=scene_value, email=email),
            code,
            ex=self._settings.email_code_expire_seconds,
        )
        pipe.set(resend_key, "1", ex=self._settings.email_code_resend_seconds)
        pipe.delete(ATTEMPT_KEY_TEMPLATE.format(scene=scene_value, email=email))
        await pipe.execute()
        return self._settings.email_code_expire_seconds

    async def verify_code(self, email: str, scene: EmailCodeScene, code: str) -> None:
        """校验验证码，失败抛出 422 业务异常。"""
        email = email.strip().lower()
        scene_value = scene.value if isinstance(scene, EmailCodeScene) else str(scene)
        key = CODE_KEY_TEMPLATE.format(scene=scene_value, email=email)
        attempt_key = ATTEMPT_KEY_TEMPLATE.format(scene=scene_value, email=email)

        stored = await self._redis.get(key)
        if stored is None:
            raise BusinessError("验证码错误或已过期")

        if not secrets_compare(stored, code.strip()):
            attempts = await self._redis.incr(attempt_key)
            if attempts == 1:
                await self._redis.expire(attempt_key, self._settings.email_code_expire_seconds)
            if attempts >= self._settings.email_code_max_attempts:
                await self._redis.delete(key)
                await self._redis.delete(attempt_key)
                raise BusinessError("验证码错误次数过多，请重新获取验证码")
            raise BusinessError("验证码错误或已过期")

        pipe = self._redis.pipeline(transaction=False)
        pipe.delete(key)
        pipe.delete(attempt_key)
        await pipe.execute()

    async def _check_ip_limit(self, client_ip: str) -> None:
        if not client_ip:
            return
        key = IP_KEY_TEMPLATE.format(ip=client_ip)
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, EMAIL_IP_LIMIT_WINDOW_SECONDS)
        if count > EMAIL_IP_LIMIT:
            raise TooManyRequestsError("验证码发送过于频繁，请稍后再试")


def secrets_compare(left: str, right: str) -> bool:
    """常量时间比较，避免时序侧信道。"""
    import hmac

    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))

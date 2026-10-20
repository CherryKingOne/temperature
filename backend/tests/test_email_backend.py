"""邮件投递后端测试：console 后端把验证码写到 Redis 并打印到标准输出，不经过 SMTP。"""

from __future__ import annotations

from app.core.config import Settings
from app.core.snowflake import next_id
from app.schemas.admin.auth import EmailCodeScene
from app.services.admin.verification_service import VerificationCodeService
from app.services.email_service import EmailService


def console_settings(settings: Settings) -> Settings:
    return settings.model_copy(update={"email_backend": "console"})


def build_service(redis, settings: Settings) -> VerificationCodeService:
    console = console_settings(settings)
    return VerificationCodeService(
        redis=redis,
        settings=console,
        email_service=EmailService(console),
    )


async def test_console_backend_writes_code_to_redis(redis, settings, capsys):
    email = f"console-{next_id()}@example.com"
    service = build_service(redis, settings)

    expire = await service.send_code(email, EmailCodeScene.REGISTER, "127.0.0.1")

    assert expire == settings.email_code_expire_seconds
    code = await redis.get(f"admin:auth:email-code:register:{email}")
    assert code is not None
    assert len(code) == 6

    printed = capsys.readouterr().out
    assert code in printed
    assert email in printed


async def test_console_backend_code_can_be_verified(redis, settings, capsys):
    email = f"console-{next_id()}@example.com"
    service = build_service(redis, settings)

    await service.send_code(email, EmailCodeScene.REGISTER, "127.0.0.1")
    code = await redis.get(f"admin:auth:email-code:register:{email}")
    assert code is not None
    capsys.readouterr()

    await service.verify_code(email, EmailCodeScene.REGISTER, code)

    assert await redis.get(f"admin:auth:email-code:register:{email}") is None

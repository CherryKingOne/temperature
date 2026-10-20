from __future__ import annotations

import logging
import sys
from email.message import EmailMessage

import aiosmtplib

from app.core.config import Settings
from app.core.errors import ServiceUnavailableError

logger = logging.getLogger(__name__)

FROM_NAME = "Temperature Platform"
EMAIL_CODE_LENGTH = 6
SMTP_TIMEOUT_SECONDS = 10

SCENE_SUBJECTS = {
    "register": "管理员注册验证码",
    "reset_password": "重置密码验证码",
}


class EmailService:
    """验证码投递服务。

    - ``smtp`` 后端：经真实 SMTP 服务器把验证码邮件发出去；
    - ``console`` 后端：验证码只打印到服务标准输出（本地开发用，不需要任何邮件容器）。

    两种后端都不改变验证码本身的生成与校验逻辑：验证码依旧真实写入 Redis，
    ``console`` 只是把"投递"这一步从 SMTP 换成了终端输出。
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def is_console(self) -> bool:
        return self._settings.email_backend == "console"

    @property
    def is_configured(self) -> bool:
        if self.is_console:
            return True
        return bool(self._settings.smtp_host and self._settings.smtp_from_email)

    async def send_verification_code(self, email: str, code: str, scene: str) -> None:
        """发送验证码邮件。SMTP 未配置或发送失败时抛出 503 业务异常。"""
        if not self.is_configured:
            raise ServiceUnavailableError("邮件服务未配置，无法发送验证码")

        subject = SCENE_SUBJECTS.get(scene, "平台验证码")
        if self.is_console:
            self._print_to_console(email, code, subject)
            return

        message = EmailMessage()
        message["Subject"] = f"【{FROM_NAME}】{subject}"
        message["From"] = f"{FROM_NAME} <{self._settings.smtp_from_email}>"
        message["To"] = email
        message.set_content(
            f"您的验证码是：{code}\n\n"
            f"验证码 {self._settings.email_code_expire_seconds // 60} 分钟内有效，"
            f"请勿转发给他人。如非本人操作请忽略本邮件。\n"
        )
        message.add_alternative(
            f"<p>您的验证码是：<strong style='font-size:20px'>{code}</strong></p>"
            f"<p>验证码 {self._settings.email_code_expire_seconds // 60} 分钟内有效，请勿转发给他人。</p>",
            subtype="html",
        )

        try:
            await aiosmtplib.send(
                message,
                hostname=self._settings.smtp_host,
                port=self._settings.smtp_port,
                username=self._settings.smtp_username or None,
                password=self._settings.smtp_password or None,
                use_tls=self._settings.smtp_use_ssl,
                # start_tls=None：由 aiosmtplib 按服务端能力自动协商
                timeout=SMTP_TIMEOUT_SECONDS,
                # 显式指定 EHLO 主机名，避免触发反向 DNS 查询导致发送延迟
                local_hostname="localhost",
            )
        except aiosmtplib.SMTPException as exc:
            logger.exception("SMTP 发送验证码失败")
            raise ServiceUnavailableError("邮件服务不可用，请稍后再试") from exc
        except OSError as exc:
            logger.exception("SMTP 连接失败")
            raise ServiceUnavailableError("邮件服务不可用，请稍后再试") from exc

    def _print_to_console(self, email: str, code: str, subject: str) -> None:
        """把验证码打印到标准输出（EMAIL_BACKEND=console）。"""
        minutes = self._settings.email_code_expire_seconds // 60
        separator = "=" * 60
        text = (
            f"\n{separator}\n"
            f"【console 邮件】{subject}\n"
            f"收件人：{email}\n"
            f"验证码：{code}\n"
            f"有效期：{minutes} 分钟\n"
            f"（EMAIL_BACKEND=console：邮件未真实发送，仅打印到服务输出）\n"
            f"{separator}\n"
        )
        _write_stdout(text)


def _write_stdout(text: str) -> None:
    """写标准输出；终端编码装不下中文时直接写 UTF-8 字节，避免乱码或报错。"""
    stream = sys.stdout
    try:
        stream.write(text)
        stream.flush()
    except UnicodeEncodeError:
        buffer = getattr(stream, "buffer", None)
        if buffer is None:
            raise
        buffer.write(text.encode("utf-8", errors="replace"))
        buffer.flush()

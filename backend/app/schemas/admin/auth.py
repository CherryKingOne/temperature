from __future__ import annotations

import enum
import re
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.core.security import MAX_PASSWORD_BYTES


class EmailCodeScene(str, enum.Enum):
    """邮箱验证码用途。"""

    REGISTER = "register"
    RESET_PASSWORD = "reset_password"


def _validate_password_bytes(value: str) -> str:
    if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(f"密码长度不能超过 {MAX_PASSWORD_BYTES} 字节")
    return value


def _normalize_phone(value: str | None) -> str | None:
    """规范化手机号：去掉空格与分隔符；空值统一为 None。"""
    if value is None:
        return None
    cleaned = re.sub(r"[\s\-()]", "", value).strip()
    return cleaned or None


class SendEmailCodeRequest(BaseModel):
    """发送邮箱验证码。"""

    email: EmailStr
    scene: EmailCodeScene

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class SendEmailCodeResponse(BaseModel):
    email: str
    scene: str
    expires_in: int
    sent: bool


class RegisterRequest(BaseModel):
    """管理员注册。"""

    name: str = Field(min_length=2, max_length=50, description="姓名")
    email: EmailStr = Field(description="邮箱")
    phone: str = Field(default="", max_length=20, description="手机号（可空）")
    code: str = Field(description="邮箱验证码（纯数字）")
    password: str = Field(min_length=8, description="密码")
    password_confirm: str = Field(min_length=8, description="确认密码")

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("phone")
    @classmethod
    def _normalize_phone_field(cls, value: str) -> str:
        return _normalize_phone(value) or ""

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("code")
    @classmethod
    def _digits_only(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("验证码必须为纯数字")
        return value

    @field_validator("password", "password_confirm")
    @classmethod
    def _check_password_length(cls, value: str) -> str:
        return _validate_password_bytes(value)

    @model_validator(mode="after")
    def _passwords_match(self) -> "RegisterRequest":
        if self.password != self.password_confirm:
            raise ValueError("两次输入的密码不一致")
        return self


class LoginRequest(BaseModel):
    """管理员登录。"""

    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def _check_password_length(cls, value: str) -> str:
        return _validate_password_bytes(value)


class RefreshTokenRequest(BaseModel):
    """刷新访问令牌。"""

    refresh_token: str = Field(min_length=1)


class ChangePasswordRequest(BaseModel):
    """修改自身密码。"""

    code: str = Field(description="邮箱验证码（纯数字，scene=reset_password）")
    old_password: str = Field(min_length=1)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @field_validator("code")
    @classmethod
    def _digits_only(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("验证码必须为纯数字")
        return value

    @field_validator("old_password", "password", "password_confirm")
    @classmethod
    def _check_password_length(cls, value: str) -> str:
        return _validate_password_bytes(value)

    @model_validator(mode="after")
    def _passwords_match(self) -> "ChangePasswordRequest":
        if self.password != self.password_confirm:
            raise ValueError("两次输入的密码不一致")
        return self


class ResetPasswordRequest(BaseModel):
    """通过邮箱验证码重置密码。"""

    email: EmailStr
    code: str = Field(min_length=1)
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("code")
    @classmethod
    def _digits_only(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("验证码必须为纯数字")
        return value

    @field_validator("password", "password_confirm")
    @classmethod
    def _check_password_length(cls, value: str) -> str:
        return _validate_password_bytes(value)

    @model_validator(mode="after")
    def _passwords_match(self) -> "ResetPasswordRequest":
        if self.password != self.password_confirm:
            raise ValueError("两次输入的密码不一致")
        return self


class UpdateProfileRequest(BaseModel):
    """修改自身资料（姓名、手机号）。"""

    name: str = Field(min_length=2, max_length=50, description="姓名")
    phone: str = Field(default="", max_length=20, description="手机号（可空）")

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("phone")
    @classmethod
    def _normalize_phone_field(cls, value: str) -> str:
        return _normalize_phone(value) or ""


class AdminUserOut(BaseModel):
    """管理员信息（对外输出）。"""

    model_config = ConfigDict(from_attributes=True)

    # 雪花 ID 超出 JavaScript 安全整数范围，统一以字符串返回避免精度丢失
    id: str
    name: str
    email: str
    phone: str | None = None
    role: str
    is_super_admin: bool
    status: str
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", "last_login_at", mode="after")
    @classmethod
    def _to_utc(cls, value: datetime | None) -> datetime | None:
        """数据库 TIMESTAMP 不带时区，统一按 UTC 解释并附加时区信息。"""
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class TokenPairOut(BaseModel):
    """令牌对。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class LoginResponse(TokenPairOut):
    """登录响应。"""

    admin: AdminUserOut


class RefreshTokenResponse(TokenPairOut):
    """刷新令牌响应。"""

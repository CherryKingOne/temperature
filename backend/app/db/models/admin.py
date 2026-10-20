from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import BigInteger, Enum, Index, String
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class AdminRole(str, enum.Enum):
    """管理员角色。系统中第一个注册的账号为超级管理员。"""

    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"


class AdminStatus(str, enum.Enum):
    """账号状态。"""

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class AdminUser(Base, TimestampMixin):
    """管理端账号表。"""

    __tablename__ = "admin_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="姓名")
    email: Mapped[str] = mapped_column(String(254), nullable=False, comment="登录邮箱")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="bcrypt 密码哈希")
    role: Mapped[AdminRole] = mapped_column(
        Enum(
            AdminRole,
            native_enum=True,
            length=20,
            values_callable=lambda members: [member.value for member in members],
        ),
        nullable=False,
        default=AdminRole.ADMIN,
        server_default=AdminRole.ADMIN.value,
        comment="角色",
    )
    status: Mapped[AdminStatus] = mapped_column(
        Enum(
            AdminStatus,
            native_enum=True,
            length=20,
            values_callable=lambda members: [member.value for member in members],
        ),
        nullable=False,
        default=AdminStatus.ACTIVE,
        server_default=AdminStatus.ACTIVE.value,
        comment="账号状态",
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        mysql.DATETIME(fsp=6), nullable=True, comment="最近登录时间"
    )
    last_login_ip: Mapped[str | None] = mapped_column(
        String(45), nullable=True, comment="最近登录 IP"
    )

    __table_args__ = (
        Index("uq_admin_user_email", "email", unique=True),
        Index("ix_admin_user_role", "role"),
        Index("ix_admin_user_status", "status"),
    )

    @property
    def is_super_admin(self) -> bool:
        return self.role == AdminRole.SUPER_ADMIN

    def __repr__(self) -> str:  # pragma: no cover - 调试辅助
        return f"<AdminUser id={self.id} email={self.email!r} role={self.role}>"

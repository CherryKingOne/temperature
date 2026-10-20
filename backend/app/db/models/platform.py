from __future__ import annotations

from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

BOOTSTRAP_LOCK_ROW_ID = 1
BOOTSTRAP_LOCK_ROW_NAME = "admin_bootstrap_lock"


class PlatformInvariant(Base, TimestampMixin):
    """平台级不变式表。

    表中固定存在 id = 1 的单行，注册流程对该行加 ``SELECT ... FOR UPDATE`` 行锁，
    从而把「首位注册者成为超级管理员」的判定串行化，保证并发注册下有且仅有一位超级管理员。
    """

    __tablename__ = "platform_invariant"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    def __repr__(self) -> str:  # pragma: no cover - 调试辅助
        return f"<PlatformInvariant id={self.id} name={self.name!r}>"

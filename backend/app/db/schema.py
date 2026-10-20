from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

# 建表语句（幂等，重复执行安全）
SCHEMA_SQL = """
-- 平台级不变式表：首位注册者判定依赖对 id=1 行的行锁
CREATE TABLE IF NOT EXISTS `platform_invariant` (
    `id`         SMALLINT    NOT NULL,
    `name`       VARCHAR(64) NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_platform_invariant_name` (`name`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

INSERT IGNORE INTO `platform_invariant` (`id`, `name`, `created_at`, `updated_at`)
VALUES (1, 'admin_bootstrap_lock', NOW(6), NOW(6));

-- 管理端账号表
CREATE TABLE IF NOT EXISTS `admin_user` (
    `id`            BIGINT       NOT NULL COMMENT '雪花 ID',
    `name`          VARCHAR(50)  NOT NULL COMMENT '姓名',
    `email`         VARCHAR(254) NOT NULL COMMENT '登录邮箱',
    `password_hash` VARCHAR(255) NOT NULL COMMENT 'bcrypt 密码哈希',
    `role`          ENUM ('SUPER_ADMIN', 'ADMIN')   NOT NULL DEFAULT 'ADMIN' COMMENT '角色',
    `status`        ENUM ('ACTIVE', 'DISABLED')    NOT NULL DEFAULT 'ACTIVE' COMMENT '账号状态',
    `last_login_at` DATETIME(6)  NULL COMMENT '最近登录时间',
    `last_login_ip` VARCHAR(45)  NULL COMMENT '最近登录 IP',
    `created_at`    DATETIME(6)  NOT NULL,
    `updated_at`    DATETIME(6)  NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_admin_user_email` (`email`),
    KEY `ix_admin_user_role` (`role`),
    KEY `ix_admin_user_status` (`status`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
"""


def load_statements() -> list[str]:
    """把建表语句拆成可逐条执行的 SQL。"""
    lines = [line for line in SCHEMA_SQL.splitlines() if not line.strip().startswith("--")]
    body = "\n".join(lines)
    return [statement.strip() for statement in body.split(";") if statement.strip()]


async def init_schema(conn: AsyncConnection) -> None:
    """在给定连接上建表（幂等，应用启动时调用）。"""
    for statement in load_statements():
        await conn.execute(text(statement))

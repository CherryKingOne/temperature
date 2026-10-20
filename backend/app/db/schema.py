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
    `phone`         VARCHAR(20)  NULL COMMENT '手机号',
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

# 增量迁移：为已建库补齐后加的字段（执行前先检查列是否存在）
MIGRATION_SQL = """
ALTER TABLE `admin_user` ADD COLUMN `phone` VARCHAR(20) NULL COMMENT '手机号' AFTER `email`;
"""

MIGRATION_COLUMNS = {
    "admin_user": {"phone"},
}


def load_statements() -> list[str]:
    """把建表语句拆成可逐条执行的 SQL。"""
    lines = [line for line in SCHEMA_SQL.splitlines() if not line.strip().startswith("--")]
    body = "\n".join(lines)
    return [statement.strip() for statement in body.split(";") if statement.strip()]


async def _column_exists(conn: AsyncConnection, table: str, column: str) -> bool:
    """查询列是否已存在。"""
    result = await conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table AND COLUMN_NAME = :column"
        ),
        {"table": table, "column": column},
    )
    return int(result.scalar_one()) > 0


async def init_schema(conn: AsyncConnection) -> None:
    """在给定连接上建表（幂等，应用启动时调用）。"""
    for statement in load_statements():
        await conn.execute(text(statement))
    await run_migrations(conn)


async def run_migrations(conn: AsyncConnection) -> None:
    """执行增量迁移：只补齐缺失的字段，已存在的库不会被破坏。"""
    for table, columns in MIGRATION_COLUMNS.items():
        for column in columns:
            if await _column_exists(conn, table, column):
                continue
            for statement in load_migrations(table, column):
                await conn.execute(text(statement))


def load_migrations(table: str, column: str) -> list[str]:
    """取出与指定表 / 字段相关的迁移语句。"""
    statements = []
    for statement in MIGRATION_SQL.split(";"):
        cleaned = statement.strip()
        if not cleaned:
            continue
        if f"`{table}`" in cleaned and f"`{column}`" in cleaned:
            statements.append(cleaned)
    return statements

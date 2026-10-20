"""测试夹具：使用真实的 MySQL、Redis 与本地 SMTP 服务器，不使用任何模拟数据。"""

from __future__ import annotations

import os
import sys
from collections.abc import AsyncIterator
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# 必须在导入应用模块之前设置环境变量（应用在导入时读取配置）
os.environ.setdefault("JWT_SECRET_KEY", "integration-test-secret-key-0123456789")
os.environ.setdefault("MYSQL_HOST", "127.0.0.1")
os.environ.setdefault("MYSQL_PORT", "3306")
os.environ.setdefault("MYSQL_USER", "root")
os.environ.setdefault("MYSQL_PASSWORD", "root")
os.environ.setdefault("MYSQL_DATABASE", "temperature_test")
os.environ.setdefault("REDIS_HOST", "127.0.0.1")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_DB", "15")
os.environ.setdefault("REDIS_PASSWORD", "")
os.environ.setdefault("SMTP_HOST", "127.0.0.1")
os.environ.setdefault("SMTP_PORT", "12525")
os.environ.setdefault("SMTP_USE_SSL", "false")
os.environ.setdefault("SMTP_FROM_EMAIL", "noreply@temperature.test")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from asgi_lifespan import LifespanManager  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from redis.asyncio import Redis  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.engine import URL  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.db.schema import init_schema  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_NAME = os.environ["MYSQL_DATABASE"]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def settings():
    return get_settings()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def smtp_server() -> AsyncIterator[None]:
    """启动一个真实的本地 SMTP 服务器用于接收验证码邮件。"""
    from aiosmtpd.controller import Controller

    class Handler:
        def __init__(self) -> None:
            self.messages: list[dict] = []

        async def handle_DATA(self, server, session, envelope):  # noqa: N802
            self.messages.append(
                {
                    "from": envelope.mail_from,
                    "to": list(envelope.rcpt_tos),
                    "content": envelope.content.decode("utf-8", errors="ignore"),
                }
            )
            return "250 Message accepted for delivery"

    handler = Handler()
    controller = Controller(
        handler,
        hostname="127.0.0.1",
        port=int(os.environ["SMTP_PORT"]),
        # 固定 banner 主机名，避免反向 DNS 查询拖慢用例
        server_hostname="localhost",
    )
    controller.start()
    try:
        yield
    finally:
        controller.stop()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine(settings):
    """测试库引擎，并按内置建表 SQL 建表。"""
    # 重建测试库，保证每次运行的表结构是干净的
    admin_engine = create_async_engine(
        URL.create(
            "mysql+asyncmy",
            username=settings.mysql_user,
            password=settings.mysql_password,
            host=settings.mysql_host,
            port=settings.mysql_port,
            database="mysql",
            query={"charset": "utf8mb4"},
        ),
        isolation_level="AUTOCOMMIT",
    )
    async with admin_engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS `{TEST_DATABASE_NAME}`"))
        await conn.execute(
            text(
                f"CREATE DATABASE `{TEST_DATABASE_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
    await admin_engine.dispose()

    test_engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    async with test_engine.begin() as conn:
        await init_schema(conn)
    try:
        yield test_engine
    finally:
        await test_engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def redis_client(settings) -> AsyncIterator[Redis]:
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    await client.ping()
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture(autouse=True)
async def clean_state(engine, redis_client) -> AsyncIterator[None]:
    """每个用例前清空管理员表与相关 Redis 键，保证用例之间互相独立。"""
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE admin_user"))
    keys = await redis_client.keys("admin:auth:*")
    if keys:
        await redis_client.delete(*keys)
    yield


@pytest.fixture
async def client(engine, redis_client, smtp_server) -> AsyncIterator[AsyncClient]:
    """带生命周期管理的测试客户端。"""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
            yield http_client


@pytest.fixture
async def redis(redis_client) -> Redis:
    return redis_client


@pytest.fixture
async def email_code(redis_client) -> "callable":
    """从 Redis 中读取真实的验证码（与发信服务写入的是同一份数据）。"""

    async def _get(email: str, scene: str = "register") -> str:
        key = f"admin:auth:email-code:{scene}:{email.lower()}"
        code = await redis_client.get(key)
        assert code is not None, f"Redis 中不存在验证码键 {key}"
        return code

    return _get

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.admin.auth import admin_auth_router
from app.core.config import get_settings
from app.core.context import request_id_var
from app.core.errors import AppError, InternalError, ValidationError
from app.core.redis_client import close_redis, create_redis_client, set_redis_client
from app.core.snowflake import next_id
from app.db.schema import init_schema
from app.db.session import create_engine, dispose_engine, set_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_engine(settings)
    set_engine(engine)
    redis = create_redis_client(settings)
    set_redis_client(redis)
    async with engine.begin() as conn:
        await init_schema(conn)
    logger.info("应用启动完成")
    try:
        yield
    finally:
        await close_redis()
        await dispose_engine()
        logger.info("应用已关闭")


app = FastAPI(
    title="Temperature Backend",
    version="0.1.0",
    description="Temperature 平台后端服务（管理端接口以 /api/admin 为前缀）",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(next_id())
    request.state.request_id = request_id
    token = request_id_var.set(request_id)
    started = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - started) * 1000:.2f}"
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return exc.to_response(request)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return ValidationError(detail=jsonable_encoder(exc.errors())).to_response(request)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code * 100,
            "message": str(exc.detail),
            "data": None,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("未捕获异常 path=%s", request.url.path)
    return InternalError().to_response(request)


app.include_router(admin_auth_router, prefix=f"{settings.api_prefix}/admin")


@app.get("/health", tags=["system"], summary="健康检查")
async def health() -> dict:
    """检查 MySQL 与 Redis 连通性。"""
    from app.core.redis_client import get_redis
    from app.db.session import get_engine

    checks: dict[str, str] = {}
    status_code = 200
    try:
        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["mysql"] = "ok"
    except Exception:
        logger.exception("MySQL 健康检查失败")
        checks["mysql"] = "error"
        status_code = 503
    try:
        await get_redis().ping()
        checks["redis"] = "ok"
    except Exception:
        logger.exception("Redis 健康检查失败")
        checks["redis"] = "error"
        status_code = 503
    return {"code": 0 if status_code == 200 else 50300, "status": checks}

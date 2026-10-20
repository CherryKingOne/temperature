from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """业务异常基类：统一映射为业务状态码 + HTTP 状态码。"""

    code: int = 50000
    http_status: int = 500
    message: str = "服务器内部错误"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: int | None = None,
        http_status: int | None = None,
        detail: Any = None,
    ) -> None:
        self.message = message or self.message
        self.code = code if code is not None else self.code
        self.http_status = http_status if http_status is not None else self.http_status
        self.detail = detail
        super().__init__(self.message)

    def to_response(self, request: Request) -> JSONResponse:
        return JSONResponse(
            status_code=self.http_status,
            content={
                "code": self.code,
                "message": self.message,
                "data": self.detail,
                "request_id": getattr(request.state, "request_id", None),
            },
        )


class ValidationError(AppError):
    code = 40001
    http_status = 422
    message = "请求参数校验失败"


class UnauthorizedError(AppError):
    code = 40100
    http_status = 401
    message = "未登录或访问令牌无效"


class InvalidRefreshTokenError(AppError):
    code = 40101
    http_status = 401
    message = "刷新令牌无效或已失效"


class InvalidCredentialsError(AppError):
    code = 40102
    http_status = 401
    message = "邮箱或密码错误"


class AccountDisabledError(AppError):
    code = 40103
    http_status = 401
    message = "账号已被禁用"


class ForbiddenError(AppError):
    code = 40300
    http_status = 403
    message = "无权限访问该资源"


class NotFoundError(AppError):
    code = 40400
    http_status = 404
    message = "资源不存在"


class ConflictError(AppError):
    code = 40900
    http_status = 409
    message = "资源已存在"


class BusinessError(AppError):
    code = 42200
    http_status = 422
    message = "业务规则校验失败"


class TooManyRequestsError(AppError):
    code = 42900
    http_status = 429
    message = "请求过于频繁，请稍后再试"


class InternalError(AppError):
    code = 50000
    http_status = 500
    message = "服务器内部错误"


class ServiceUnavailableError(AppError):
    code = 50300
    http_status = 503
    message = "依赖服务不可用"

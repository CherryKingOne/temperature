from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.core.responses import ApiResponse
from app.db.models.admin import AdminUser
from app.deps.admin_auth import (
    get_auth_service,
    get_current_admin,
    get_lenient_access_claims,
)
from app.schemas.admin.auth import (
    AdminUserOut,
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SendEmailCodeRequest,
    SendEmailCodeResponse,
    UpdateProfileRequest,
)
from app.services.admin.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["admin-auth"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


@router.post(
    "/send-email-code",
    response_model=ApiResponse[SendEmailCodeResponse],
    summary="发送邮箱验证码",
    status_code=status.HTTP_200_OK,
)
async def send_email_code(
    payload: SendEmailCodeRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ApiResponse[SendEmailCodeResponse]:
    data = await service.send_email_code(payload, _client_ip(request))
    return ApiResponse(data=data)


@router.post(
    "/register",
    response_model=ApiResponse[AdminUserOut],
    summary="管理员注册（首个注册者为超级管理员）",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ApiResponse[AdminUserOut]:
    data = await service.register(payload)
    return ApiResponse(data=data)


@router.post(
    "/login",
    response_model=ApiResponse[LoginResponse],
    summary="管理员登录",
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: LoginRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ApiResponse[LoginResponse]:
    data = await service.login(payload, _client_ip(request))
    return ApiResponse(data=data)


@router.post(
    "/refresh-token",
    response_model=ApiResponse[RefreshTokenResponse],
    summary="刷新访问令牌",
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    payload: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ApiResponse[RefreshTokenResponse]:
    data = await service.refresh_token(payload)
    return ApiResponse(data=data)


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    summary="管理员登出",
    status_code=status.HTTP_200_OK,
)
async def logout(
    service: Annotated[AuthService, Depends(get_auth_service)],
    access_claims: Annotated[dict | None, Depends(get_lenient_access_claims)],
) -> ApiResponse[None]:
    if access_claims:
        await service.logout(access_claims)
    return ApiResponse(data=None, message="已退出登录")


@router.get(
    "/me",
    response_model=ApiResponse[AdminUserOut],
    summary="获取当前管理员信息",
    status_code=status.HTTP_200_OK,
)
async def get_current_admin_info(
    service: Annotated[AuthService, Depends(get_auth_service)],
    admin: Annotated[AdminUser, Depends(get_current_admin)],
) -> ApiResponse[AdminUserOut]:
    data = await service.get_current_admin(admin.id)
    return ApiResponse(data=data)


@router.patch(
    "/profile",
    response_model=ApiResponse[AdminUserOut],
    summary="修改自身资料",
    status_code=status.HTTP_200_OK,
)
async def update_profile(
    payload: UpdateProfileRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    admin: Annotated[AdminUser, Depends(get_current_admin)],
) -> ApiResponse[AdminUserOut]:
    data = await service.update_profile(admin, payload)
    return ApiResponse(data=data, message="资料已更新")


@router.post(
    "/change-password",
    response_model=ApiResponse[None],
    summary="修改密码",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    payload: ChangePasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    admin: Annotated[AdminUser, Depends(get_current_admin)],
) -> ApiResponse[None]:
    await service.change_password(admin, payload)
    return ApiResponse(data=None, message="密码修改成功，请重新登录")


@router.post(
    "/reset-password",
    response_model=ApiResponse[None],
    summary="重置密码",
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    payload: ResetPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> ApiResponse[None]:
    await service.reset_password(payload)
    return ApiResponse(data=None, message="密码重置成功，请使用新密码登录")

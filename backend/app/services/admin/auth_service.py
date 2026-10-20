from __future__ import annotations

import logging
from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import (
    AccountDisabledError,
    BusinessError,
    ConflictError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UnauthorizedError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.snowflake import next_id
from app.db.models.admin import AdminRole, AdminStatus, AdminUser
from app.db.models.platform import BOOTSTRAP_LOCK_ROW_ID, PlatformInvariant
from app.schemas.admin.auth import (
    AdminUserOut,
    ChangePasswordRequest,
    EmailCodeScene,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SendEmailCodeRequest,
    SendEmailCodeResponse,
    TokenPairOut,
)
from app.services.admin.verification_service import VerificationCodeService

logger = logging.getLogger(__name__)

REFRESH_SESSION_KEY = "admin:auth:refresh:{jti}"
SESSION_INDEX_KEY = "admin:auth:sessions:{admin_id}"
REVOKED_KEY = "admin:auth:revoked:{jti}"
LOGIN_FAIL_KEY = "admin:auth:login-fail:{email}"


class AuthService:
    """管理端登录认证业务逻辑。"""

    def __init__(
        self,
        *,
        session: AsyncSession,
        redis: Redis,
        settings: Settings,
        verification_service: VerificationCodeService,
    ) -> None:
        self._session = session
        self._redis = redis
        self.settings = settings
        self._verification = verification_service

    # ------------------------------------------------------------------
    # 邮箱验证码
    # ------------------------------------------------------------------
    async def send_email_code(
        self, payload: SendEmailCodeRequest, client_ip: str
    ) -> SendEmailCodeResponse:
        expires_in = await self._verification.send_code(payload.email, payload.scene, client_ip)
        return SendEmailCodeResponse(
            email=payload.email,
            scene=payload.scene.value,
            expires_in=expires_in,
            sent=True,
        )

    # ------------------------------------------------------------------
    # 注册
    # ------------------------------------------------------------------
    async def register(self, payload: RegisterRequest) -> AdminUserOut:
        """注册管理端账号；系统内首个注册账号自动成为超级管理员。"""
        email = payload.email
        await self._verification.verify_code(email, EmailCodeScene.REGISTER, payload.code)
        password_hash = hash_password(payload.password)

        try:
            async with self._session.begin():
                existing = await self._session.scalar(
                    select(AdminUser).where(AdminUser.email == email)
                )
                if existing is not None:
                    raise ConflictError("该邮箱已被注册")

                # 对不变式单行加行锁，把「首位注册者」的判定串行化
                await self._session.execute(
                    select(PlatformInvariant)
                    .where(PlatformInvariant.id == BOOTSTRAP_LOCK_ROW_ID)
                    .with_for_update()
                )
                # 必须使用加锁读（当前读）：在 REPEATABLE READ 下普通快照读
                # 可能读不到并发事务刚提交的数据，导致出现多个超级管理员
                total = len(
                    (
                        await self._session.scalars(
                            select(AdminUser.id).with_for_update()
                        )
                    ).all()
                )
                role = AdminRole.SUPER_ADMIN if total == 0 else AdminRole.ADMIN

                user = AdminUser(
                    id=next_id(),
                    name=payload.name,
                    email=email,
                    password_hash=password_hash,
                    role=role,
                    status=AdminStatus.ACTIVE,
                )
                self._session.add(user)
                await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError("该邮箱已被注册") from exc

        await self._session.refresh(user)
        logger.info("管理员注册成功 admin_id=%s role=%s", user.id, user.role.value)
        return self._to_out(user)

    # ------------------------------------------------------------------
    # 登录 / 刷新 / 登出
    # ------------------------------------------------------------------
    async def login(self, payload: LoginRequest, client_ip: str) -> LoginResponse:
        email = payload.email
        fail_key = LOGIN_FAIL_KEY.format(email=email)

        fail_count = int(await self._redis.get(fail_key) or 0)
        if fail_count >= self.settings.login_max_failures:
            raise InvalidCredentialsError("登录失败次数过多，账号已临时锁定")

        user = await self._session.scalar(select(AdminUser).where(AdminUser.email == email))
        if user is None or not verify_password(payload.password, user.password_hash):
            await self._record_login_failure(fail_key)
            raise InvalidCredentialsError("邮箱或密码错误")

        if user.status != AdminStatus.ACTIVE:
            raise AccountDisabledError("账号已被禁用")

        await self._redis.delete(fail_key)
        user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
        user.last_login_ip = client_ip
        await self._session.commit()
        await self._session.refresh(user)

        tokens = await self._issue_token_pair(user)
        logger.info("管理员登录成功 admin_id=%s", user.id)
        return LoginResponse(**tokens.model_dump(), admin=self._to_out(user))

    async def refresh_token(self, payload: RefreshTokenRequest) -> RefreshTokenResponse:
        claims = decode_token(self.settings, payload.refresh_token, "refresh")
        jti = str(claims["jti"])
        session_key = REFRESH_SESSION_KEY.format(jti=jti)

        admin_id_raw = await self._redis.get(session_key)
        if admin_id_raw is None:
            raise InvalidRefreshTokenError("刷新令牌无效或已失效")

        user = await self._session.scalar(
            select(AdminUser).where(AdminUser.id == int(admin_id_raw))
        )
        if user is None:
            raise InvalidRefreshTokenError("刷新令牌无效或已失效")
        if user.status != AdminStatus.ACTIVE:
            raise AccountDisabledError("账号已被禁用")

        # 轮换：旧刷新令牌立即失效，同时吊销由它签发的访问令牌
        pipe = self._redis.pipeline(transaction=False)
        pipe.delete(session_key)
        pipe.srem(SESSION_INDEX_KEY.format(admin_id=user.id), jti)
        pipe.set(
            REVOKED_KEY.format(jti=jti),
            "1",
            ex=self.settings.refresh_token_expire_seconds,
        )
        await pipe.execute()

        tokens = await self._issue_token_pair(user)
        return RefreshTokenResponse(**tokens.model_dump())

    async def logout(self, access_claims: dict) -> None:
        """登出：吊销当前会话的刷新令牌与访问令牌。"""
        jti = str(access_claims.get("jti", ""))
        session_id = access_claims.get("sid")
        admin_id = int(access_claims["sub"])
        if not jti:
            raise UnauthorizedError("访问令牌无效")

        pipe = self._redis.pipeline(transaction=False)
        pipe.set(
            REVOKED_KEY.format(jti=jti),
            "1",
            ex=max(self.settings.access_token_expire_seconds, 1),
        )
        if session_id:
            pipe.delete(REFRESH_SESSION_KEY.format(jti=session_id))
            pipe.srem(SESSION_INDEX_KEY.format(admin_id=admin_id), session_id)
            pipe.set(
                REVOKED_KEY.format(jti=session_id),
                "1",
                ex=self.settings.refresh_token_expire_seconds,
            )
        await pipe.execute()

    # ------------------------------------------------------------------
    # 当前管理员
    # ------------------------------------------------------------------
    async def get_current_admin(self, admin_id: int) -> AdminUserOut:
        user = await self._session.scalar(select(AdminUser).where(AdminUser.id == admin_id))
        if user is None:
            raise UnauthorizedError("管理员不存在")
        if user.status != AdminStatus.ACTIVE:
            raise UnauthorizedError("账号不可用")
        return self._to_out(user)

    # ------------------------------------------------------------------
    # 密码
    # ------------------------------------------------------------------
    async def change_password(self, admin: AdminUser, payload: ChangePasswordRequest) -> None:
        if not verify_password(payload.old_password, admin.password_hash):
            raise BusinessError("原密码不正确")
        if verify_password(payload.password, admin.password_hash):
            raise BusinessError("新密码不能与原密码相同")

        admin.password_hash = hash_password(payload.password)
        await self._session.commit()
        await self._revoke_all_sessions(admin.id)
        logger.info("管理员修改密码 admin_id=%s", admin.id)

    async def reset_password(self, payload: ResetPasswordRequest) -> None:
        email = payload.email
        await self._verification.verify_code(email, EmailCodeScene.RESET_PASSWORD, payload.code)

        user = await self._session.scalar(select(AdminUser).where(AdminUser.email == email))
        if user is None:
            raise BusinessError("验证码错误或已过期")

        user.password_hash = hash_password(payload.password)
        await self._session.commit()
        await self._revoke_all_sessions(user.id)
        await self._redis.delete(LOGIN_FAIL_KEY.format(email=email))
        logger.info("管理员重置密码 admin_id=%s", user.id)

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------
    async def _issue_token_pair(self, user: AdminUser) -> TokenPairOut:
        refresh_token, refresh_jti, _ = create_refresh_token(
            self.settings, admin_id=user.id, role=user.role.value
        )
        access_token, _, _ = create_access_token(
            self.settings,
            admin_id=user.id,
            role=user.role.value,
            session_id=refresh_jti,
        )

        session_key = REFRESH_SESSION_KEY.format(jti=refresh_jti)
        index_key = SESSION_INDEX_KEY.format(admin_id=user.id)
        pipe = self._redis.pipeline(transaction=False)
        pipe.set(
            session_key,
            str(user.id),
            ex=self.settings.refresh_token_expire_seconds,
        )
        pipe.sadd(index_key, refresh_jti)
        pipe.expire(index_key, self.settings.refresh_token_expire_seconds * 2)
        await pipe.execute()

        return TokenPairOut(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.settings.access_token_expire_seconds,
            refresh_expires_in=self.settings.refresh_token_expire_seconds,
        )

    async def _record_login_failure(self, fail_key: str) -> None:
        pipe = self._redis.pipeline(transaction=False)
        pipe.incr(fail_key)
        pipe.expire(fail_key, self.settings.login_lock_seconds)
        await pipe.execute()

    async def _revoke_all_sessions(self, admin_id: int) -> None:
        index_key = SESSION_INDEX_KEY.format(admin_id=admin_id)
        members = await self._redis.smembers(index_key)
        if members:
            pipe = self._redis.pipeline(transaction=False)
            for jti in members:
                pipe.delete(REFRESH_SESSION_KEY.format(jti=jti))
                pipe.set(
                    REVOKED_KEY.format(jti=jti),
                    "1",
                    ex=self.settings.refresh_token_expire_seconds,
                )
            await pipe.execute()
        await self._redis.delete(index_key)

    @staticmethod
    def _to_out(user: AdminUser) -> AdminUserOut:
        return AdminUserOut(
            id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role.value,
            is_super_admin=user.role == AdminRole.SUPER_ADMIN,
            status=user.status.value,
            last_login_at=user.last_login_at,
            last_login_ip=user.last_login_ip,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

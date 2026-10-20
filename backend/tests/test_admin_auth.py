"""管理端登录认证接口集成测试（真实 MySQL + Redis + 本地 SMTP）。"""

from __future__ import annotations

from httpx import AsyncClient

from app.core.snowflake import next_id

API = "/api/admin/auth"


def unique_email(prefix: str = "admin") -> str:
    return f"{prefix}-{next_id()}@example.com"


async def request_code(
    client: AsyncClient, email: str, scene: str = "register"
) -> None:
    response = await client.post(
        f"{API}/send-email-code", json={"email": email, "scene": scene}
    )
    assert response.status_code == 200, response.text
    assert response.json()["code"] == 0


async def register_admin(
    client: AsyncClient, email_code, email: str, name: str = "测试管理员"
) -> dict:
    await request_code(client, email)
    code = await email_code(email)
    response = await client.post(
        f"{API}/register",
        json={
            "name": name,
            "email": email,
            "code": code,
            "password": "Abcd@1234",
            "password_confirm": "Abcd@1234",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]


async def login_admin(client: AsyncClient, email: str, password: str = "Abcd@1234"):
    response = await client.post(f"{API}/login", json={"email": email, "password": password})
    return response


# ----------------------------------------------------------------------
# 注册
# ----------------------------------------------------------------------
async def test_first_registered_admin_becomes_super_admin(client, email_code):
    email = unique_email("first")
    data = await register_admin(client, email_code, email)

    assert data["role"] == "SUPER_ADMIN"
    assert data["is_super_admin"] is True
    assert data["status"] == "ACTIVE"


async def test_second_registered_admin_is_normal_admin(client, email_code):
    await register_admin(client, email_code, unique_email("first"))
    second = await register_admin(client, email_code, unique_email("second"))

    assert second["role"] == "ADMIN"
    assert second["is_super_admin"] is False


async def test_concurrent_registrations_produce_exactly_one_super_admin(client, email_code):
    import asyncio

    emails = [unique_email("concurrent"), unique_email("concurrent")]
    for email in emails:
        await request_code(client, email)
    codes = [await email_code(email) for email in emails]

    async def do_register(email: str, code: str):
        return await client.post(
            f"{API}/register",
            json={
                "name": "并发注册",
                "email": email,
                "code": code,
                "password": "Abcd@1234",
                "password_confirm": "Abcd@1234",
            },
        )

    responses = await asyncio.gather(
        do_register(emails[0], codes[0]), do_register(emails[1], codes[1])
    )

    assert all(response.status_code == 201 for response in responses), [
        response.text for response in responses
    ]
    roles = sorted(response.json()["data"]["role"] for response in responses)
    assert roles == ["ADMIN", "SUPER_ADMIN"]


async def test_register_with_duplicated_email_returns_conflict(client, email_code):
    email = unique_email("dup")
    await register_admin(client, email_code, email)

    await request_code(client, email)
    code = await email_code(email)
    response = await client.post(
        f"{API}/register",
        json={
            "name": "重复注册",
            "email": email,
            "code": code,
            "password": "Abcd@1234",
            "password_confirm": "Abcd@1234",
        },
    )
    assert response.status_code == 409
    assert response.json()["code"] == 40900


async def test_register_with_wrong_code_returns_422(client):
    email = unique_email("badcode")
    await request_code(client, email)
    response = await client.post(
        f"{API}/register",
        json={
            "name": "验证码错误",
            "email": email,
            "code": "000000",
            "password": "Abcd@1234",
            "password_confirm": "Abcd@1234",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == 42200


async def test_register_with_mismatched_passwords_returns_400(client, email_code):
    email = unique_email("mismatch")
    await request_code(client, email)
    code = await email_code(email)
    response = await client.post(
        f"{API}/register",
        json={
            "name": "密码不一致",
            "email": email,
            "code": code,
            "password": "Abcd@1234",
            "password_confirm": "Wxyz@5678",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == 40001


# ----------------------------------------------------------------------
# 登录
# ----------------------------------------------------------------------
async def test_login_returns_tokens_and_admin_profile(client, email_code):
    email = unique_email("login")
    await register_admin(client, email_code, email)

    response = await login_admin(client, email)
    assert response.status_code == 200, response.text
    data = response.json()["data"]

    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["expires_in"] == 7200
    assert data["admin"]["email"] == email


async def test_login_with_wrong_password_returns_401(client, email_code):
    email = unique_email("wrongpwd")
    await register_admin(client, email_code, email)

    response = await login_admin(client, email, password="Wrong@1234")
    assert response.status_code == 401
    assert response.json()["code"] == 40102


async def test_login_with_unknown_email_returns_401(client):
    response = await login_admin(client, unique_email("ghost"))
    assert response.status_code == 401
    assert response.json()["code"] == 40102


async def test_login_is_locked_after_max_failures(client, email_code):
    email = unique_email("lock")
    await register_admin(client, email_code, email)

    for _ in range(5):
        assert (await login_admin(client, email, password="Wrong@1234")).status_code == 401

    response = await login_admin(client, email)
    assert response.status_code == 401
    assert response.json()["code"] == 40102


# ----------------------------------------------------------------------
# 当前管理员
# ----------------------------------------------------------------------
async def test_get_current_admin_requires_token(client, email_code):
    email = unique_email("me")
    await register_admin(client, email_code, email)

    response = await client.get(f"{API}/me")
    assert response.status_code == 401
    assert response.json()["code"] == 40100


async def test_get_current_admin_returns_profile(client, email_code):
    email = unique_email("me")
    await register_admin(client, email_code, email)
    tokens = (await login_admin(client, email)).json()["data"]

    response = await client.get(
        f"{API}/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email"] == email
    assert data["is_super_admin"] is True
    assert "password" not in data


# ----------------------------------------------------------------------
# 刷新 / 登出
# ----------------------------------------------------------------------
async def test_refresh_token_rotates_and_rejects_old_token(client, email_code):
    email = unique_email("refresh")
    await register_admin(client, email_code, email)
    tokens = (await login_admin(client, email)).json()["data"]

    response = await client.post(
        f"{API}/refresh-token", json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    new_tokens = response.json()["data"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # 旧刷新令牌已失效
    again = await client.post(
        f"{API}/refresh-token", json={"refresh_token": tokens["refresh_token"]}
    )
    assert again.status_code == 401
    assert again.json()["code"] == 40101


async def test_logout_invalidates_access_token(client, email_code):
    email = unique_email("logout")
    await register_admin(client, email_code, email)
    tokens = (await login_admin(client, email)).json()["data"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    response = await client.post(f"{API}/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["code"] == 0

    after = await client.get(f"{API}/me", headers=headers)
    assert after.status_code == 401
    assert after.json()["code"] == 40100


async def test_logout_is_idempotent_when_token_already_invalid(client):
    response = await client.post(
        f"{API}/logout", headers={"Authorization": "Bearer not-a-valid-token"}
    )
    assert response.status_code == 200
    assert response.json()["code"] == 0


async def test_logout_without_authorization_header_returns_401(client):
    response = await client.post(f"{API}/logout")
    assert response.status_code == 401
    assert response.json()["code"] == 40100


# ----------------------------------------------------------------------
# 密码
# ----------------------------------------------------------------------
async def test_change_password_requires_correct_old_password(client, email_code):
    email = unique_email("chpwd")
    await register_admin(client, email_code, email)
    tokens = (await login_admin(client, email)).json()["data"]

    response = await client.post(
        f"{API}/change-password",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "old_password": "Wrong@1234",
            "password": "Wxyz@5678",
            "password_confirm": "Wxyz@5678",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == 42200


async def test_change_password_then_login_with_new_password(client, email_code):
    email = unique_email("chpwd2")
    await register_admin(client, email_code, email)
    tokens = (await login_admin(client, email)).json()["data"]

    response = await client.post(
        f"{API}/change-password",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={
            "old_password": "Abcd@1234",
            "password": "Wxyz@5678",
            "password_confirm": "Wxyz@5678",
        },
    )
    assert response.status_code == 200
    assert response.json()["code"] == 0

    # 修改密码后旧会话失效
    assert (await client.get(f"{API}/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})).status_code == 401

    assert (await login_admin(client, email, password="Wxyz@5678")).status_code == 200
    assert (await login_admin(client, email, password="Abcd@1234")).status_code == 401


async def test_reset_password_with_email_code(client, email_code):
    email = unique_email("reset")
    await register_admin(client, email_code, email)

    await request_code(client, email, scene="reset_password")
    code = await email_code(email, scene="reset_password")
    response = await client.post(
        f"{API}/reset-password",
        json={
            "email": email,
            "code": code,
            "password": "Wxyz@5678",
            "password_confirm": "Wxyz@5678",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["code"] == 0

    assert (await login_admin(client, email, password="Wxyz@5678")).status_code == 200


async def test_reset_password_rejects_register_scene_code(client, email_code):
    email = unique_email("scene")
    await request_code(client, email, scene="register")
    code = await email_code(email, scene="register")

    response = await client.post(
        f"{API}/reset-password",
        json={
            "email": email,
            "code": code,
            "password": "Wxyz@5678",
            "password_confirm": "Wxyz@5678",
        },
    )
    assert response.status_code == 422
    assert response.json()["code"] == 42200


# ----------------------------------------------------------------------
# 验证码
# ----------------------------------------------------------------------
async def test_send_email_code_rejects_wrong_scene(client):
    response = await client.post(
        f"{API}/send-email-code",
        json={"email": unique_email("scene"), "scene": "not_a_scene"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == 40001


async def test_send_email_code_is_rate_limited(client):
    email = unique_email("rate")
    await request_code(client, email)
    response = await client.post(
        f"{API}/send-email-code", json={"email": email, "scene": "register"}
    )
    assert response.status_code == 429
    assert response.json()["code"] == 42900


async def test_email_code_is_single_use(client, email_code, redis):
    email = unique_email("single")
    await request_code(client, email)
    code = await email_code(email)

    payload = {
        "name": "一次性验证码",
        "email": email,
        "code": code,
        "password": "Abcd@1234",
        "password_confirm": "Abcd@1234",
    }
    assert (await client.post(f"{API}/register", json=payload)).status_code == 201

    # 验证码被消费后从 Redis 删除，不可重复使用
    assert await redis.get(f"admin:auth:email-code:register:{email}") is None
    assert await redis.get(f"admin:auth:email-code:attempt:register:{email}") is None

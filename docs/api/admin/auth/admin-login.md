# 管理员登录

使用邮箱与密码登录管理端，签发访问令牌与刷新令牌。

- **文档标识**：`admin-login`
- **请求方法**：`POST`
- **请求路径**：`/api/admin/auth/login`
- **是否需要认证**：否
- **所属模块**：管理端 / 登录认证

## 请求头

| 名称 | 必填 | 说明 |
| --- | --- | --- |
| `Content-Type` | 是 | `application/json` |

## 请求参数

Body（JSON）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `email` | string | 是 | 合法邮箱 | 登录账号，服务端统一转小写 |
| `password` | string | 是 | 1–72 字节 | 登录密码明文，传输层必须使用 HTTPS |

请求示例：

```json
{
  "email": "admin@example.com",
  "password": "Abcd@1234"
}
```

## 响应示例

成功：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 7200,
    "refresh_expires_in": 604800,
    "admin": {
      "id": "370893497273683968",
      "name": "张伟",
      "email": "admin@example.com",
      "role": "SUPER_ADMIN",
      "is_super_admin": true,
      "status": "ACTIVE",
      "last_login_at": "2026-10-20T08:33:25Z",
      "created_at": "2026-10-20T08:33:25Z"
    }
  },
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

失败（账号或密码错误）：

```json
{
  "code": 40102,
  "message": "邮箱或密码错误",
  "data": null,
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

## 业务规则

1. 登录成功签发两枚 JWT：
   - `access_token`：有效期 **7200 秒**（2 小时），用于访问受保护的管理端接口。
   - `refresh_token`：有效期 **604800 秒**（7 天），仅用于换取新的访问令牌。
2. `refresh_token` 的 `jti` 同时写入 Redis（键 `admin:auth:refresh:{jti}`，TTL 与令牌一致），登出或轮换时可在 Redis 中即时吊销。
3. 密码错误统一返回 `40102`，不区分「邮箱不存在」与「密码错误」，避免账号枚举。
4. 账号状态为 `DISABLED` 时返回 `40103`，登录不签发任何令牌。
5. 连续登录失败 **5 次**，账号锁定 **15 分钟**（Redis 计数），锁定期间即使密码正确也返回 `40102`；成功登录后清空计数。
6. 登录成功更新管理员的 `last_login_at` 与 `last_login_ip`。
7. 令牌内容包含 `sub`（管理员 ID）、`role`、`jti`、`typ`（`access` / `refresh`），均使用 HS256 签名，密钥来自环境变量 `JWT_SECRET_KEY`。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 登录成功 |
| `40001` | 422 | 参数校验失败 |
| `40102` | 401 | 邮箱或密码错误（含账号锁定） |
| `40103` | 401 | 账号已被禁用 |
| `42900` | 429 | 请求过于频繁 |

## 调用示例

```bash
curl -X POST 'http://127.0.0.1:8000/api/admin/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"Abcd@1234"}'
```

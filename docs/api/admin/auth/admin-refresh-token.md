# 刷新访问令牌

使用刷新令牌换取新的访问令牌，刷新令牌同步轮换（旧刷新令牌立即失效）。

- **文档标识**：`admin-refresh-token`
- **请求方法**：`POST`
- **请求路径**：`/api/admin/auth/refresh-token`
- **是否需要认证**：否（通过请求体中的 `refresh_token` 校验身份）
- **所属模块**：管理端 / 登录认证

## 请求头

| 名称 | 必填 | 说明 |
| --- | --- | --- |
| `Content-Type` | 是 | `application/json` |

## 请求参数

Body（JSON）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `refresh_token` | string | 是 | JWT 字符串 | 登录接口签发的刷新令牌 |

请求示例：

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
    "refresh_expires_in": 604800
  },
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

失败：

```json
{
  "code": 40101,
  "message": "刷新令牌无效或已失效",
  "data": null,
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

## 业务规则

1. 校验顺序：签名与 `typ` → 是否过期 → Redis 中 `jti` 是否仍存在（是否被登出吊销）→ 对应管理员是否仍有效。
2. 校验通过后**签发新的访问令牌与新的刷新令牌**，并立即删除 Redis 中的旧 `jti`，实现刷新令牌轮换（Refresh Token Rotation），可有效发现并阻断刷新令牌被盗用。
3. 旧刷新令牌重复使用会被拒绝（`40101`）。
4. 管理员账号被禁用时，刷新同样失败。
5. 刷新不修改 `last_login_at`。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 刷新成功 |
| `40001` | 422 | 参数校验失败 |
| `40101` | 401 | 刷新令牌无效、已过期、已被登出吊销或已被轮换 |
| `40103` | 401 | 账号已被禁用 |

## 调用示例

```bash
curl -X POST 'http://127.0.0.1:8000/api/admin/auth/refresh-token' \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

# 修改密码

已登录管理员修改自身密码，修改成功后当前会话的刷新令牌全部失效，需重新登录。

- **文档标识**：`admin-change-password`
- **请求方法**：`POST`
- **请求路径**：`/api/admin/auth/change-password`
- **是否需要认证**：是
- **所属模块**：管理端 / 登录认证

## 请求头

| 名称 | 必填 | 说明 |
| --- | --- | --- |
| `Authorization` | 是 | `Bearer <access_token>` |
| `Content-Type` | 是 | `application/json` |

## 请求参数

Body（JSON）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
| --- | --- | --- | --- | --- |
| `old_password` | string | 是 | 1–72 字节 | 当前密码 |
| `password` | string | 是 | 8–72 字节 | 新密码 |
| `password_confirm` | string | 是 | 8–72 字节 | 确认新密码，必须与 `password` 一致 |

请求示例：

```json
{
  "old_password": "Abcd@1234",
  "password": "Wxyz@5678",
  "password_confirm": "Wxyz@5678"
}
```

## 响应示例

成功：

```json
{
  "code": 0,
  "message": "密码修改成功，请重新登录",
  "data": null,
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

失败（原密码错误）：

```json
{
  "code": 42200,
  "message": "原密码不正确",
  "data": null,
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

## 业务规则

1. 必须校验 `old_password` 与库中 bcrypt 哈希匹配，不匹配返回 `42200`。
2. `password` 与 `password_confirm` 不一致返回 `40001`。
3. 新密码不得与原密码相同，返回 `42200`。
4. 新密码使用 bcrypt（cost=12）重新哈希后覆盖写入。
5. 密码修改成功后，**吊销该管理员的全部刷新会话**（清除 Redis 中该管理员的所有 `admin:auth:refresh:*` 会话键），强制重新登录。
6. 接口需要携带有效的访问令牌，因此新密码不含「忘记密码」流程中的验证码校验。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 修改成功 |
| `40001` | 422 | 参数校验失败（两次新密码不一致、密码长度非法） |
| `40100` | 401 | 未登录或访问令牌无效 |
| `42200` | 422 | 原密码不正确，或新密码与原密码相同 |

## 调用示例

```bash
curl -X POST 'http://127.0.0.1:8000/api/admin/auth/change-password' \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"old_password":"Abcd@1234","password":"Wxyz@5678","password_confirm":"Wxyz@5678"}'
```

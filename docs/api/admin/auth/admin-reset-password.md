# 重置密码

忘记密码时，使用邮箱验证码设置新密码。

- **文档标识**：`admin-reset-password`
- **请求方法**：`POST`
- **请求路径**：`/api/admin/auth/reset-password`
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
| `email` | string | 是 | 合法邮箱 | 需要重置密码的账号邮箱 |
| `code` | string | 是 | 6 位纯数字 | 邮箱验证码，需与 `scene=reset_password` 的验证码匹配 |
| `password` | string | 是 | 8–72 字节 | 新密码 |
| `password_confirm` | string | 是 | 8–72 字节 | 确认新密码，必须与 `password` 一致 |

请求示例：

```json
{
  "email": "admin@example.com",
  "code": "654321",
  "password": "Wxyz@5678",
  "password_confirm": "Wxyz@5678"
}
```

## 响应示例

成功：

```json
{
  "code": 0,
  "message": "密码重置成功，请使用新密码登录",
  "data": null,
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

失败（验证码错误）：

```json
{
  "code": 42200,
  "message": "验证码错误或已过期",
  "data": null,
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

## 业务规则

1. 验证码必须来自 `scene=reset_password` 的发送请求；`scene=register` 的验证码不可用于重置密码。
2. 验证码校验通过后立即失效，且新密码写入后该邮箱的验证码不可再次使用。
3. 邮箱不存在时统一返回 `42200`（验证码校验失败在先），不泄露账号是否存在。
4. `password` 与 `password_confirm` 不一致返回 `40001`。
5. 新密码使用 bcrypt（cost=12）哈希后写入 MySQL。
6. 重置成功后吊销该管理员的全部刷新会话，并清空登录失败计数，强制重新登录。
7. 重置不改变管理员的角色与状态，超级管理员身份不受影响。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 重置成功 |
| `40001` | 422 | 参数校验失败（两次密码不一致、密码长度非法） |
| `42200` | 422 | 验证码错误/已过期，或邮箱不存在 |
| `42900` | 429 | 请求过于频繁 |

## 调用示例

```bash
curl -X POST 'http://127.0.0.1:8000/api/admin/auth/reset-password' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "admin@example.com",
    "code": "654321",
    "password": "Wxyz@5678",
    "password_confirm": "Wxyz@5678"
  }'
```

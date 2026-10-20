# 管理员注册

使用姓名、邮箱、邮箱验证码、密码、确认密码完成管理端账号注册。

- **文档标识**：`admin-register`
- **请求方法**：`POST`
- **请求路径**：`/api/admin/auth/register`
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
| `name` | string | 是 | 长度 2–50 个字符 | 姓名，管理员显示名称 |
| `email` | string | 是 | 合法邮箱，最长 254 字符 | 登录账号，服务端统一转小写，唯一 |
| `code` | string | 是 | 6 位纯数字 | 邮箱验证码，需与 `scene=register` 的验证码匹配 |
| `password` | string | 是 | 长度 8–72 字节 | 登录密码 |
| `password_confirm` | string | 是 | 长度 8–72 字节 | 确认密码，必须与 `password` 一致 |

请求示例：

```json
{
  "name": "张伟",
  "email": "admin@example.com",
  "code": "123456",
  "password": "Abcd@1234",
  "password_confirm": "Abcd@1234"
}
```

## 响应示例

成功：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "370893497273683968",
    "name": "张伟",
    "email": "admin@example.com",
    "role": "SUPER_ADMIN",
    "is_super_admin": true,
    "status": "ACTIVE",
    "created_at": "2026-10-20T08:33:25Z"
  },
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

失败（邮箱已注册）：

```json
{
  "code": 40900,
  "message": "该邮箱已被注册",
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

1. **第一个注册的人自动成为超级管理员**（`role = SUPER_ADMIN`）。判定方式：在同一事务内对 `platform_invariant` 表的唯一单行执行 `SELECT ... FOR UPDATE` 行锁，锁内统计管理员总数，为 `0` 时写入的角色即为 `SUPER_ADMIN`。并发注册请求被行锁串行化，**保证全系统有且仅有一位超级管理员**。
2. 之后注册的所有账号为普通管理员（`role = ADMIN`）。
3. 邮箱唯一索引约束，重复注册返回 `40900`。
4. 管理员 ID 为**雪花 ID**（64 位整数，由服务端生成、随时间单调递增），超出 JavaScript 安全整数范围，接口以**字符串**返回。
5. 验证码必须为 `scene=register` 的验证码，且未使用、未过期；校验通过后立即失效。
6. 密码与确认密码不一致时返回 `40001`。
6. 密码使用 **bcrypt** 单向哈希（cost=12）存储，数据库不保存明文。
8. 密码长度上限 72 字节，为 bcrypt 算法硬性上限，服务端会显式校验。
9. 注册成功不自动签发令牌，需调用登录接口获取令牌。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 注册成功 |
| `40001` | 422 | 参数校验失败（姓名/密码格式、两次密码不一致） |
| `40900` | 409 | 邮箱已被注册 |
| `42200` | 422 | 验证码错误或已过期 |
| `42900` | 429 | 请求过于频繁 |

## 调用示例

```bash
curl -X POST 'http://127.0.0.1:8000/api/admin/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "张伟",
    "email": "admin@example.com",
    "code": "123456",
    "password": "Abcd@1234",
    "password_confirm": "Abcd@1234"
  }'
```

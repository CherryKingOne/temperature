# 发送邮箱验证码

为指定邮箱发送图形/数字验证码，用于注册与重置密码场景的二次身份校验。

- **文档标识**：`admin-send-email-code`
- **请求方法**：`POST`
- **请求路径**：`/api/admin/auth/send-email-code`
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
| `email` | string | 是 | 合法邮箱，最长 254 字符 | 目标邮箱，服务端统一转小写 |
| `scene` | string | 是 | `register` / `reset_password` | 验证码用途，不同场景的验证码互不通用 |

> 说明：为避免邮箱被枚举，无论邮箱是否已注册、验证码是否实际发送，接口均返回 `code = 0`。

## 响应示例

成功：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "email": "admin@example.com",
    "scene": "register",
    "expires_in": 300,
    "sent": true
  },
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

失败（发送过于频繁）：

```json
{
  "code": 42900,
  "message": "验证码发送过于频繁，请 60 秒后再试",
  "data": null,
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

## 业务规则

1. 验证码为 6 位纯数字，由服务端使用 `secrets` 安全随机数生成，有效期 **300 秒**（5 分钟）。
2. 验证码只存储在 **Redis**，键格式 `admin:auth:email-code:{scene}:{email}`，过期自动清理，数据库不落库。
3. **同一邮箱 + 同一场景**，重复发送时旧验证码立即失效（覆盖写入），仅最新验证码可用。
4. 发送频率限制：
   - 同一邮箱 + 同一场景，**已有有效验证码**时 60 秒内不可重复发送；验证码已过期或被消费后可立即重新获取。
   - 同一 IP 10 分钟内最多发送 **30 次**（Redis 计数器实现）。
5. 验证码校验成功后立即失效（一次性使用）；同一邮箱 + 同一场景连续校验错误 **5 次**后立即作废，需重新获取。
6. 邮件通过 SMTP 真实发送，服务端未配置或 SMTP 不可用时返回 `50300`，**不返回任何模拟/占位数据**。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 发送成功（业务上视为成功） |
| `40001` | 422 | 参数校验失败（邮箱格式错误、scene 非法） |
| `42900` | 429 | 触发发送频率限制 |
| `50300` | 503 | 邮件服务不可用 |

## 调用示例

```bash
curl -X POST 'http://127.0.0.1:8000/api/admin/auth/send-email-code' \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","scene":"register"}'
```

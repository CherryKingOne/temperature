# 管理员登出

吊销当前会话的刷新令牌，使已签发的访问令牌在下一次校验时立即失效。

- **文档标识**：`admin-logout`
- **请求方法**：`POST`
- **请求路径**：`/api/admin/auth/logout`
- **是否需要认证**：是
- **所属模块**：管理端 / 登录认证

## 请求头

| 名称 | 必填 | 说明 |
| --- | --- | --- |
| `Authorization` | 是 | `Bearer <access_token>` |

## 请求参数

无（无 Body）。

## 响应示例

成功：

```json
{
  "code": 0,
  "message": "success",
  "data": null,
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

## 业务规则

1. 从访问令牌中解析 `jti` 与 `sid`，删除 Redis 中对应的刷新会话键 `admin:auth:refresh:{sid}`。
2. 同时将该访问令牌的 `jti` 加入 Redis 吊销集合 `admin:auth:revoked:{jti}`（TTL = 访问令牌剩余有效期），使**当前访问令牌在下一次请求时立即失效**。
3. 登出为幂等操作：**请求头缺少 `Authorization`** 时返回 `40100`；**令牌已过期 / 已被吊销**时仍返回 `code = 0`（视为已登出）。
4. 登出不影响其它设备/会话的登录状态；若需要踢出全部会话，使用 `admin-logout-all` 能力（后续版本提供）。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 登出成功（含令牌已失效的幂等场景） |
| `40100` | 401 | 未携带 `Authorization` 请求头 |

## 调用示例

```bash
curl -X POST 'http://127.0.0.1:8000/api/admin/auth/logout' \
  -H 'Authorization: Bearer <access_token>'
```

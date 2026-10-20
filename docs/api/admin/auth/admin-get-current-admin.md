# 获取当前管理员信息

返回当前登录管理员的完整资料，用于管理端初始化用户态。

- **文档标识**：`admin-get-current-admin`
- **请求方法**：`GET`
- **请求路径**：`/api/admin/auth/me`
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
  "data": {
    "id": "370893497273683968",
    "name": "张伟",
    "email": "admin@example.com",
    "phone": "13800138000",
    "role": "SUPER_ADMIN",
    "is_super_admin": true,
    "status": "ACTIVE",
    "last_login_at": "2026-10-20T08:33:25Z",
    "last_login_ip": "127.0.0.1",
    "created_at": "2026-10-20T08:33:25Z",
    "updated_at": "2026-10-20T08:33:25Z"
  },
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

## 响应字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 管理员 ID（雪花 ID，以字符串返回避免前端精度丢失） |
| `name` | string | 姓名 |
| `email` | string | 邮箱 |
| `phone` | string \| null | 手机号（联系方式） |
| `role` | string | 角色：`SUPER_ADMIN` / `ADMIN` |
| `is_super_admin` | bool | 是否为超级管理员，等价于 `role == "SUPER_ADMIN"` |
| `status` | string | 账号状态：`ACTIVE` / `DISABLED` |
| `last_login_at` | string \| null | 最近一次登录时间 |
| `last_login_ip` | string \| null | 最近一次登录 IP |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 最后更新时间 |

## 业务规则

1. 每次请求都会实时读取数据库中的管理员记录（不使用令牌内的缓存快照），保证禁用、改名等变更即时生效。
2. 若令牌对应的管理员已被删除或被禁用，返回 `40100`。
3. 响应中**不包含** `password` 哈希等敏感字段。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 获取成功 |
| `40100` | 401 | 未登录、访问令牌无效或账号不可用 |

## 调用示例

```bash
curl -X GET 'http://127.0.0.1:8000/api/admin/auth/me' \
  -H 'Authorization: Bearer <access_token>'
```

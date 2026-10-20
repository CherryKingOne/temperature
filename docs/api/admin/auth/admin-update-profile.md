# 更新个人资料

已登录管理员修改自身资料（姓名、手机号），用于维护联系方式。

- **文档标识**：`admin-update-profile`
- **请求方法**：`PATCH`
- **请求路径**：`/api/admin/auth/profile`
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
| `name` | string | 是 | 长度 2–50 个字符 | 姓名 |
| `phone` | string | 否 | 最长 20 字符 | 手机号；传空字符串表示清空 |

请求示例：

```json
{
  "name": "张伟",
  "phone": "13800138000"
}
```

## 响应示例

成功：

```json
{
  "code": 0,
  "message": "资料已更新",
  "data": {
    "id": "370893497273683968",
    "name": "张伟",
    "email": "admin@example.com",
    "phone": "13800138000",
    "role": "SUPER_ADMIN",
    "is_super_admin": true,
    "status": "ACTIVE",
    "created_at": "2026-10-20T08:33:25Z",
    "updated_at": "2026-10-21T09:10:00Z"
  },
  "request_id": "0f0d9a6e1b2c4d8e"
}
```

## 业务规则

1. 只能修改**自身**资料，无法通过该接口改动其他管理员；他人资料由人员管理接口维护。
2. `phone` 会被规范化：去掉空格、`-`、`()` 等分隔符后存储；全为空时按 `NULL` 保存。
3. `email`（登录账号）不通过该接口修改。
4. 手机号在系统内不做唯一性约束，仅作为联系方式展示。

## 错误码

| code | HTTP | 说明 |
| --- | --- | --- |
| `0` | 200 | 更新成功 |
| `40001` | 422 | 参数校验失败（姓名长度非法） |
| `40100` | 401 | 未登录或访问令牌无效 |

## 调用示例

```bash
curl -X PATCH 'http://127.0.0.1:8000/api/admin/auth/profile' \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"name":"张伟","phone":"13800138000"}'
```

# 管理端登录认证接口

管理端（`/api/admin`）的登录认证相关接口，所有文档以 `admin-` 开头。

## 接口清单

| 文档 | 方法 | 路径 | 认证 | 说明 |
| --- | --- | --- | --- | --- |
| [admin-send-email-code.md](./admin-send-email-code.md) | POST | `/api/admin/auth/send-email-code` | 否 | 发送邮箱验证码（注册 / 重置密码） |
| [admin-register.md](./admin-register.md) | POST | `/api/admin/auth/register` | 否 | 管理员注册（首个注册者为超级管理员） |
| [admin-login.md](./admin-login.md) | POST | `/api/admin/auth/login` | 否 | 登录并签发令牌 |
| [admin-refresh-token.md](./admin-refresh-token.md) | POST | `/api/admin/auth/refresh-token` | 否 | 刷新访问令牌（轮换刷新令牌） |
| [admin-logout.md](./admin-logout.md) | POST | `/api/admin/auth/logout` | 是 | 登出并吊销当前会话 |
| [admin-get-current-admin.md](./admin-get-current-admin.md) | GET | `/api/admin/auth/me` | 是 | 获取当前管理员信息 |
| [admin-change-password.md](./admin-change-password.md) | POST | `/api/admin/auth/change-password` | 是 | 修改自身密码 |
| [admin-reset-password.md](./admin-reset-password.md) | POST | `/api/admin/auth/reset-password` | 否 | 忘记密码时重置密码 |

## 注册流程

```
1) POST /api/admin/auth/send-email-code   {email, scene:"register"}   -> 获取 6 位验证码（邮件）
2) POST /api/admin/auth/register          {name, email, code, password, password_confirm}
   -> 第一个注册的账号自动成为 SUPER_ADMIN，之后注册为 ADMIN
3) POST /api/admin/auth/login             {email, password}          -> 返回 access_token / refresh_token
4) GET  /api/admin/auth/me                (Bearer access_token)      -> 返回当前管理员信息
```

## 忘记密码流程

```
1) POST /api/admin/auth/send-email-code   {email, scene:"reset_password"}
2) POST /api/admin/auth/reset-password    {email, code, password, password_confirm}
3) POST /api/admin/auth/login             {email, password}
```

## 令牌机制

| 令牌 | 有效期 | 用途 | 存储 |
| --- | --- | --- | --- |
| `access_token` | 2 小时 | 访问管理端受保护接口 | 不落库；登出后 `jti` 进入 Redis 吊销集合 |
| `refresh_token` | 7 天 | 换取新的访问令牌 | `jti` 存于 Redis，登出/轮换时即时吊销 |

刷新令牌采用**轮换**策略：每次刷新签发新的刷新令牌并立即废弃旧的，旧令牌复用会被拒绝。

## 相关文档

- 响应结构与错误码约定：[../../README.md](../../README.md)
- 管理端接口总览：[../README.md](../README.md)

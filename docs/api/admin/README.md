# 管理端（admin）接口

平台管理端接口，供后台管理系统调用。**该目录下所有文档均以 `admin-` 开头**，对应的路由均以 `/api/admin` 开头。

## 子目录

| 目录 | 说明 |
| --- | --- |
| [`auth/`](./auth/) | 登录认证：注册、登录、登出、令牌刷新、密码修改等 |

## 角色与权限

| 角色 | 标识 | 说明 |
| --- | --- | --- |
| 超级管理员 | `SUPER_ADMIN` | **系统中第一个注册的账号自动成为超级管理员**，拥有全部管理端权限 |
| 管理员 | `ADMIN` | 后续注册或由超级管理员创建的管理员账号 |

超级管理员身份在注册落库时依据「当前管理员总数是否为 0」判定，并发注册通过数据库行锁串行化，保证只有一位超级管理员。

## ID 策略

管理员 ID 采用**雪花 ID**（64 位整数：1 位符号 + 41 位毫秒时间戳 + 10 位机器号 + 12 位序列号），由服务端生成、随时间单调递增，不依赖数据库自增。

> 雪花 ID 超出 JavaScript `Number.MAX_SAFE_INTEGER`（2^53-1），因此接口中 `id` 统一以**字符串**返回，避免前端解析时精度丢失。

## 接口清单

| 文档 | 方法 | 路径 | 认证 |
| --- | --- | --- | --- |
| [admin-send-email-code.md](./auth/admin-send-email-code.md) | POST | `/api/admin/auth/send-email-code` | 否 |
| [admin-register.md](./auth/admin-register.md) | POST | `/api/admin/auth/register` | 否 |
| [admin-login.md](./auth/admin-login.md) | POST | `/api/admin/auth/login` | 否 |
| [admin-refresh-token.md](./auth/admin-refresh-token.md) | POST | `/api/admin/auth/refresh-token` | 否（携带 refresh_token） |
| [admin-logout.md](./auth/admin-logout.md) | POST | `/api/admin/auth/logout` | 是 |
| [admin-get-current-admin.md](./auth/admin-get-current-admin.md) | GET | `/api/admin/auth/me` | 是 |
| [admin-change-password.md](./auth/admin-change-password.md) | POST | `/api/admin/auth/change-password` | 是 |
| [admin-reset-password.md](./auth/admin-reset-password.md) | POST | `/api/admin/auth/reset-password` | 否 |

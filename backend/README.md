# Temperature Backend

Temperature 服务的后端工程。Python 3.12 + `uv` + FastAPI + MySQL + Redis。

## 技术栈

| 组件 | 选型 |
| --- | --- |
| Web 框架 | FastAPI（异步） |
| ORM | SQLAlchemy 2.0（async）+ asyncmy 驱动 |
| 数据库 | MySQL 8 |
| 缓存 | Redis 7（验证码、会话、限流、令牌吊销） |
| 鉴权 | JWT（HS256，access + refresh 轮换） |
| 密码 | bcrypt（cost=12） |
| ID | 雪花 ID（`app/core/snowflake.py`，机器号由 `SNOWFLAKE_WORKER_ID` 指定） |
| 邮件 | 投递后端可选：`console`（打印到日志）/ SMTP（aiosmtplib，真实发送） |

> 代码中不含任何 mock / 模拟数据：验证码真实写入 Redis 并按配置投递，账号数据只落 MySQL。
> 邮件投递有两种后端：`console`（只打印到服务日志）与 `smtp`（真实发送）——两者都不改变验证码的生成与校验逻辑。
>
> MySQL 侧**不开启任何调试日志**：连接引擎不打印 SQL 语句与执行计划，服务日志只有应用级 INFO。

## 目录结构

```
backend/
├── data/                   # 本地数据目录（MySQL/Redis 数据，docker compose 相对路径挂载）
├── app/
│   ├── main.py                 # 应用入口、异常处理、生命周期
│   ├── core/                   # 配置、错误、安全、Redis、响应封装
│   ├── db/                     # 声明基类、会话、ORM 模型
│   ├── schemas/admin/          # 管理端请求 / 响应模型
│   ├── services/               # 业务逻辑（邮箱、验证码、认证）
│   ├── api/admin/auth/         # 管理端登录认证路由
│   └── deps/                   # FastAPI 依赖（鉴权、DB、Redis）
├── tests/                      # 集成测试（真实 MySQL / Redis / SMTP）
└── pyproject.toml
```

接口文档见 [`../docs/api/admin`](../docs/api/admin)。

## 环境准备

### 0. 本地数据目录（重要）

数据库数据文件**统一放在 `backend/data/` 下**，由 `docker-compose.yml` 用**相对路径**挂载：

```yaml
volumes:
  - ./backend/data/mysql:/var/lib/mysql      # MySQL 数据文件
  - ./backend/data/redis:/data               # Redis 持久化
```

相对路径是相对于 `docker-compose.yml` 所在目录解析的，**仓库 clone 到任何服务器、任何目录下都不用改配置**（写绝对路径才会因服务器不同而失效）。

```
backend/data/                 # 随仓库位置自适应，服务器换目录也不用改配置
├── mysql/                    # docker compose 挂载的 MySQL 数据目录
├── redis/                    # docker compose 挂载的 Redis 持久化目录
└── .gitkeep
```

这两个目录就是 `docker-compose.yml` 里的挂载点，由 Docker 自动创建与初始化；`backend/data/*` 已在 `.gitignore` 中忽略（仅保留 `.gitkeep`），数据不会进版本库。

### 1. 启动依赖服务

```bash
cd ..                     # 项目根目录 temperature/
docker compose up -d      # MySQL 8 + Redis 7
```

MySQL 容器会自动建库并创建账号：`temperature/temperature123`（业务库 `temperature`）、`root/root`（管理用）。Redis 密码与 MySQL 业务密码一致（`temperature123`）。测试库 `temperature_test` 由测试夹具自动创建。

> 如果不用 Docker 而用本机安装的 MySQL：把数据目录放在仓库外（如 `/opt/homebrew/var/mysql`），`backend/data/` 留给 compose 挂载，两者不要混用；`.env` 里的连接信息保持不变即可。
> 本机已装 MySQL/Redis 且占用了 3306/6379 时，先停掉本地服务再 `docker compose up -d`（端口冲突）。

### 2. 准备数据库与账号

用 docker compose 时容器已自动建好；用本机 MySQL 时手动执行：

```bash
mysql -uroot -p <<'SQL'
CREATE DATABASE temperature DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE temperature_test DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'temperature'@'%' IDENTIFIED BY 'temperature';
GRANT ALL PRIVILEGES ON temperature.* TO 'temperature'@'%';
FLUSH PRIVILEGES;
SQL
```
```

### 3. 安装依赖并配置环境变量

```bash
cd backend
uv sync --all-groups
cp ../.env.example ../.env   # 项目根目录的 .env 为统一配置源（Compose 与后端共用）
```

`JWT_SECRET_KEY` 至少 16 位，生产环境请使用 `openssl rand -hex 32` 生成。

> 根目录 `.env` 会被后端自动读取（在 `backend/` 下启动时按 `../.env` 加载）；
> 如需只为本地调试改几项，可以在 `backend/.env` 里放同名变量覆盖根目录配置。

### 配置项

连接类配置按 host / port / user / password / name 分项填写，连接串由代码内部拼装：

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MYSQL_HOST` | `127.0.0.1` | MySQL 地址 |
| `MYSQL_PORT` | `3306` | MySQL 端口 |
| `MYSQL_USER` | `root` | MySQL 账号 |
| `MYSQL_PASSWORD` | 空 | MySQL 密码 |
| `MYSQL_DATABASE` | `temperature` | MySQL 库名 |
| `REDIS_HOST` | `127.0.0.1` | Redis 地址 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `REDIS_DB` | `0` | Redis 库编号 |
| `REDIS_PASSWORD` | 空 | Redis 密码 |
| `SNOWFLAKE_WORKER_ID` | `1` | 雪花 ID 机器号，多实例部署时每台机器取不同值 |
| `JWT_SECRET_KEY` | 无（必填） | 令牌签名密钥，≥16 位 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | 访问令牌有效期（分钟） |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | 刷新令牌有效期（天） |
| `EMAIL_CODE_EXPIRE_SECONDS` | `300` | 邮箱验证码有效期（秒） |
| `EMAIL_CODE_MAX_ATTEMPTS` | `5` | 验证码连续错误次数上限 |
| `LOGIN_MAX_FAILURES` | `5` | 登录失败多少次后锁定 |
| `LOGIN_LOCK_SECONDS` | `900` | 锁定时长（秒） |
| `EMAIL_BACKEND` | `smtp` | 邮件后端：`console`=验证码只打印到服务日志（本地开发，免邮件容器）；`smtp`=真实发送 |
| `SMTP_HOST` / `SMTP_PORT` | 空 / `465` | 邮件服务器；`EMAIL_BACKEND=smtp` 且为空时验证码接口返回 503 |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | 空 | SMTP 账号密码 |
| `SMTP_USE_SSL` | `true` | `true`=465 隐式 TLS；`false`=587 由服务端协商 STARTTLS |
| `SMTP_FROM_EMAIL` | 空 | 发件人邮箱 |
| `API_PREFIX` | `/api` | 接口前缀 |
| `CORS_ORIGINS` | 空 | 允许的跨域来源，逗号分隔 |

### 4. 启动服务

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- 交互式文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>（同时探测 MySQL 与 Redis）

## 常用命令

```bash
uv sync --all-groups          # 安装 / 同步依赖
uv run pytest                 # 运行集成测试（需要真实 MySQL / Redis）
uv add <pkg>                  # 添加依赖
```

## 邮件服务说明

验证码的生成、写入 Redis、校验流程与投递方式无关，只由 `EMAIL_BACKEND` 决定"怎么送到你手上"。

### 本地开发：`EMAIL_BACKEND=console`（默认推荐，零邮件容器）

```dotenv
EMAIL_BACKEND=console
```

验证码直接打印到服务的标准输出（启动 uvicorn 的终端窗口）里：

```
============================================================
【console 邮件】管理员注册验证码
收件人：admin@example.com
验证码：123456
有效期：5 分钟
（EMAIL_BACKEND=console：邮件未真实发送，仅打印到服务输出）
============================================================
```

不需要起任何邮件容器，也不会误发到真实邮箱。应用启动时同样会打一条 WARN 提醒当前是 console 后端。

### 生产环境：`EMAIL_BACKEND=smtp`

```dotenv
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USERNAME=你的邮箱账号
SMTP_PASSWORD=你的邮箱授权码
SMTP_USE_SSL=true
SMTP_FROM_EMAIL=你的邮箱账号
```

465 端口用 `SMTP_USE_SSL=true`，587 端口用 `SMTP_USE_SSL=false`（由服务端协商 STARTTLS）。`SMTP_HOST` 未配置时验证码接口返回 `50300`（依赖服务不可用），**不会**返回任何伪造的验证码。

## 测试说明

`tests/` 下的用例是**真实集成测试**：

- 使用真实的 MySQL 库 `temperature_test`（按 `app/db/schema.py` 内置 SQL 建表）
- 使用真实的 Redis 库 `DB 15`（验证码、登录失败计数、令牌吊销）
- 使用进程内真实 SMTP 服务器（aiosmtpd）接收验证码邮件，验证码从 Redis 真实读取

运行前确保 MySQL（`127.0.0.1:3306`）与 Redis（`127.0.0.1:6379`）可用（`docker compose up -d` 即可）；连接信息通过环境变量覆盖（见 `tests/conftest.py` 顶部）。

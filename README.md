# Temperature

Temperature 平台工程：后端服务（Python）+ 接口文档。

## 目录结构

```
temperature/
├── .env.example          # 统一配置模板（复制为 .env，Docker Compose 与后端共用）
├── docs/                  # 接口文档（Markdown）
│   ├── README.md          # 响应结构、错误码等通用约定
│   └── api/
│       └── admin/         # 管理端接口
│           ├── README.md
│           └── auth/      # 登录认证接口，一个接口一个 md
├── backend/               # 后端服务（Python 3.12 / FastAPI / MySQL / Redis）
│   └── data/              # 本地数据目录（MySQL/Redis 数据，compose 相对路径挂载）
└── docker-compose.yml     # 本地 MySQL + Redis
```

## 快速开始

```bash
cp .env.example .env                # 复制配置模板（Compose 与后端共用，改这里即可）
docker compose up -d                # 启动 MySQL / Redis
cd backend
uv sync --all-groups
uv run uvicorn app.main:app --reload  # 启动时自动建表
```

接口文档：<http://127.0.0.1:8000/docs>

## 当前进度

- [x] 管理端登录认证（注册 / 登录 / 登出 / 刷新令牌 / 密码）
- [x] 邮箱验证码（Redis 存储 + SMTP 真实发送，本地可用 console 后端直接打印到终端）
- [x] 首位注册者自动成为超级管理员（数据库行锁保证唯一性）
- [ ] 管理员列表 / 详情 / 启用禁用 / 角色调整
- [ ] 菜单与权限体系

## 文档索引

- 通用约定：[docs/README.md](./docs/README.md)
- 管理端接口：[docs/api/admin/README.md](./docs/api/admin/README.md)
- 登录认证：[docs/api/admin/auth/README.md](./docs/api/admin/auth/README.md)

# Temperature Frontend

Temperature 平台管理端前端。Vue 3 + TypeScript + Vite + Pinia + Vue Router。

## 技术栈

| 组件 | 选型 |
| --- | --- |
| 框架 | Vue 3（`<script setup>` + TypeScript） |
| 构建 | Vite 8 |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| 样式 | 原生 CSS + CSS 变量（无 UI 框架、无图标库依赖） |

## 目录结构

```
frontend/
├── src/
│   ├── api/                  # 接口层
│   │   ├── client.ts         # fetch 封装：统一响应解包、业务异常、令牌注入
│   │   └── admin/auth.ts     # 管理端认证接口
│   ├── assets/               # 样式
│   │   ├── base.css          # 重置与排版
│   │   ├── theme.css         # 主题变量：主题色 / 侧边栏 / 明暗模式
│   │   ├── components.css    # 组件样式（BEM）
│   │   ├── utils.css         # 工具类（间距 / 布局 / 文字）
│   │   └── main.css          # 样式入口
│   ├── components/
│   │   ├── auth/AuthLayout.vue      # 认证页布局（左介绍 + 右表单）
│   │   └── ui/                     # 基础组件：按钮 / 输入框 / 复选框 / 图标 / 提示 / 主题切换
│   ├── layouts/BasicLayout.vue     # 基本布局：顶部导航 + 侧边栏 + 页签
│   ├── composables/useCountdown.ts # 验证码重发倒计时（前端负责）
│   ├── router/index.ts       # 路由与登录守卫（默认落地页 /profile）
│   ├── stores/               # Pinia：auth（登录态）/ theme（主题）/ toast（提示）
│   ├── types/api.ts          # 接口类型定义
│   └── views/                # 页面：登录 / 注册 / 首页
├── index.html
└── vite.config.ts            # 开发服务器与 /api 代理
```

## 本地开发

```sh
bun install
bun dev          # http://127.0.0.1:3000
```

开发服务器把 `/api` 代理到后端（默认 `http://127.0.0.1:8000`），避免跨域：

```sh
# 临时换后端地址
VITE_PROXY_TARGET=http://127.0.0.1:8001 bun dev
```

后端服务需要在 `D:\temperature\backend` 下启动（`uv run uvicorn app.main:app --reload`），并使用项目根目录的 `.env` 配置（`EMAIL_BACKEND=console` 时验证码会直接打印到后端终端）。

### 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `/api` | 接口根路径；生产环境由 Nginx 反向代理时保持相对路径即可 |
| `VITE_PROXY_TARGET` | `http://127.0.0.1:8000` | 开发环境 `/api` 代理目标 |

## 设计规范

设计对标企业级后台管理系统（若依风格）：扁平化、Bootstrap 风格、多主题可切换。

### 主题

主题色、侧边栏主题、明暗模式全部通过 `<html>` 上的 `data-*` 属性驱动，由 CSS 变量接管：

| 属性 | 取值 | 说明 |
| --- | --- | --- |
| `data-theme` | `blue` / `green` / `red` / `yellow` / `purple` | 主题色（主色 + 激活色） |
| `data-sidebar` | `dark` / `light` / `deep` | 侧边栏主题 |
| `data-theme-mode` | `light` / `dark` | 明暗模式 |

切换状态由 `stores/theme.ts` 维护并写入 `localStorage`，页面右上角的切换器可直接操作。

### 组件

`components/ui/` 下为基础组件，样式统一在 `assets/components.css` 中以 BEM 规范维护：

- `BaseButton`：圆角 3px，高 34px（标准）/ 28px（小），支持 primary / success / warning / danger / info、rounded、outline、block、loading。
- `BaseInput`：高 34px，边框 `#ddd`，聚焦高亮，支持前置图标与密码明文切换。
- `BaseCheckbox`：18x18px 选中态为主题色。
- `UiIcon`：内置线性图标，不依赖外部图标库。
- `ToastHost`：顶部提示，3 秒自动关闭。

### 页面

- `/login`：全屏背景 + 750px 半透明登录框，左侧系统介绍、右侧登录表单。
- `/register`：姓名、邮箱、邮箱验证码（前端 60 秒倒计时）、密码、确认密码；首个注册账号自动成为超级管理员。
- `/profile`：**登录后的默认落地页**。左侧个人名片（头像、姓名、角色、账号概况），右侧账号信息与安全设置（修改密码）。修改密码需要「邮箱验证码 + 当前密码」双重校验，验证码发送到账号邮箱，前端 60 秒倒计时；该页面对所有账号开放，不受菜单权限影响，因此无权限的账号登录后也有页面可看。
- `/home`：管理后台首页概览（顶部导航 + 侧边栏 + 页签）。

登录成功后默认跳转 `/profile`（`router/index.ts` 中的 `DEFAULT_HOME`）；若访问地址带 `?redirect=`，登录后会回到该地址。侧边栏中尚未实现的模块（管理员管理、系统设置）以置灰不可点状态占位。

## 常用命令

```sh
bun dev            # 启动开发服务器
bun run build      # 类型检查 + 生产构建
bun run preview    # 本地预览构建产物
bun lint           # oxlint + eslint
bun run format     # prettier 格式化
```

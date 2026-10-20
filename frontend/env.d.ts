/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 接口根路径，默认 /api（开发环境由 Vite 代理转发到后端） */
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

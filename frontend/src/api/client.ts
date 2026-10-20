import type { ApiResponse } from '@/types/api'

/** 接口根路径：默认 /api，开发环境由 Vite 代理转发到后端 */
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? '/api'

const TOKEN_KEY = 'temperature_access_token'

/** 业务异常：携带后端业务状态码 */
export class ApiError extends Error {
  readonly code: number
  readonly httpStatus: number
  readonly requestId: string | null

  constructor(code: number, message: string, httpStatus: number, requestId: string | null) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.httpStatus = httpStatus
    this.requestId = requestId
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
  /** 是否携带访问令牌，默认携带 */
  auth?: boolean
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = options

  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(50000, '网络连接失败，请检查后端服务是否已启动', 0, null)
  }

  let payload: ApiResponse<T> | null = null
  try {
    payload = (await response.json()) as ApiResponse<T>
  } catch {
    payload = null
  }

  if (!response.ok || !payload || payload.code !== 0) {
    const code = payload?.code ?? response.status * 100
    const message = payload?.message ?? `请求失败（HTTP ${response.status}）`
    throw new ApiError(code, message, response.status, payload?.request_id ?? null)
  }

  return payload.data as T
}

export const http = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: 'POST', body }),
}

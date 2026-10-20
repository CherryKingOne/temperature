/** 后端统一响应结构与认证相关类型定义（对应 docs/api/admin/auth） */

/** 统一响应包装 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T | null
  request_id: string | null
}

/** 管理员账号 */
export interface AdminUser {
  /** 雪花 ID 超出 JS 安全整数范围，服务端以字符串返回 */
  id: string
  name: string
  email: string
  role: 'SUPER_ADMIN' | 'ADMIN'
  is_super_admin: boolean
  status: 'ACTIVE' | 'DISABLED'
  last_login_at: string | null
  last_login_ip: string | null
  created_at: string
  updated_at: string
}

/** 令牌对 */
export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  refresh_expires_in: number
}

/** 登录响应 */
export interface LoginResult extends TokenPair {
  admin: AdminUser
}

/** 发送验证码响应 */
export interface SendEmailCodeResult {
  email: string
  scene: EmailCodeScene
  expires_in: number
  sent: boolean
}

/** 验证码场景 */
export type EmailCodeScene = 'register' | 'reset_password'

/** 登录请求 */
export interface LoginPayload {
  email: string
  password: string
}

/** 注册请求 */
export interface RegisterPayload {
  name: string
  email: string
  code: string
  password: string
  password_confirm: string
}

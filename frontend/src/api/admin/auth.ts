import { http } from '@/api/client'
import type {
  AdminUser,
  EmailCodeScene,
  LoginPayload,
  LoginResult,
  RegisterPayload,
  SendEmailCodeResult,
} from '@/types/api'

const BASE = '/admin/auth'

/** 发送邮箱验证码 */
export function sendEmailCode(email: string, scene: EmailCodeScene) {
  return http.post<SendEmailCodeResult>(
    `${BASE}/send-email-code`,
    { email, scene },
    { auth: false },
  )
}

/** 管理员登录 */
export function login(payload: LoginPayload) {
  return http.post<LoginResult>(`${BASE}/login`, payload, { auth: false })
}

/** 管理员注册 */
export function register(payload: RegisterPayload) {
  return http.post<AdminUser>(`${BASE}/register`, payload, { auth: false })
}

/** 获取当前管理员信息 */
export function fetchCurrentAdmin() {
  return http.get<AdminUser>(`${BASE}/me`)
}

/** 登出 */
export function logout() {
  return http.post<null>(`${BASE}/logout`)
}

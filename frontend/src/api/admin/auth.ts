import { http } from '@/api/client'
import type {
  AdminUser,
  EmailCodeScene,
  LoginPayload,
  LoginResult,
  RegisterPayload,
  SendEmailCodeResult,
  UpdateProfilePayload,
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

/** 修改自身资料（姓名、手机号） */
export function updateProfile(payload: UpdateProfilePayload) {
  return http.patch<AdminUser>(`${BASE}/profile`, payload)
}

/** 修改自身密码（需邮箱验证码 + 原密码） */
export function changePassword(payload: {
  code: string
  old_password: string
  password: string
  password_confirm: string
}) {
  return http.post<null>(`${BASE}/change-password`, payload)
}

/** 登出 */
export function logout() {
  return http.post<null>(`${BASE}/logout`)
}

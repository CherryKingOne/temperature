import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import {
  fetchCurrentAdmin,
  login as loginApi,
  logout as logoutApi,
  register as registerApi,
  updateProfile as updateProfileApi,
} from '@/api/admin/auth'
import { ApiError, getToken, setToken } from '@/api/client'
import type { AdminUser, LoginPayload, RegisterPayload, UpdateProfilePayload } from '@/types/api'
import { isTokenExpired } from '@/utils/token'

/** 读取本地令牌；已过期的令牌直接作废 */
function loadToken(): string | null {
  const token = getToken()
  if (token && isTokenExpired(token)) {
    setToken(null)
    return null
  }
  return token
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(loadToken())
  const admin = ref<AdminUser | null>(null)
  /** 是否已登录：有访问令牌即视为已登录 */
  const isLoggedIn = computed(() => Boolean(token.value))
  /** 是否为超级管理员（首个注册账号） */
  const isSuperAdmin = computed(() => admin.value?.is_super_admin ?? false)

  async function login(payload: LoginPayload): Promise<AdminUser> {
    const result = await loginApi(payload)
    token.value = result.access_token
    setToken(result.access_token)
    admin.value = result.admin
    return result.admin
  }

  async function register(payload: RegisterPayload): Promise<AdminUser> {
    return registerApi(payload)
  }

  /** 拉取当前管理员信息（页面刷新后恢复登录态用） */
  async function loadCurrentAdmin(): Promise<AdminUser> {
    try {
      const user = await fetchCurrentAdmin()
      admin.value = user
      return user
    } catch (error) {
      if (error instanceof ApiError && error.httpStatus === 401) {
        clearSession()
      }
      throw error
    }
  }

  /** 修改自身资料（姓名、手机号） */
  async function updateProfile(payload: UpdateProfilePayload): Promise<AdminUser> {
    const user = await updateProfileApi(payload)
    admin.value = user
    return user
  }

  /** 清空本地登录态（不改服务端数据） */
  function clearSession(): void {
    token.value = null
    setToken(null)
    admin.value = null
  }

  async function logout(): Promise<void> {
    try {
      await logoutApi()
    } finally {
      clearSession()
    }
  }

  return {
    token,
    admin,
    isLoggedIn,
    isSuperAdmin,
    login,
    register,
    loadCurrentAdmin,
    updateProfile,
    clearSession,
    logout,
  }
})

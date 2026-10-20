import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import {
  fetchCurrentAdmin,
  login as loginApi,
  logout as logoutApi,
  register as registerApi,
} from '@/api/admin/auth'
import { getToken, setToken } from '@/api/client'
import type { AdminUser, LoginPayload, RegisterPayload } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(getToken())
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

  async function loadCurrentAdmin(): Promise<AdminUser> {
    const user = await fetchCurrentAdmin()
    admin.value = user
    return user
  }

  async function logout(): Promise<void> {
    try {
      await logoutApi()
    } finally {
      token.value = null
      setToken(null)
      admin.value = null
    }
  }

  return { token, admin, isLoggedIn, isSuperAdmin, login, register, loadCurrentAdmin, logout }
})

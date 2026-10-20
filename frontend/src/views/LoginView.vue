<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import AuthLayout from '@/components/auth/AuthLayout.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import UiIcon from '@/components/ui/UiIcon.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const REMEMBER_KEY = 'temperature_remember_email'
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const email = ref('')
const password = ref('')
const remember = ref(false)
const errors = ref<{ email?: string; password?: string }>({})
const errorMessage = ref('')
const submitting = ref(false)

onMounted(() => {
  const remembered = localStorage.getItem(REMEMBER_KEY)
  if (remembered) {
    email.value = remembered
    remember.value = true
  }
  const queryEmail = route.query.email
  if (typeof queryEmail === 'string' && queryEmail) {
    email.value = queryEmail
  }
})

function validate(): boolean {
  const next: { email?: string; password?: string } = {}
  const value = email.value.trim()
  if (!value) {
    next.email = '请输入邮箱'
  } else if (!EMAIL_PATTERN.test(value)) {
    next.email = '邮箱格式不正确'
  }
  if (!password.value) {
    next.password = '请输入密码'
  }
  errors.value = next
  return Object.keys(next).length === 0
}

async function onSubmit(): Promise<void> {
  errorMessage.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const admin = await auth.login({ email: email.value.trim(), password: password.value })
    if (remember.value) {
      localStorage.setItem(REMEMBER_KEY, email.value.trim())
    } else {
      localStorage.removeItem(REMEMBER_KEY)
    }
    toast.success(`欢迎回来，${admin.name}`)
    await router.push('/')
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : '登录失败，请稍后再试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthLayout title="账号登录" subtitle="请使用管理员邮箱登录管理后台">
    <form class="form" novalidate @submit.prevent="onSubmit">
      <div v-if="errorMessage" class="auth__error">
        <UiIcon name="alert-circle" :size="15" />
        <span>{{ errorMessage }}</span>
      </div>

      <div class="form-item">
        <label class="form-item__label form-item__label--required" for="login-email">邮箱</label>
        <BaseInput
          id="login-email"
          v-model="email"
          type="email"
          icon="mail"
          placeholder="请输入管理员邮箱"
          :error="errors.email"
          autocomplete="username"
        />
        <p v-if="errors.email" class="form-item__error">{{ errors.email }}</p>
      </div>

      <div class="form-item">
        <label class="form-item__label form-item__label--required" for="login-password">密码</label>
        <BaseInput
          id="login-password"
          v-model="password"
          type="password"
          icon="lock"
          placeholder="请输入登录密码"
          :error="errors.password"
          password-toggle
          autocomplete="current-password"
        />
        <p v-if="errors.password" class="form-item__error">{{ errors.password }}</p>
      </div>

      <div class="auth__row">
        <BaseCheckbox v-model="remember" label="记住邮箱" />
        <span class="auth__link">没有账号？<router-link to="/register">立即注册</router-link></span>
      </div>

      <BaseButton type="primary" size="large" block :loading="submitting" native-type="submit">
        {{ submitting ? '登录中...' : '登 录' }}
      </BaseButton>

      <p class="auth__tip">登录即表示同意平台服务条款与隐私政策</p>
    </form>
  </AuthLayout>
</template>

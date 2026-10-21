<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import { sendEmailCode } from '@/api/admin/auth'
import AuthLayout from '@/components/auth/AuthLayout.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import FaIcon from '@/components/ui/FaIcon.vue'
import { useCountdown } from '@/composables/useCountdown'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const CODE_COUNTDOWN_SECONDS = 60

const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const name = ref('')
const email = ref('')
const phone = ref('')
const code = ref('')
const password = ref('')
const passwordConfirm = ref('')
const errors = ref<Record<string, string>>({})
const errorMessage = ref('')
const submitting = ref(false)
const sending = ref(false)
/** 验证码重发倒计时（秒），0 表示可重新发送 */
const { remaining: countdown, start: startCountdown } = useCountdown(CODE_COUNTDOWN_SECONDS)

const passwordStrength = computed(() => {
  const value = password.value
  if (!value) return { level: 0, text: '', color: '' }
  let score = 0
  if (value.length >= 8) score += 1
  if (/[a-zA-Z]/.test(value) && /\d/.test(value)) score += 1
  if (/[^a-zA-Z0-9]/.test(value) || value.length >= 12) score += 1
  if (score <= 1) return { level: 1, text: '弱', color: 'var(--app-danger)' }
  if (score === 2) return { level: 2, text: '中', color: 'var(--app-warning)' }
  return { level: 3, text: '强', color: 'var(--app-success)' }
})

function validate(): boolean {
  const next: Record<string, string> = {}
  if (name.value.trim().length < 2) {
    next.name = '姓名至少 2 个字符'
  }
  if (!email.value.trim()) {
    next.email = '请输入邮箱'
  } else if (!EMAIL_PATTERN.test(email.value.trim())) {
    next.email = '邮箱格式不正确'
  }
  if (!/^\d{6}$/.test(code.value.trim())) {
    next.code = '请输入 6 位数字验证码'
  }
  if (password.value.length < 8) {
    next.password = '密码至少 8 位'
  } else if (password.value.length > 72) {
    next.password = '密码长度不能超过 72 字节'
  }
  if (passwordConfirm.value !== password.value) {
    next.passwordConfirm = '两次输入的密码不一致'
  }
  errors.value = next
  return Object.keys(next).length === 0
}

/** 发送邮箱验证码：倒计时由前端负责，服务端不做重发冷却 */
async function onSendCode(): Promise<void> {
  if (countdown.value > 0 || sending.value) return

  const value = email.value.trim()
  if (!EMAIL_PATTERN.test(value)) {
    errors.value = { ...errors.value, email: '请先填写正确的邮箱' }
    return
  }
  errors.value = { ...errors.value, email: '' }

  sending.value = true
  try {
    await sendEmailCode(value, 'register')
    toast.success('验证码已发送，请查收邮件')
    startCountdown()
  } catch (error) {
    toast.error(error instanceof ApiError ? error.message : '验证码发送失败，请稍后再试')
  } finally {
    sending.value = false
  }
}

async function onSubmit(): Promise<void> {
  errorMessage.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    await auth.register({
      name: name.value.trim(),
      email: email.value.trim(),
      phone: phone.value.trim(),
      code: code.value.trim(),
      password: password.value,
      password_confirm: passwordConfirm.value,
    })
    toast.success('注册成功，请使用新账号登录')
    await router.push({ path: '/login', query: { email: email.value.trim() } })
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : '注册失败，请稍后再试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AuthLayout title="账号注册" subtitle="首个注册账号将自动成为超级管理员">
    <form
      class="w-full [--checkbox-bg:rgba(255,255,255,0.15)] [--checkbox-border:rgba(255,255,255,0.5)] [--checkbox-color:rgba(255,255,255,0.85)] [--error-color:#ffd7d7] [--input-bg:#fff] [--input-placeholder:#bbb] [--label-color:rgba(255,255,255,0.85)]"
      novalidate
      @submit.prevent="onSubmit"
    >
      <div
        v-if="errorMessage"
        class="mb-4 flex items-center gap-1.5 rounded-sm bg-[rgba(221,75,57,0.75)] px-3 py-2 text-sm text-[#ffecec]"
      >
        <FaIcon name="exclamation-circle" :size="15" />
        <span>{{ errorMessage }}</span>
      </div>

      <div class="relative mb-5">
        <label
          class="mb-1.5 block text-sm text-[var(--label-color)] before:mr-1 before:text-danger before:content-['*']"
          for="register-name"
          >姓名</label
        >
        <BaseInput
          id="register-name"
          v-model="name"
          icon="user"
          placeholder="请输入姓名"
          :error="errors.name"
          autocomplete="name"
        />
        <p v-if="errors.name" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-[var(--error-color)]">
          {{ errors.name }}
        </p>
      </div>

      <div class="relative mb-5">
        <label
          class="mb-1.5 block text-sm text-[var(--label-color)] before:mr-1 before:text-danger before:content-['*']"
          for="register-email"
          >邮箱</label
        >
        <BaseInput
          id="register-email"
          v-model="email"
          type="email"
          icon="mail"
          placeholder="请输入常用邮箱"
          :error="errors.email"
          autocomplete="email"
        />
        <p v-if="errors.email" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-[var(--error-color)]">
          {{ errors.email }}
        </p>
      </div>

      <div class="relative mb-5">
        <label class="mb-1.5 block text-sm text-[var(--label-color)]" for="register-phone">手机号</label>
        <BaseInput
          id="register-phone"
          v-model="phone"
          icon="user"
          placeholder="用于日常联系，可留空"
          autocomplete="tel"
        />
      </div>

      <div class="relative mb-5">
        <label
          class="mb-1.5 block text-sm text-[var(--label-color)] before:mr-1 before:text-danger before:content-['*']"
          for="register-code"
          >邮箱验证码</label
        >
        <div class="flex gap-2.5">
          <BaseInput
            id="register-code"
            v-model="code"
            icon="key"
            placeholder="6 位数字验证码"
            :error="errors.code"
            autocomplete="one-time-code"
            class="flex-1"
          />
          <BaseButton
            class="w-[120px] shrink-0"
            :disabled="countdown > 0"
            :loading="sending"
            type="primary"
            native-type="button"
            @click="onSendCode"
          >
            {{ countdown > 0 ? `${countdown}s 后重发` : '获取验证码' }}
          </BaseButton>
        </div>
        <p v-if="errors.code" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-[var(--error-color)]">
          {{ errors.code }}
        </p>
      </div>

      <div class="relative mb-5">
        <label
          class="mb-1.5 block text-sm text-[var(--label-color)] before:mr-1 before:text-danger before:content-['*']"
          for="register-password"
          >密码</label
        >
        <BaseInput
          id="register-password"
          v-model="password"
          type="password"
          icon="lock"
          placeholder="8-72 位，建议字母 + 数字 + 符号"
          :error="errors.password"
          password-toggle
          autocomplete="new-password"
        />
        <p v-if="errors.password" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-[var(--error-color)]">
          {{ errors.password }}
        </p>
        <p v-else-if="passwordStrength.level" class="mt-1.5 text-xs text-[var(--tip-color)]">
          密码强度：<span :style="{ color: passwordStrength.color }">{{ passwordStrength.text }}</span>
        </p>
      </div>

      <div class="relative mb-5">
        <label
          class="mb-1.5 block text-sm text-[var(--label-color)] before:mr-1 before:text-danger before:content-['*']"
          for="register-password-confirm"
          >确认密码</label
        >
        <BaseInput
          id="register-password-confirm"
          v-model="passwordConfirm"
          type="password"
          icon="lock"
          placeholder="请再次输入密码"
          :error="errors.passwordConfirm"
          password-toggle
          autocomplete="new-password"
        />
        <p v-if="errors.passwordConfirm" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-[var(--error-color)]">
          {{ errors.passwordConfirm }}
        </p>
      </div>

      <BaseButton type="primary" size="large" block :loading="submitting" native-type="submit">
        {{ submitting ? '注册中...' : '注 册' }}
      </BaseButton>

      <p class="mt-[18px] text-center text-sm text-white/85">
        已有账号？<router-link class="text-white" to="/login">返回登录</router-link>
      </p>
    </form>
  </AuthLayout>
</template>

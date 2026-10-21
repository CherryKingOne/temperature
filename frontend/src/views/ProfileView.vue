<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import { changePassword, sendEmailCode } from '@/api/admin/auth'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import FaIcon from '@/components/ui/FaIcon.vue'
import { useCountdown } from '@/composables/useCountdown'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { formatDateTime } from '@/utils/datetime'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const code = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const errors = ref<Record<string, string>>({})
const submitting = ref(false)
const sending = ref(false)
/** 账号信息加载状态 */
const loading = ref(false)
const loadError = ref('')
const { remaining, start } = useCountdown(60)

/** 头像文字：取姓名首字 */
const avatarText = computed(() => (auth.admin?.name ?? 'A').charAt(0))

const roleText = computed(() => (auth.isSuperAdmin ? '超级管理员' : '管理员'))

const statusText = computed(() => (auth.admin?.status === 'ACTIVE' ? '正常' : '已禁用'))

onMounted(async () => {
  if (auth.admin) return
  await onReload()
})

/** 加载账号信息（接口：GET /api/admin/auth/me） */
async function onReload(): Promise<void> {
  loadError.value = ''
  loading.value = true
  try {
    await auth.loadCurrentAdmin()
  } catch (error) {
    loadError.value = error instanceof ApiError ? error.message : '账号信息加载失败'
  } finally {
    loading.value = false
  }
}

function validate(): boolean {
  const next: Record<string, string> = {}
  if (!/^\d{6}$/.test(code.value.trim())) {
    next.code = '请输入 6 位数字验证码'
  }
  if (!oldPassword.value) {
    next.oldPassword = '请输入当前密码'
  }
  if (newPassword.value.length < 8) {
    next.newPassword = '新密码至少 8 位'
  } else if (newPassword.value.length > 72) {
    next.newPassword = '密码长度不能超过 72 字节'
  }
  if (newPassword.value && newPassword.value === oldPassword.value) {
    next.newPassword = '新密码不能与原密码相同'
  }
  if (confirmPassword.value !== newPassword.value) {
    next.newPassword = '两次输入的新密码不一致'
  }
  errors.value = next
  return Object.keys(next).length === 0
}

/** 发送邮箱验证码：验证码发送到当前账号邮箱，倒计时由前端负责 */
async function onSendCode(): Promise<void> {
  if (remaining.value > 0 || sending.value) return

  const email = auth.admin?.email
  if (!email) {
    toast.error('未获取到当前账号邮箱，请稍后再试')
    return
  }

  sending.value = true
  try {
    await sendEmailCode(email, 'reset_password')
    toast.success('验证码已发送，请查收邮件')
    start()
  } catch (error) {
    toast.error(error instanceof ApiError ? error.message : '验证码发送失败，请稍后再试')
  } finally {
    sending.value = false
  }
}

async function onSubmit(): Promise<void> {
  if (!validate()) return

  submitting.value = true
  try {
    await changePassword({
      code: code.value.trim(),
      old_password: oldPassword.value,
      password: newPassword.value,
      password_confirm: confirmPassword.value,
    })
    toast.success('密码修改成功，请重新登录')
    await auth.logout()
    await router.push('/login')
  } catch (error) {
    toast.error(error instanceof ApiError ? error.message : '密码修改失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}

// ------------------------------------------------------------------
// 行内编辑（姓名 / 手机号 各自独立）
// ------------------------------------------------------------------
type EditField = 'name' | 'phone'

const editingField = ref<EditField | null>(null)
const editValue = ref('')
const editError = ref('')
const editSaving = ref(false)

function startEdit(field: EditField): void {
  editingField.value = field
  editValue.value = field === 'name' ? (auth.admin?.name ?? '') : (auth.admin?.phone ?? '')
  editError.value = ''
}

function cancelEdit(): void {
  editingField.value = null
  editValue.value = ''
  editError.value = ''
}

async function saveEdit(): Promise<void> {
  const field = editingField.value
  if (!field) return

  const name = field === 'name' ? editValue.value.trim() : (auth.admin?.name ?? '')
  const phone = field === 'phone' ? editValue.value.trim() : (auth.admin?.phone ?? '')
  if (field === 'name' && name.length < 2) {
    editError.value = '姓名至少 2 个字符'
    return
  }
  if (field === 'phone' && phone.length > 20) {
    editError.value = '手机号最长 20 个字符'
    return
  }

  editSaving.value = true
  try {
    await auth.updateProfile({ name, phone })
    toast.success(field === 'name' ? '姓名已更新' : '手机号已更新')
    cancelEdit()
  } catch (error) {
    editError.value = error instanceof ApiError ? error.message : '保存失败，请稍后再试'
  } finally {
    editSaving.value = false
  }
}
</script>

<template>
  <div class="flex items-start gap-[15px] max-[900px]:flex-col">
    <!-- 加载中 / 加载失败 -->
    <div v-if="loading" class="w-full rounded border border-border bg-surface shadow-card">
      <div class="flex items-center justify-center gap-2.5 p-[15px]">
        <span
          class="inline-block h-3.5 w-3.5 animate-spinner rounded-full border-2 border-current border-t-transparent"
        />
        <span class="text-sm text-text-secondary">正在加载账号信息...</span>
      </div>
    </div>

    <div v-else-if="loadError" class="w-full rounded border border-border bg-surface shadow-card">
      <div class="flex items-center justify-center gap-2.5 p-[15px]">
        <FaIcon name="exclamation-circle" :size="15" />
        <span class="text-sm text-danger">{{ loadError }}</span>
        <BaseButton size="small" @click="onReload">重新加载</BaseButton>
      </div>
    </div>

    <template v-else>
      <!-- 左侧：个人名片 -->
      <aside class="w-[280px] shrink-0 max-[900px]:w-full">
        <div class="rounded border border-border bg-surface shadow-card">
          <div class="flex flex-col items-center p-[15px] text-center">
            <span
              class="mb-3 inline-flex h-16 w-16 items-center justify-center rounded-full bg-primary text-[26px] text-white"
              >{{ avatarText }}</span
            >
            <p class="text-lg font-medium">{{ auth.admin?.name ?? '加载中...' }}</p>
            <p class="mx-0 my-1 mb-2.5 break-all text-sm text-text-secondary">
              {{ auth.admin?.email ?? '-' }}
            </p>
            <p v-if="auth.admin?.phone" class="mx-0 my-1 mb-2.5 break-all text-sm text-text-secondary">
              {{ auth.admin.phone }}
            </p>
            <span
              class="rounded-[2px] px-2.5 py-0.5 text-xs"
              :class="
                auth.isSuperAdmin
                  ? 'bg-[rgba(243,156,18,0.14)] text-warning'
                  : 'bg-primary-light text-primary'
              "
              >{{ roleText }}</span
            >
          </div>
        </div>

        <div class="mt-[15px] rounded border border-border bg-surface shadow-card">
          <div
            class="flex h-[41px] items-center justify-between border-b border-border-lighter bg-card-header-bg px-[15px] text-base"
          >
            <span>账号概况</span>
          </div>
          <ul class="px-[15px] pt-1.5 pb-3.5">
            <li
              class="flex items-center justify-between gap-2.5 border-b border-dashed border-border-lighter py-1.5 text-sm last:border-b-0"
            >
              <span class="whitespace-nowrap text-text-secondary">账号状态</span>
              <span
                class="text-right break-all"
                :class="{ 'text-success': auth.admin?.status === 'ACTIVE' }"
              >
                {{ statusText }}
              </span>
            </li>
            <li
              class="flex items-center justify-between gap-2.5 border-b border-dashed border-border-lighter py-1.5 text-sm last:border-b-0"
            >
              <span class="whitespace-nowrap text-text-secondary">账号 ID</span>
              <span class="text-right break-all">{{ auth.admin?.id ?? '-' }}</span>
            </li>
            <li
              class="flex items-center justify-between gap-2.5 border-b border-dashed border-border-lighter py-1.5 text-sm last:border-b-0"
            >
              <span class="whitespace-nowrap text-text-secondary">注册时间</span>
              <span class="text-right break-all">{{ formatDateTime(auth.admin?.created_at) }}</span>
            </li>
            <li
              class="flex items-center justify-between gap-2.5 border-b border-dashed border-border-lighter py-1.5 text-sm last:border-b-0"
            >
              <span class="whitespace-nowrap text-text-secondary">最近登录</span>
              <span class="text-right break-all">{{ formatDateTime(auth.admin?.last_login_at) }}</span>
            </li>
          </ul>
        </div>
      </aside>

      <!-- 右侧：账号信息 + 安全设置 -->
      <section class="min-w-0 flex-1">
        <div class="rounded border border-border bg-surface shadow-card">
          <div
            class="flex h-[41px] items-center justify-between border-b border-border-lighter bg-card-header-bg px-[15px] text-base"
          >
            <span>账号信息</span>
            <span class="text-xs text-text-placeholder">数据来自服务端，仅本人可见</span>
          </div>
          <div class="p-[15px]">
            <table
              class="w-full text-sm text-text [&_th]:w-[110px] [&_th]:border-b [&_th]:border-border-lighter [&_th]:px-2 [&_th]:py-2 [&_th]:text-left [&_th]:font-normal [&_th]:text-text-secondary [&_td]:border-b [&_td]:border-border-lighter [&_td]:px-2 [&_td]:py-2 [&>tbody>tr>td:hover]:bg-hover"
            >
              <tbody>
                <tr>
                  <th>
                    姓名
                  </th>
                  <td>
                    <span v-if="editingField !== 'name'" class="inline-flex items-center gap-1.5">
                      {{ auth.admin?.name ?? '-' }}
                      <button
                        class="inline-flex h-5 w-5 cursor-pointer items-center justify-center rounded-sm text-text-placeholder transition-all duration-300 ease hover:bg-primary-light hover:text-primary"
                        title="编辑姓名"
                        @click="startEdit('name')"
                      >
                        <FaIcon name="edit" :size="13" />
                      </button>
                    </span>
                    <span v-else class="inline-flex items-center gap-1.5">
                      <BaseInput
                        v-model="editValue"
                        class="w-[180px]"
                        :error="editError"
                        @keyup.enter="saveEdit"
                        @keyup.esc="cancelEdit"
                      />
                      <button
                        class="inline-flex h-6 w-6 cursor-pointer items-center justify-center rounded-sm text-text-secondary transition-all duration-300 ease hover:bg-primary-light hover:text-primary disabled:cursor-not-allowed disabled:bg-transparent disabled:text-disabled-text"
                        title="保存"
                        :disabled="editSaving"
                        @click="saveEdit"
                      >
                        <FaIcon name="check" :size="13" />
                      </button>
                      <button
                        class="inline-flex h-6 w-6 cursor-pointer items-center justify-center rounded-sm text-text-secondary transition-all duration-300 ease hover:bg-primary-light hover:text-primary"
                        title="取消"
                        @click="cancelEdit"
                      >
                        <FaIcon name="times" :size="13" />
                      </button>
                    </span>
                  </td>
                  <th>
                    登录邮箱
                  </th>
                  <td>{{ auth.admin?.email ?? '-' }}</td>
                </tr>
                <tr>
                  <th>
                    手机号
                  </th>
                  <td>
                    <span v-if="editingField !== 'phone'" class="inline-flex items-center gap-1.5">
                      <span v-if="auth.admin?.phone">{{ auth.admin.phone }}</span>
                      <span v-else class="text-text-placeholder">未填写</span>
                      <button
                        class="inline-flex h-5 w-5 cursor-pointer items-center justify-center rounded-sm text-text-placeholder transition-all duration-300 ease hover:bg-primary-light hover:text-primary"
                        title="编辑手机号"
                        @click="startEdit('phone')"
                      >
                        <FaIcon name="edit" :size="13" />
                      </button>
                    </span>
                    <span v-else class="inline-flex items-center gap-1.5">
                      <BaseInput
                        v-model="editValue"
                        class="w-[180px]"
                        placeholder="请输入手机号"
                        :error="editError"
                        @keyup.enter="saveEdit"
                        @keyup.esc="cancelEdit"
                      />
                      <button
                        class="inline-flex h-6 w-6 cursor-pointer items-center justify-center rounded-sm text-text-secondary transition-all duration-300 ease hover:bg-primary-light hover:text-primary disabled:cursor-not-allowed disabled:bg-transparent disabled:text-disabled-text"
                        title="保存"
                        :disabled="editSaving"
                        @click="saveEdit"
                      >
                        <FaIcon name="check" :size="13" />
                      </button>
                      <button
                        class="inline-flex h-6 w-6 cursor-pointer items-center justify-center rounded-sm text-text-secondary transition-all duration-300 ease hover:bg-primary-light hover:text-primary"
                        title="取消"
                        @click="cancelEdit"
                      >
                        <FaIcon name="times" :size="13" />
                      </button>
                    </span>
                  </td>
                  <th>
                    角色
                  </th>
                  <td>{{ roleText }}</td>
                </tr>
                <tr>
                  <th>
                    账号状态
                  </th>
                  <td>{{ statusText }}</td>
                  <th>
                    账号 ID
                  </th>
                  <td>{{ auth.admin?.id ?? '-' }}</td>
                </tr>
                <tr>
                  <th>
                    创建时间
                  </th>
                  <td>
                    {{ formatDateTime(auth.admin?.created_at) }}
                  </td>
                  <th>
                    最近登录时间
                  </th>
                  <td>
                    {{ formatDateTime(auth.admin?.last_login_at) }}
                  </td>
                </tr>
                <tr>
                  <th>
                    最近登录 IP
                  </th>
                  <td>
                    {{ auth.admin?.last_login_ip ?? '-' }}
                  </td>
                  <th></th>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="mt-[15px] rounded border border-border bg-surface shadow-card">
          <div
            class="flex h-[41px] items-center justify-between border-b border-border-lighter bg-card-header-bg px-[15px] text-base"
          >
            <span>安全设置</span>
          </div>
          <div class="p-[15px]">
            <p
              class="mb-[15px] flex items-center gap-1.5 rounded-sm bg-surface-alt px-3 py-2 text-xs text-text-secondary"
            >
              <FaIcon name="exclamation-circle" :size="14" />
              修改密码需要邮箱验证码与当前密码，修改成功后当前账号的全部登录会话都会失效，需要重新登录。
            </p>

            <form class="w-full max-w-[720px]" novalidate @submit.prevent="onSubmit">
              <div class="flex gap-5 max-[900px]:flex-col max-[900px]:gap-0">
                <div class="relative flex-1">
                  <label
                    class="mb-1.5 block text-sm text-text-secondary before:mr-1 before:text-danger before:content-['*']"
                    for="change-code"
                    >邮箱验证码</label
                  >
                  <div class="flex gap-2.5">
                    <BaseInput
                      id="change-code"
                      v-model="code"
                      icon="key"
                      placeholder="6 位数字验证码"
                      :error="errors.code"
                      autocomplete="one-time-code"
                      class="flex-1"
                    />
                    <BaseButton
                      class="w-[120px] shrink-0"
                      :disabled="remaining > 0"
                      :loading="sending"
                      type="primary"
                      native-type="button"
                      @click="onSendCode"
                    >
                      {{ remaining > 0 ? `${remaining}s 后重发` : '获取验证码' }}
                    </BaseButton>
                  </div>
                  <p v-if="errors.code" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-danger">
                    {{ errors.code }}
                  </p>
                  <p class="mt-1.5 text-xs text-text-placeholder">
                    验证码将发送到账号邮箱 {{ auth.admin?.email ?? '-' }}
                  </p>
                </div>
              </div>

              <div class="flex gap-5 max-[900px]:flex-col max-[900px]:gap-0">
                <div class="relative flex-1">
                  <label
                    class="mb-1.5 block text-sm text-text-secondary before:mr-1 before:text-danger before:content-['*']"
                    for="old-password"
                    >当前密码</label
                  >
                  <BaseInput
                    id="old-password"
                    v-model="oldPassword"
                    type="password"
                    icon="lock"
                    placeholder="请输入当前密码"
                    :error="errors.oldPassword"
                    password-toggle
                    autocomplete="current-password"
                  />
                  <p v-if="errors.oldPassword" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-danger">
                    {{ errors.oldPassword }}
                  </p>
                </div>
              </div>

              <div class="flex gap-5 max-[900px]:flex-col max-[900px]:gap-0">
                <div class="relative flex-1">
                  <label
                    class="mb-1.5 block text-sm text-text-secondary before:mr-1 before:text-danger before:content-['*']"
                    for="new-password"
                    >新密码</label
                  >
                  <BaseInput
                    id="new-password"
                    v-model="newPassword"
                    type="password"
                    icon="lock"
                    placeholder="8-72 位，建议字母 + 数字 + 符号"
                    :error="errors.newPassword"
                    password-toggle
                    autocomplete="new-password"
                  />
                  <p v-if="errors.newPassword" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-danger">
                    {{ errors.newPassword }}
                  </p>
                </div>

                <div class="relative flex-1">
                  <label
                    class="mb-1.5 block text-sm text-text-secondary before:mr-1 before:text-danger before:content-['*']"
                    for="confirm-password"
                    >确认新密码</label
                  >
                  <BaseInput
                    id="confirm-password"
                    v-model="confirmPassword"
                    type="password"
                    icon="lock"
                    placeholder="请再次输入新密码"
                    :error="errors.confirmPassword"
                    password-toggle
                    autocomplete="new-password"
                  />
                  <p v-if="errors.confirmPassword" class="absolute top-full right-0 mt-0.5 text-xs leading-[1.4] text-danger">
                    {{ errors.confirmPassword }}
                  </p>
                </div>
              </div>

              <BaseButton type="primary" :loading="submitting" native-type="submit"
                >保存新密码</BaseButton
              >
            </form>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

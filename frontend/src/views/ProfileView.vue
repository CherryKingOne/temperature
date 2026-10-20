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
    next.confirmPassword = '两次输入的新密码不一致'
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
  <div class="profile">
    <!-- 加载中 / 加载失败 -->
    <div v-if="loading" class="card profile__state">
      <div class="card__body flex-center gap10">
        <span class="spinner" />
        <span class="text-secondary text-sm">正在加载账号信息...</span>
      </div>
    </div>

    <div v-else-if="loadError" class="card profile__state">
      <div class="card__body flex-center gap10">
        <FaIcon name="exclamation-circle" :size="15" />
        <span class="text-danger text-sm">{{ loadError }}</span>
        <BaseButton size="small" @click="onReload">重新加载</BaseButton>
      </div>
    </div>

    <template v-else>
      <!-- 左侧：个人名片 -->
      <aside class="profile__side">
        <div class="card">
          <div class="card__body profile__card">
            <span class="profile__avatar">{{ avatarText }}</span>
            <p class="profile__name">{{ auth.admin?.name ?? '加载中...' }}</p>
            <p class="profile__email">{{ auth.admin?.email ?? '-' }}</p>
            <p v-if="auth.admin?.phone" class="profile__email">{{ auth.admin.phone }}</p>
            <span class="profile__role" :class="{ 'is-super': auth.isSuperAdmin }">{{
              roleText
            }}</span>
          </div>
        </div>

        <div class="card mt15">
          <div class="card__header"><span>账号概况</span></div>
          <ul class="profile__summary">
            <li class="profile__summary-item">
              <span class="profile__summary-label">账号状态</span>
              <span
                class="profile__summary-value"
                :class="{ 'text-success': auth.admin?.status === 'ACTIVE' }"
              >
                {{ statusText }}
              </span>
            </li>
            <li class="profile__summary-item">
              <span class="profile__summary-label">账号 ID</span>
              <span class="profile__summary-value">{{ auth.admin?.id ?? '-' }}</span>
            </li>
            <li class="profile__summary-item">
              <span class="profile__summary-label">注册时间</span>
              <span class="profile__summary-value">{{
                formatDateTime(auth.admin?.created_at)
              }}</span>
            </li>
            <li class="profile__summary-item">
              <span class="profile__summary-label">最近登录</span>
              <span class="profile__summary-value">{{
                formatDateTime(auth.admin?.last_login_at)
              }}</span>
            </li>
          </ul>
        </div>
      </aside>

      <!-- 右侧：账号信息 + 安全设置 -->
      <section class="profile__main">
        <div class="card">
          <div class="card__header">
            <span>账号信息</span>
            <span class="text-xs text-placeholder">数据来自服务端，仅本人可见</span>
          </div>
          <div class="card__body">
            <table class="table profile__table">
              <tbody>
                <tr>
                  <th class="profile__table-label">姓名</th>
                  <td>
                    <span v-if="editingField !== 'name'" class="profile__value">
                      {{ auth.admin?.name ?? '-' }}
                      <button class="profile__edit" title="编辑姓名" @click="startEdit('name')">
                        <FaIcon name="edit" :size="13" />
                      </button>
                    </span>
                    <span v-else class="profile__edit-box">
                      <BaseInput
                        v-model="editValue"
                        class="profile__edit-input"
                        :error="editError"
                        @keyup.enter="saveEdit"
                        @keyup.esc="cancelEdit"
                      />
                      <button
                        class="profile__edit-action"
                        title="保存"
                        :disabled="editSaving"
                        @click="saveEdit"
                      >
                        <FaIcon name="check" :size="13" />
                      </button>
                      <button class="profile__edit-action" title="取消" @click="cancelEdit">
                        <FaIcon name="times" :size="13" />
                      </button>
                    </span>
                  </td>
                  <th class="profile__table-label">登录邮箱</th>
                  <td>{{ auth.admin?.email ?? '-' }}</td>
                </tr>
                <tr>
                  <th class="profile__table-label">手机号</th>
                  <td>
                    <span v-if="editingField !== 'phone'" class="profile__value">
                      <span v-if="auth.admin?.phone">{{ auth.admin.phone }}</span>
                      <span v-else class="text-placeholder">未填写</span>
                      <button class="profile__edit" title="编辑手机号" @click="startEdit('phone')">
                        <FaIcon name="edit" :size="13" />
                      </button>
                    </span>
                    <span v-else class="profile__edit-box">
                      <BaseInput
                        v-model="editValue"
                        class="profile__edit-input"
                        placeholder="请输入手机号"
                        :error="editError"
                        @keyup.enter="saveEdit"
                        @keyup.esc="cancelEdit"
                      />
                      <button
                        class="profile__edit-action"
                        title="保存"
                        :disabled="editSaving"
                        @click="saveEdit"
                      >
                        <FaIcon name="check" :size="13" />
                      </button>
                      <button class="profile__edit-action" title="取消" @click="cancelEdit">
                        <FaIcon name="times" :size="13" />
                      </button>
                    </span>
                  </td>
                  <th class="profile__table-label">角色</th>
                  <td>{{ roleText }}</td>
                </tr>
                <tr>
                  <th class="profile__table-label">账号状态</th>
                  <td>{{ statusText }}</td>
                  <th class="profile__table-label">账号 ID</th>
                  <td>{{ auth.admin?.id ?? '-' }}</td>
                </tr>
                <tr>
                  <th class="profile__table-label">创建时间</th>
                  <td>{{ formatDateTime(auth.admin?.created_at) }}</td>
                  <th class="profile__table-label">最近登录时间</th>
                  <td>{{ formatDateTime(auth.admin?.last_login_at) }}</td>
                </tr>
                <tr>
                  <th class="profile__table-label">最近登录 IP</th>
                  <td>{{ auth.admin?.last_login_ip ?? '-' }}</td>
                  <th class="profile__table-label"></th>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card mt15">
          <div class="card__header"><span>安全设置</span></div>
          <div class="card__body">
            <p class="profile__tip">
              <FaIcon name="exclamation-circle" :size="14" />
              修改密码需要邮箱验证码与当前密码，修改成功后当前账号的全部登录会话都会失效，需要重新登录。
            </p>

            <form class="form profile__form" novalidate @submit.prevent="onSubmit">
              <div class="profile__form-row">
                <div class="form-item">
                  <label class="form-item__label form-item__label--required" for="change-code"
                    >邮箱验证码</label
                  >
                  <div class="profile__code">
                    <BaseInput
                      id="change-code"
                      v-model="code"
                      icon="key"
                      placeholder="6 位数字验证码"
                      :error="errors.code"
                      autocomplete="one-time-code"
                    />
                    <BaseButton
                      :disabled="remaining > 0"
                      :loading="sending"
                      type="primary"
                      native-type="button"
                      @click="onSendCode"
                    >
                      {{ remaining > 0 ? `${remaining}s 后重发` : '获取验证码' }}
                    </BaseButton>
                  </div>
                  <p v-if="errors.code" class="form-item__error">{{ errors.code }}</p>
                  <p class="form-item__tip">
                    验证码将发送到账号邮箱 {{ auth.admin?.email ?? '-' }}
                  </p>
                </div>
              </div>

              <div class="profile__form-row">
                <div class="form-item">
                  <label class="form-item__label form-item__label--required" for="old-password"
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
                  <p v-if="errors.oldPassword" class="form-item__error">{{ errors.oldPassword }}</p>
                </div>
              </div>

              <div class="profile__form-row">
                <div class="form-item">
                  <label class="form-item__label form-item__label--required" for="new-password"
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
                  <p v-if="errors.newPassword" class="form-item__error">{{ errors.newPassword }}</p>
                </div>

                <div class="form-item">
                  <label class="form-item__label form-item__label--required" for="confirm-password"
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
                  <p v-if="errors.confirmPassword" class="form-item__error">
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

<style scoped>
.profile {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.profile__side {
  width: 280px;
  flex-shrink: 0;
}

.profile__state {
  width: 100%;
}

.profile__main {
  flex: 1;
  min-width: 0;
}

.profile__card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.profile__avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin-bottom: 12px;
  font-size: 26px;
  color: #fff;
  background-color: var(--color-primary);
  border-radius: 50%;
}

.profile__name {
  font-size: 16px;
  font-weight: 500;
}

.profile__email {
  margin: 4px 0 10px;
  font-size: 13px;
  color: var(--color-text-secondary);
  word-break: break-all;
}

.profile__role {
  padding: 2px 10px;
  font-size: 12px;
  color: var(--color-primary);
  background-color: var(--color-primary-light);
  border-radius: 2px;
}

.profile__role.is-super {
  color: var(--color-warning);
  background-color: rgba(243, 156, 18, 0.14);
}

.profile__summary {
  padding: 6px 15px 14px;
}

.profile__summary-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 7px 0;
  font-size: 13px;
  border-bottom: 1px dashed var(--color-border-lighter);
}

.profile__summary-item:last-child {
  border-bottom: none;
}

.profile__summary-label {
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.profile__summary-value {
  text-align: right;
  word-break: break-all;
}

.profile__table th.profile__table-label {
  width: 110px;
  font-weight: normal;
  color: var(--color-text-secondary);
  background-color: transparent;
  border-bottom: 1px solid var(--color-border-lighter);
}

.profile__phone {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

/* 行内编辑铅笔图标 */
.profile__value {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.profile__edit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  color: var(--color-text-placeholder);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition:
    color var(--transition),
    background-color var(--transition);
}

.profile__edit:hover {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

/* 行内编辑：输入框 + 保存 / 取消 */
.profile__edit-box {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.profile__edit-input {
  width: 180px;
}

.profile__edit-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition:
    color var(--transition),
    background-color var(--transition);
}

.profile__edit-action:hover {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.profile__edit-action[disabled] {
  color: var(--color-disabled-text);
  cursor: not-allowed;
  background-color: transparent;
}

.profile__tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 15px;
  padding: 8px 12px;
  font-size: 12px;
  color: var(--color-text-secondary);
  background-color: var(--color-surface-alt);
  border-radius: var(--radius-sm);
}

.profile__form {
  max-width: 720px;
}

.profile__code {
  display: flex;
  gap: 10px;
}

.profile__code .input-group {
  flex: 1;
}

.profile__code .btn {
  flex-shrink: 0;
  width: 120px;
}

.profile__form-row {
  display: flex;
  gap: 20px;
}

.profile__form-row .form-item {
  flex: 1;
}

@media (max-width: 900px) {
  .profile {
    flex-direction: column;
  }

  .profile__side {
    width: 100%;
  }

  .profile__form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>

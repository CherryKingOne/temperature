<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createPersonnel,
  employmentTypes,
  listPersonnel,
  personnelSummary,
  removePersonnel,
  setPersonnelStatus,
  updatePersonnel,
} from '@/api/admin/personnel'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BasePagination from '@/components/ui/BasePagination.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseTag from '@/components/ui/BaseTag.vue'
import FaIcon from '@/components/ui/FaIcon.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import {
  EMPLOYMENT_LABELS,
  ROLE_LABELS,
  STATUS_LABELS,
  type AdminRole,
  type EmploymentType,
  type Personnel,
  type PersonnelStatus,
} from '@/types/personnel'
import { formatDateTime } from '@/utils/datetime'

const auth = useAuthStore()
const toast = useToastStore()

/** 是否超级管理员：可新增人员、分配角色与权限 */
const isSuperAdmin = computed(() => auth.isSuperAdmin)

const ROLE_OPTIONS = [
  { label: ROLE_LABELS.SUPER_ADMIN, value: 'SUPER_ADMIN' },
  { label: ROLE_LABELS.ADMIN, value: 'ADMIN' },
  { label: ROLE_LABELS.MEMBER, value: 'MEMBER' },
]

const EMPLOYMENT_OPTIONS = employmentTypes().map((value) => ({
  label: EMPLOYMENT_LABELS[value],
  value,
}))

const STATUS_OPTIONS = [
  { label: STATUS_LABELS.ACTIVE, value: 'ACTIVE' },
  { label: STATUS_LABELS.DISABLED, value: 'DISABLED' },
]

/** 示例权限项（权限体系设计完成后替换为后端菜单 / 操作权限） */
const PERMISSIONS = [
  { key: 'admin:view', label: '人员管理（查看）' },
  { key: 'admin:create', label: '人员管理（新增）' },
  { key: 'admin:update', label: '人员管理（编辑）' },
  { key: 'admin:status', label: '人员管理（启用/禁用）' },
  { key: 'admin:role', label: '人员管理（分配角色）' },
  { key: 'admin:delete', label: '人员管理（删除）' },
  { key: 'menu:manage', label: '菜单与权限管理' },
  { key: 'log:view', label: '操作日志查看' },
]

// ------------------------------------------------------------------
// 列表
// ------------------------------------------------------------------
const filters = reactive<{
  keyword: string
  role: string
  employment_type: string
  status: string
}>({
  keyword: '',
  role: '',
  employment_type: '',
  status: '',
})

const page = ref(1)
const pageSize = ref(10)
const list = ref<Personnel[]>([])
const total = ref(0)
const loading = ref(false)

const summary = ref({
  total: 0,
  full_time: 0,
  outsource: 0,
  part_time: 0,
  active: 0,
})

async function load(): Promise<void> {
  loading.value = true
  try {
    const result = await listPersonnel({
      keyword: filters.keyword,
      role: filters.role as AdminRole | '',
      employment_type: filters.employment_type as EmploymentType | '',
      status: filters.status as PersonnelStatus | '',
      page: page.value,
      page_size: pageSize.value,
    })
    list.value = result.items
    total.value = result.total
  } catch {
    toast.error('加载人员列表失败')
  } finally {
    loading.value = false
  }
}

async function loadSummary(): Promise<void> {
  summary.value = await personnelSummary()
}

onMounted(async () => {
  await Promise.all([load(), loadSummary()])
})

function onSearch(): void {
  page.value = 1
  void load()
}

function onReset(): void {
  filters.keyword = ''
  filters.role = ''
  filters.employment_type = ''
  filters.status = ''
  page.value = 1
  void load()
}

function onRefresh(): void {
  void Promise.all([load(), loadSummary()])
  toast.info('已刷新')
}

// ------------------------------------------------------------------
// 新增 / 编辑
// ------------------------------------------------------------------
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const form = reactive({
  id: '',
  name: '',
  email: '',
  phone: '',
  employment_type: 'FULL_TIME',
  role: 'MEMBER',
  status: 'ACTIVE',
  password: '',
})

function openCreate(): void {
  dialogMode.value = 'create'
  Object.assign(form, {
    id: '',
    name: '',
    email: '',
    phone: '',
    employment_type: 'FULL_TIME',
    role: 'MEMBER',
    status: 'ACTIVE',
    password: '',
  })
  dialogVisible.value = true
}

function openEdit(item: Personnel): void {
  dialogMode.value = 'edit'
  Object.assign(form, {
    id: item.id,
    name: item.name,
    email: item.email,
    phone: item.phone ?? '',
    employment_type: item.employment_type,
    role: item.role,
    status: item.status,
    password: '',
  })
  dialogVisible.value = true
}

async function onSubmit(): Promise<void> {
  if (!form.name.trim() || !form.email.trim()) {
    toast.warning('请填写姓名与邮箱')
    return
  }
  if (dialogMode.value === 'create' && form.password.length < 8) {
    toast.warning('初始密码至少 8 位')
    return
  }

  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createPersonnel({
        name: form.name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
        role: form.role as AdminRole,
        employment_type: form.employment_type as EmploymentType,
        status: form.status as PersonnelStatus,
        password: form.password,
      })
      toast.success('人员已添加')
    } else {
      await updatePersonnel(form.id, {
        name: form.name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
        role: form.role as AdminRole,
        employment_type: form.employment_type as EmploymentType,
        status: form.status as PersonnelStatus,
      })
      toast.success('人员信息已更新')
    }
    dialogVisible.value = false
    await Promise.all([load(), loadSummary()])
  } catch {
    toast.error('保存失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}

// ------------------------------------------------------------------
// 启用 / 禁用 / 删除
// ------------------------------------------------------------------
async function onToggleStatus(item: Personnel): Promise<void> {
  const next: PersonnelStatus = item.status === 'ACTIVE' ? 'DISABLED' : 'ACTIVE'
  await setPersonnelStatus(item.id, next)
  toast.success(next === 'ACTIVE' ? '已启用' : '已禁用')
  await Promise.all([load(), loadSummary()])
}

async function onRemove(item: Personnel): Promise<void> {
  if (!window.confirm(`确认删除「${item.name}」？该操作不可恢复。`)) return
  await removePersonnel(item.id)
  toast.success('已删除')
  await Promise.all([load(), loadSummary()])
}

// ------------------------------------------------------------------
// 分配角色与权限（仅超级管理员）
// ------------------------------------------------------------------
const permissionVisible = ref(false)
const permissionTarget = ref<Personnel | null>(null)
const permissionRole = ref<AdminRole>('MEMBER')
const permissionChecked = ref<string[]>([])

function openPermission(item: Personnel): void {
  permissionTarget.value = item
  permissionRole.value = item.role
  permissionChecked.value = ['admin:view']
  permissionVisible.value = true
}

async function onSavePermission(): Promise<void> {
  permissionVisible.value = false
  toast.success('权限已更新')
}
</script>

<template>
  <div class="personnel">
    <!-- 概览 -->
    <div class="personnel__stats">
      <div class="card personnel__stat">
        <div class="card__body">
          <p class="personnel__stat-value">{{ summary.total }}</p>
          <p class="personnel__stat-label">人员总数</p>
        </div>
      </div>
      <div class="card personnel__stat">
        <div class="card__body">
          <p class="personnel__stat-value text-success">{{ summary.full_time }}</p>
          <p class="personnel__stat-label">正式员工</p>
        </div>
      </div>
      <div class="card personnel__stat">
        <div class="card__body">
          <p class="personnel__stat-value text-warning">{{ summary.outsource }}</p>
          <p class="personnel__stat-label">外包</p>
        </div>
      </div>
      <div class="card personnel__stat">
        <div class="card__body">
          <p class="personnel__stat-value text-primary">{{ summary.part_time }}</p>
          <p class="personnel__stat-label">兼职</p>
        </div>
      </div>
      <div class="card personnel__stat">
        <div class="card__body">
          <p class="personnel__stat-value">{{ summary.active }}</p>
          <p class="personnel__stat-label">启用中</p>
        </div>
      </div>
    </div>

    <!-- 列表 -->
    <div class="card mt15">
      <div class="card__header">
        <span>人员列表</span>
        <div class="flex gap10">
          <BaseButton size="small" title="刷新列表" @click="onRefresh">
            <template #icon><FaIcon name="refresh" :size="14" /></template>
            刷新
          </BaseButton>
          <BaseButton v-if="isSuperAdmin" type="primary" size="small" @click="openCreate">
            <template #icon><FaIcon name="plus" :size="14" /></template>
            新增人员
          </BaseButton>
        </div>
      </div>

      <!-- 筛选 -->
      <div class="card__body personnel__filter">
        <div class="personnel__filter-item">
          <label class="personnel__filter-label">关键字</label>
          <BaseInput
            v-model="filters.keyword"
            icon="user"
            placeholder="姓名 / 邮箱"
            @keyup.enter="onSearch"
          />
        </div>
        <div class="personnel__filter-item">
          <label class="personnel__filter-label">角色</label>
          <BaseSelect v-model="filters.role" :options="ROLE_OPTIONS" placeholder="全部角色" />
        </div>
        <div class="personnel__filter-item">
          <label class="personnel__filter-label">人员类型</label>
          <BaseSelect
            v-model="filters.employment_type"
            :options="EMPLOYMENT_OPTIONS"
            placeholder="全部类型"
          />
        </div>
        <div class="personnel__filter-item">
          <label class="personnel__filter-label">状态</label>
          <BaseSelect v-model="filters.status" :options="STATUS_OPTIONS" placeholder="全部状态" />
        </div>
        <div class="personnel__filter-actions">
          <BaseButton type="primary" @click="onSearch">查询</BaseButton>
          <BaseButton @click="onReset">重置</BaseButton>
        </div>
      </div>

      <!-- 表格 -->
      <table class="table personnel__table">
        <thead>
          <tr>
            <th>姓名</th>
            <th>登录邮箱</th>
            <th>手机号</th>
            <th>角色</th>
            <th>人员类型</th>
            <th>状态</th>
            <th>最近登录</th>
            <th>创建时间</th>
            <th class="personnel__table-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in list" :key="item.id">
            <td>
              <div class="personnel__user">
                <span class="personnel__avatar">{{ item.name.charAt(0) }}</span>
                <div class="personnel__user-info">
                  <p class="personnel__user-name">{{ item.name }}</p>
                  <p class="personnel__user-id">ID：{{ item.id }}</p>
                </div>
              </div>
            </td>
            <td>{{ item.email }}</td>
            <td>
              <span v-if="item.phone">{{ item.phone }}</span>
              <span v-else class="text-placeholder">未填写</span>
            </td>
            <td>
              <BaseTag
                :type="
                  item.role === 'SUPER_ADMIN'
                    ? 'warning'
                    : item.role === 'ADMIN'
                      ? 'primary'
                      : 'default'
                "
              >
                {{ ROLE_LABELS[item.role] }}
              </BaseTag>
            </td>
            <td>
              <BaseTag
                :type="
                  item.employment_type === 'FULL_TIME'
                    ? 'success'
                    : item.employment_type === 'OUTSOURCE'
                      ? 'warning'
                      : 'info'
                "
              >
                {{ EMPLOYMENT_LABELS[item.employment_type] }}
              </BaseTag>
            </td>
            <td>
              <BaseTag :type="item.status === 'ACTIVE' ? 'success' : 'danger'" dot>
                {{ STATUS_LABELS[item.status] }}
              </BaseTag>
            </td>
            <td>
              <p>{{ formatDateTime(item.last_login_at) }}</p>
              <p v-if="item.last_login_ip" class="personnel__ip">{{ item.last_login_ip }}</p>
            </td>
            <td>{{ formatDateTime(item.created_at) }}</td>
            <td>
              <div class="table__actions personnel__actions">
                <button class="personnel__action" title="编辑" @click="openEdit(item)">
                  <FaIcon name="edit" :size="14" />
                </button>
                <button
                  class="personnel__action"
                  :title="item.status === 'ACTIVE' ? '禁用' : '启用'"
                  @click="onToggleStatus(item)"
                >
                  <FaIcon name="power-off" :size="14" />
                </button>
                <button
                  v-if="isSuperAdmin"
                  class="personnel__action"
                  title="分配权限"
                  @click="openPermission(item)"
                >
                  <FaIcon name="key" :size="14" />
                </button>
                <button
                  v-if="isSuperAdmin"
                  class="personnel__action personnel__action--danger"
                  title="删除"
                  @click="onRemove(item)"
                >
                  <FaIcon name="trash-o" :size="14" />
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!loading && list.length === 0">
            <td colspan="9" class="personnel__empty">暂无数据</td>
          </tr>
        </tbody>
      </table>

      <div class="card__body">
        <BasePagination v-model="page" v-model:page-size="pageSize" :total="total" />
      </div>
    </div>

    <!-- 新增 / 编辑人员 -->
    <BaseModal v-model="dialogVisible" :title="dialogMode === 'create' ? '新增人员' : '编辑人员'">
      <form class="form" @submit.prevent="onSubmit">
        <div class="personnel__form-row">
          <div class="form-item">
            <label class="form-item__label form-item__label--required" for="p-name">姓名</label>
            <BaseInput id="p-name" v-model="form.name" icon="user" placeholder="请输入姓名" />
          </div>
          <div class="form-item">
            <label class="form-item__label form-item__label--required" for="p-email"
              >登录邮箱</label
            >
            <BaseInput
              id="p-email"
              v-model="form.email"
              type="email"
              icon="mail"
              placeholder="请输入邮箱"
            />
          </div>
          <div class="form-item">
            <label class="form-item__label" for="p-phone">手机号</label>
            <BaseInput
              id="p-phone"
              v-model="form.phone"
              icon="user"
              placeholder="用于日常联系，可留空"
            />
          </div>
        </div>

        <div class="personnel__form-row">
          <div class="form-item">
            <label class="form-item__label form-item__label--required" for="p-type">人员类型</label>
            <BaseSelect id="p-type" v-model="form.employment_type" :options="EMPLOYMENT_OPTIONS" />
          </div>
          <div class="form-item">
            <label class="form-item__label form-item__label--required" for="p-role">角色</label>
            <BaseSelect
              id="p-role"
              v-model="form.role"
              :options="
                isSuperAdmin ? ROLE_OPTIONS : ROLE_OPTIONS.filter((o) => o.value !== 'SUPER_ADMIN')
              "
            />
          </div>
        </div>

        <div class="personnel__form-row">
          <div class="form-item">
            <label class="form-item__label form-item__label--required" for="p-status"
              >账号状态</label
            >
            <BaseSelect id="p-status" v-model="form.status" :options="STATUS_OPTIONS" />
          </div>
          <div v-if="dialogMode === 'create'" class="form-item">
            <label class="form-item__label form-item__label--required" for="p-password"
              >初始密码</label
            >
            <BaseInput
              id="p-password"
              v-model="form.password"
              type="password"
              icon="lock"
              placeholder="至少 8 位"
              password-toggle
            />
          </div>
        </div>
      </form>

      <template #footer>
        <BaseButton @click="dialogVisible = false">取消</BaseButton>
        <BaseButton type="primary" :loading="submitting" @click="onSubmit">保存</BaseButton>
      </template>
    </BaseModal>

    <!-- 分配角色与权限（仅超级管理员） -->
    <BaseModal v-model="permissionVisible" title="分配角色与权限" size="md">
      <p class="personnel__permission-target">
        正在为 <strong>{{ permissionTarget?.name }}</strong
        >（{{ permissionTarget?.email }}）分配权限
      </p>

      <div class="form-item">
        <label class="form-item__label form-item__label--required" for="perm-role">角色</label>
        <BaseSelect id="perm-role" v-model="permissionRole" :options="ROLE_OPTIONS" />
      </div>

      <div class="form-item">
        <span class="form-item__label">功能权限</span>
        <div class="personnel__permissions">
          <BaseCheckbox
            v-for="item in PERMISSIONS"
            :key="item.key"
            :model-value="permissionChecked.includes(item.key)"
            :label="item.label"
            @update:model-value="
              (checked: boolean) => {
                permissionChecked = checked
                  ? [...permissionChecked, item.key]
                  : permissionChecked.filter((k) => k !== item.key)
              }
            "
          />
        </div>
      </div>

      <template #footer>
        <BaseButton @click="permissionVisible = false">取消</BaseButton>
        <BaseButton type="primary" @click="onSavePermission">保存</BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.personnel__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 15px;
}

.personnel__stat-value {
  font-size: 22px;
  font-weight: 500;
  line-height: 1.3;
}

.personnel__stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.personnel__filter {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 15px;
  align-items: flex-end;
  padding-bottom: 0;
}

.personnel__filter-item {
  width: 180px;
}

.personnel__filter-label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.personnel__filter-actions {
  display: flex;
  gap: 8px;
}

.personnel__table th,
.personnel__table td {
  vertical-align: middle;
}

.personnel__table-actions {
  width: 220px;
}

.personnel__user {
  display: flex;
  align-items: center;
  gap: 9px;
}

.personnel__avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  font-size: 13px;
  color: #fff;
  background-color: var(--color-primary);
  border-radius: 50%;
}

.personnel__user-name {
  font-weight: 500;
}

.personnel__user-id,
.personnel__ip {
  font-size: 12px;
  color: var(--color-text-placeholder);
}

.personnel__actions {
  flex-wrap: wrap;
}

.personnel__action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  font-size: 13px;
  color: var(--color-primary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition:
    color var(--transition),
    background-color var(--transition);
}

.personnel__action:hover {
  color: var(--color-primary-active);
  background-color: var(--color-primary-light);
}

.personnel__action--danger {
  color: var(--color-danger);
}

.personnel__action--danger:hover {
  color: var(--color-danger-active);
}

.personnel__empty {
  padding: 30px 0;
  text-align: center;
  color: var(--color-text-placeholder);
}

.personnel__form-row {
  display: flex;
  gap: 15px;
}

.personnel__form-row .form-item {
  flex: 1;
}

.personnel__permission-target {
  margin-bottom: 15px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.personnel__permissions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  padding: 12px;
  background-color: var(--color-surface-alt);
  border-radius: var(--radius-sm);
}

@media (max-width: 900px) {
  .personnel__form-row {
    flex-direction: column;
    gap: 0;
  }

  .personnel__filter-item {
    width: 100%;
  }
}
</style>

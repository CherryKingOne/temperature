import type {
  AdminRole,
  EmploymentType,
  PageResult,
  Personnel,
  PersonnelPayload,
  PersonnelQuery,
} from '@/types/personnel'

/**
 * 人员管理接口契约
 *
 * 后端人员管理接口尚未实现，这里先用本地数据把页面跑通、供评审；
 * 接口就绪后只需把下面每个函数体替换为 http 调用，页面代码无需改动。
 */

const ROLE_VALUES: AdminRole[] = ['SUPER_ADMIN', 'ADMIN', 'MEMBER']
const EMPLOYMENT_VALUES: EmploymentType[] = ['FULL_TIME', 'OUTSOURCE', 'PART_TIME']

let seed = 1000

function nextId(): string {
  seed += 1
  return String(370952000000000000 + seed)
}

function daysAgo(days: number): string {
  return new Date(Date.now() - days * 86400000).toISOString()
}

/** 本地示例数据 */
const store: Personnel[] = [
  {
    id: '370952000000000001',
    name: '平台管理员',
    email: 'cherry_050607@163.com',
    role: 'SUPER_ADMIN',
    employment_type: 'FULL_TIME',
    status: 'ACTIVE',
    last_login_at: daysAgo(0),
    last_login_ip: '127.0.0.1',
    created_at: daysAgo(30),
  },
  {
    id: '370952000000000002',
    name: '张伟',
    email: 'zhangwei@example.com',
    role: 'ADMIN',
    employment_type: 'FULL_TIME',
    status: 'ACTIVE',
    last_login_at: daysAgo(1),
    last_login_ip: '192.168.1.21',
    created_at: daysAgo(28),
  },
  {
    id: '370952000000000003',
    name: '李娜',
    email: 'lina@example.com',
    role: 'ADMIN',
    employment_type: 'FULL_TIME',
    status: 'ACTIVE',
    last_login_at: daysAgo(2),
    last_login_ip: '192.168.1.35',
    created_at: daysAgo(25),
  },
  {
    id: '370952000000000004',
    name: '王强',
    email: 'wangqiang@example.com',
    role: 'MEMBER',
    employment_type: 'OUTSOURCE',
    status: 'ACTIVE',
    last_login_at: daysAgo(5),
    last_login_ip: '10.0.3.14',
    created_at: daysAgo(20),
  },
  {
    id: '370952000000000005',
    name: '赵敏',
    email: 'zhaomin@example.com',
    role: 'MEMBER',
    employment_type: 'PART_TIME',
    status: 'ACTIVE',
    last_login_at: daysAgo(9),
    last_login_ip: '10.0.3.88',
    created_at: daysAgo(18),
  },
  {
    id: '370952000000000006',
    name: '孙浩',
    email: 'sunhao@example.com',
    role: 'MEMBER',
    employment_type: 'OUTSOURCE',
    status: 'DISABLED',
    last_login_at: daysAgo(30),
    last_login_ip: '10.0.5.7',
    created_at: daysAgo(15),
  },
  {
    id: '370952000000000007',
    name: '周雅',
    email: 'zhouya@example.com',
    role: 'MEMBER',
    employment_type: 'PART_TIME',
    status: 'ACTIVE',
    last_login_at: daysAgo(3),
    last_login_ip: '172.16.2.19',
    created_at: daysAgo(12),
  },
  {
    id: '370952000000000008',
    name: '吴桐',
    email: 'wutong@example.com',
    role: 'MEMBER',
    employment_type: 'FULL_TIME',
    status: 'ACTIVE',
    last_login_at: daysAgo(6),
    last_login_ip: '172.16.2.44',
    created_at: daysAgo(9),
  },
  {
    id: '370952000000000009',
    name: '郑凯',
    email: 'zhengkai@example.com',
    role: 'MEMBER',
    employment_type: 'OUTSOURCE',
    status: 'ACTIVE',
    last_login_at: null,
    last_login_ip: null,
    created_at: daysAgo(6),
  },
  {
    id: '370952000000000010',
    name: '冯雪',
    email: 'fengxue@example.com',
    role: 'MEMBER',
    employment_type: 'PART_TIME',
    status: 'ACTIVE',
    last_login_at: daysAgo(11),
    last_login_ip: '10.0.8.61',
    created_at: daysAgo(4),
  },
  {
    id: '370952000000000011',
    name: '许斌',
    email: 'xubin@example.com',
    role: 'MEMBER',
    employment_type: 'FULL_TIME',
    status: 'ACTIVE',
    last_login_at: daysAgo(2),
    last_login_ip: '192.168.3.52',
    created_at: daysAgo(3),
  },
  {
    id: '370952000000000012',
    name: '何静',
    email: 'hejing@example.com',
    role: 'MEMBER',
    employment_type: 'OUTSOURCE',
    status: 'DISABLED',
    last_login_at: null,
    last_login_ip: null,
    created_at: daysAgo(2),
  },
]

function delay(): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, 200))
}

/** 人员列表（分页 + 条件过滤） */
export async function listPersonnel(query: PersonnelQuery): Promise<PageResult<Personnel>> {
  await delay()

  const keyword = (query.keyword ?? '').trim().toLowerCase()
  const filtered = store.filter((item) => {
    if (keyword) {
      const hit =
        item.name.toLowerCase().includes(keyword) || item.email.toLowerCase().includes(keyword)
      if (!hit) return false
    }
    if (query.role && item.role !== query.role) return false
    if (query.employment_type && item.employment_type !== query.employment_type) return false
    if (query.status && item.status !== query.status) return false
    return true
  })

  const start = (query.page - 1) * query.page_size
  return {
    items: filtered.slice(start, start + query.page_size),
    total: filtered.length,
    page: query.page,
    page_size: query.page_size,
  }
}

/** 人员统计（总数 / 各类型 / 启用中） */
export async function personnelSummary(): Promise<{
  total: number
  full_time: number
  outsource: number
  part_time: number
  active: number
}> {
  await delay()
  return {
    total: store.length,
    full_time: store.filter((i) => i.employment_type === 'FULL_TIME').length,
    outsource: store.filter((i) => i.employment_type === 'OUTSOURCE').length,
    part_time: store.filter((i) => i.employment_type === 'PART_TIME').length,
    active: store.filter((i) => i.status === 'ACTIVE').length,
  }
}

/** 新增人员 */
export async function createPersonnel(payload: PersonnelPayload): Promise<Personnel> {
  await delay()
  const item: Personnel = {
    id: nextId(),
    name: payload.name,
    email: payload.email,
    role: payload.role,
    employment_type: payload.employment_type,
    status: payload.status,
    last_login_at: null,
    last_login_ip: null,
    created_at: new Date().toISOString(),
  }
  store.unshift(item)
  return item
}

/** 编辑人员 */
export async function updatePersonnel(id: string, payload: PersonnelPayload): Promise<Personnel> {
  await delay()
  const item = store.find((i) => i.id === id)
  if (!item) throw new Error('人员不存在')
  Object.assign(item, {
    name: payload.name,
    email: payload.email,
    role: payload.role,
    employment_type: payload.employment_type,
    status: payload.status,
  })
  return item
}

/** 启用 / 禁用 */
export async function setPersonnelStatus(id: string, status: Personnel['status']): Promise<void> {
  await delay()
  const item = store.find((i) => i.id === id)
  if (!item) throw new Error('人员不存在')
  item.status = status
}

/** 删除人员 */
export async function removePersonnel(id: string): Promise<void> {
  await delay()
  const index = store.findIndex((i) => i.id === id)
  if (index >= 0) store.splice(index, 1)
}

/** 可分配的角色 */
export function assignableRoles(): AdminRole[] {
  return ROLE_VALUES
}

/** 人员类型枚举 */
export function employmentTypes(): EmploymentType[] {
  return EMPLOYMENT_VALUES
}

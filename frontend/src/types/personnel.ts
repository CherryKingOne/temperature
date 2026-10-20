/** 人员管理相关类型（对应后端人员管理接口） */

/** 角色：超级管理员 / 管理员 / 普通管理员 */
export type AdminRole = 'SUPER_ADMIN' | 'ADMIN' | 'MEMBER'

/** 人员类型：正式员工 / 外包 / 兼职 */
export type EmploymentType = 'FULL_TIME' | 'OUTSOURCE' | 'PART_TIME'

/** 账号状态 */
export type PersonnelStatus = 'ACTIVE' | 'DISABLED'

/** 人员条目 */
export interface Personnel {
  id: string
  name: string
  email: string
  /** 手机号（联系方式） */
  phone: string | null
  role: AdminRole
  employment_type: EmploymentType
  status: PersonnelStatus
  last_login_at: string | null
  last_login_ip: string | null
  created_at: string
}

/** 列表查询条件 */
export interface PersonnelQuery {
  /** 姓名 / 邮箱关键字 */
  keyword?: string
  role?: AdminRole | ''
  employment_type?: EmploymentType | ''
  status?: PersonnelStatus | ''
  page: number
  page_size: number
}

/** 分页结果 */
export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/** 新增 / 编辑人员 */
export interface PersonnelPayload {
  name: string
  email: string
  phone?: string
  role: AdminRole
  employment_type: EmploymentType
  status: PersonnelStatus
  /** 新增时必填：初始密码 */
  password?: string
}

/** 角色中文名 */
export const ROLE_LABELS: Record<AdminRole, string> = {
  SUPER_ADMIN: '超级管理员',
  ADMIN: '管理员',
  MEMBER: '普通管理员',
}

/** 人员类型中文名 */
export const EMPLOYMENT_LABELS: Record<EmploymentType, string> = {
  FULL_TIME: '正式员工',
  OUTSOURCE: '外包',
  PART_TIME: '兼职',
}

/** 状态中文名 */
export const STATUS_LABELS: Record<PersonnelStatus, string> = {
  ACTIVE: '正常',
  DISABLED: '已禁用',
}

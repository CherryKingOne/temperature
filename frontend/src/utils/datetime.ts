/** 时间格式化：后端返回 ISO 字符串，前端统一展示到分钟 */

function pad(value: number): string {
  return value < 10 ? `0${value}` : String(value)
}

/** ISO 字符串 -> YYYY-MM-DD HH:mm */
export function formatDateTime(value?: string | null): string {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ` +
    `${pad(date.getHours())}:${pad(date.getMinutes())}`
  )
}

/** ISO 字符串 -> YYYY-MM-DD */
export function formatDate(value?: string | null): string {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

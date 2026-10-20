import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastItem {
  id: number
  type: ToastType
  message: string
}

/** 顶部提示：默认 3 秒后自动关闭 */
export const useToastStore = defineStore('toast', () => {
  const items = ref<ToastItem[]>([])
  let seed = 0

  function remove(id: number): void {
    items.value = items.value.filter((item) => item.id !== id)
  }

  function show(message: string, type: ToastType = 'info', duration = 3000): void {
    const id = ++seed
    items.value = [...items.value, { id, type, message }]
    window.setTimeout(() => remove(id), duration)
  }

  const success = (message: string) => show(message, 'success')
  const error = (message: string) => show(message, 'error')
  const warning = (message: string) => show(message, 'warning')
  const info = (message: string) => show(message, 'info')

  return { items, show, remove, success, error, warning, info }
})

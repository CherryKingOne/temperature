<script setup lang="ts">
import { useToastStore } from '@/stores/toast'
import FaIcon from './FaIcon.vue'

/** 顶部提示容器：3 秒后自动关闭 */
const toast = useToastStore()

const ICON_MAP: Record<string, string> = {
  success: 'check-circle',
  error: 'exclamation-circle',
  warning: 'exclamation-circle',
  info: 'exclamation-circle',
}

/** 提示类型对应的左侧色条 */
const TYPE_CLASS: Record<string, string> = {
  success: 'border-l-success',
  error: 'border-l-danger',
  warning: 'border-l-warning',
  info: 'border-l-info',
}

const toastClass =
  'flex animate-toast-in items-center gap-2 min-w-[220px] rounded-sm border border-border-light border-l-[3px] bg-surface px-4 py-2.5 text-sm text-text shadow-popup'
</script>

<template>
  <div class="fixed top-[20px] left-1/2 z-[3000] flex -translate-x-1/2 flex-col gap-2.5">
    <div
      v-for="item in toast.items"
      :key="item.id"
      :class="[toastClass, TYPE_CLASS[item.type] ?? TYPE_CLASS.info]"
    >
      <FaIcon :name="ICON_MAP[item.type] ?? 'exclamation-circle'" :size="16" />
      <span>{{ item.message }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToastStore } from '@/stores/toast'
import UiIcon from './UiIcon.vue'

/** 顶部提示容器：3 秒后自动关闭 */
const toast = useToastStore()

const ICON_MAP: Record<string, string> = {
  success: 'check-circle',
  error: 'alert-circle',
  warning: 'alert-circle',
  info: 'alert-circle',
}
</script>

<template>
  <div class="toast">
    <div
      v-for="item in toast.items"
      :key="item.id"
      class="toast__item"
      :class="`toast__item--${item.type}`"
    >
      <UiIcon :name="ICON_MAP[item.type] ?? 'alert-circle'" :size="16" />
      <span>{{ item.message }}</span>
    </div>
  </div>
</template>

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
</script>

<template>
  <div class="toast">
    <div
      v-for="item in toast.items"
      :key="item.id"
      class="toast__item"
      :class="`toast__item--${item.type}`"
    >
      <FaIcon :name="ICON_MAP[item.type] ?? 'exclamation-circle'" :size="16" />
      <span>{{ item.message }}</span>
    </div>
  </div>
</template>

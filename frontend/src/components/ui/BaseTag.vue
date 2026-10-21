<script setup lang="ts">
import { computed } from 'vue'

/** 标签：用于状态、角色、人员类型等标识 */
const props = withDefaults(
  defineProps<{
    type?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
    /** 圆点前缀 */
    dot?: boolean
  }>(),
  {
    type: 'default',
    dot: false,
  },
)

/** 各类型的配色 */
const TYPE_CLASS: Record<string, string> = {
  default: 'border-border-light bg-disabled-bg text-text-secondary',
  primary: 'border-primary-border bg-primary-light text-primary',
  success: 'border-[rgba(26,179,148,0.35)] bg-[rgba(26,179,148,0.12)] text-success',
  warning: 'border-[rgba(248,172,89,0.4)] bg-[rgba(248,172,89,0.14)] text-warning',
  danger: 'border-[rgba(237,85,101,0.35)] bg-[rgba(237,85,101,0.12)] text-danger',
  info: 'border-[rgba(35,198,200,0.35)] bg-[rgba(35,198,200,0.12)] text-info',
}

const tagClass = computed(
  () =>
    `inline-flex items-center gap-1.25 whitespace-nowrap rounded-[2px] border px-2 py-px text-xs leading-[18px] ${
      TYPE_CLASS[props.type] ?? TYPE_CLASS.default
    }`,
)
</script>

<template>
  <span :class="tagClass">
    <i v-if="dot" class="h-1.5 w-1.5 rounded-full bg-current" />
    <slot />
  </span>
</template>

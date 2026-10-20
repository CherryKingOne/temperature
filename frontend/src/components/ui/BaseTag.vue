<script setup lang="ts">
/** 标签：用于状态、角色、人员类型等标识 */
withDefaults(
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
</script>

<template>
  <span class="tag" :class="`tag--${type}`">
    <i v-if="dot" class="tag__dot" />
    <slot />
  </span>
</template>

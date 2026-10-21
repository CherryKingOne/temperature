<script setup lang="ts">
/**
 * Font Awesome 4.7 图标（与若依保持一致）
 * 通过 index.html 引入 FA4 CDN，图标名即 fa-xxx
 */
const props = withDefaults(defineProps<{ name: string; size?: number }>(), {
  size: 14,
})
</script>

<template>
  <i
    class="fa inline-block shrink-0 align-middle leading-none"
    :class="`fa-${props.name}`"
    :style="{ fontSize: `${props.size}px` }"
    aria-hidden="true"
  />
</template>

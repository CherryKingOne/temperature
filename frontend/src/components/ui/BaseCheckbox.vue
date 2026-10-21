<script setup lang="ts">
import { computed } from 'vue'

import FaIcon from './FaIcon.vue'

/** 复选框：18x18px，选中态为主题色 */
const props = defineProps<{ modelValue: boolean; label?: string; disabled?: boolean }>()

const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

/** 勾选框样式：选中态与未选中态互斥 */
const boxClass = computed(() =>
  props.modelValue
    ? 'border-primary bg-primary text-white'
    : 'border-[var(--checkbox-border)] bg-[var(--checkbox-bg)] text-transparent group-hover:border-primary',
)

function toggle(): void {
  if (props.disabled) return
  emit('update:modelValue', !props.modelValue)
}
</script>

<template>
  <label
    class="group inline-flex cursor-pointer select-none items-center gap-1.5 text-sm text-[var(--checkbox-color)]"
    @click.prevent="toggle"
  >
    <span
      class="inline-flex h-4.5 w-4.5 items-center justify-center rounded-sm border text-xs transition-all duration-300 ease"
      :class="boxClass"
    >
      <FaIcon name="check" :size="12" />
    </span>
    <span v-if="props.label">{{ props.label }}</span>
  </label>
</template>

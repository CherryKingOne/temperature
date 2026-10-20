<script setup lang="ts">
import UiIcon from './UiIcon.vue'

/** 复选框：18x18px，选中态为主题色 */
const props = defineProps<{ modelValue: boolean; label?: string; disabled?: boolean }>()

const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

function toggle(): void {
  if (props.disabled) return
  emit('update:modelValue', !props.modelValue)
}
</script>

<template>
  <label class="checkbox" :class="{ 'is-checked': props.modelValue }" @click.prevent="toggle">
    <span class="checkbox__box"><UiIcon name="check" :size="12" /></span>
    <span v-if="props.label" class="checkbox__label">{{ props.label }}</span>
  </label>
</template>

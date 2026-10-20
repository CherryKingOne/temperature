<script setup lang="ts">
/** 开关：40x20px，圆形滑块，激活色 #33cabb */
const props = defineProps<{ modelValue: boolean; disabled?: boolean }>()

const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

function toggle(): void {
  if (props.disabled) return
  emit('update:modelValue', !props.modelValue)
}
</script>

<template>
  <span
    class="switch"
    :class="{ 'is-checked': props.modelValue }"
    role="switch"
    :aria-checked="props.modelValue"
    @click="toggle"
  >
    <span class="switch__slider" />
  </span>
</template>

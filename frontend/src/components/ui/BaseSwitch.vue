<script setup lang="ts">
import { computed } from 'vue'

/** 开关：40x20px，圆形滑块，激活色 #33cabb */
const props = defineProps<{ modelValue: boolean; disabled?: boolean }>()

const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

/** 滑块位移：开启时向右平移 20px */
const sliderClass = computed(() =>
  props.modelValue ? 'translate-x-5' : 'translate-x-0',
)

function toggle(): void {
  if (props.disabled) return
  emit('update:modelValue', !props.modelValue)
}
</script>

<template>
  <span
    class="relative inline-flex h-5 w-10 cursor-pointer items-center rounded-full transition-colors duration-300 ease"
    :class="props.modelValue ? 'bg-[#33cabb]' : 'bg-border'"
    role="switch"
    :aria-checked="props.modelValue"
    @click="toggle"
  >
    <span
      class="absolute left-0.5 h-4 w-4 rounded-full bg-white shadow-[0_1px_3px_rgba(0,0,0,0.25)] transition-transform duration-300 ease"
      :class="sliderClass"
    />
  </span>
</template>

<script setup lang="ts">
import FaIcon from './FaIcon.vue'

export interface SelectOption {
  label: string
  value: string
}

/** 下拉选择：与输入框统一样式（高 34px、1px 边框、4px 圆角） */
const props = withDefaults(
  defineProps<{
    modelValue?: string
    options: SelectOption[]
    placeholder?: string
    disabled?: boolean
    id?: string
  }>(),
  {
    modelValue: '',
    placeholder: '请选择',
    disabled: false,
    id: undefined,
  },
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

function onChange(event: Event): void {
  emit('update:modelValue', (event.target as HTMLSelectElement).value)
}
</script>

<template>
  <div class="relative flex items-center" :class="{ 'opacity-70': props.disabled }">
    <select
      :id="props.id"
      class="h-control w-full cursor-pointer appearance-none rounded border border-border bg-surface py-1.5 pl-3 pr-[30px] text-base text-text transition-[border-color,box-shadow] duration-300 ease hover:border-primary-border focus:border-primary focus:shadow-[0_0_0_2px_var(--app-primary-light)] focus:outline-none disabled:cursor-not-allowed disabled:bg-disabled-bg disabled:text-disabled-text"
      :value="props.modelValue"
      :disabled="props.disabled"
      @change="onChange"
    >
      <option value="">{{ props.placeholder }}</option>
      <option v-for="item in props.options" :key="item.value" :value="item.value">
        {{ item.label }}
      </option>
    </select>
    <FaIcon class="pointer-events-none absolute right-2.5 text-text-placeholder" name="chevron-down" :size="14" />
  </div>
</template>

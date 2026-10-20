<script setup lang="ts">
import UiIcon from './UiIcon.vue'

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
  <div class="select" :class="{ 'is-disabled': props.disabled }">
    <select
      :id="props.id"
      class="select__control"
      :value="props.modelValue"
      :disabled="props.disabled"
      @change="onChange"
    >
      <option value="">{{ props.placeholder }}</option>
      <option v-for="item in props.options" :key="item.value" :value="item.value">
        {{ item.label }}
      </option>
    </select>
    <UiIcon class="select__arrow" name="chevron-down" :size="14" />
  </div>
</template>

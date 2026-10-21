<script setup lang="ts">
import { computed, ref } from 'vue'

import FaIcon from './FaIcon.vue'

/** 输入框：高度 34px，边框 1px #ddd，圆角 4px，聚焦时高亮 */
const props = withDefaults(
  defineProps<{
    modelValue?: string
    /** 输入类型 */
    type?: 'text' | 'password' | 'email' | 'number'
    placeholder?: string
    /** 错误文案（同时给输入框描红） */
    error?: string
    disabled?: boolean
    /** 前置图标名 */
    icon?: string
    /** 是否提供密码明文切换 */
    passwordToggle?: boolean
    autocomplete?: string
    /** 输入框 id，便于 label 关联 */
    id?: string
  }>(),
  {
    modelValue: '',
    type: 'text',
    placeholder: '',
    error: '',
    disabled: false,
    icon: '',
    passwordToggle: false,
    autocomplete: 'off',
    id: undefined,
  },
)

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const visible = ref(false)

const inputType = computed(() => {
  if (props.passwordToggle) {
    return visible.value ? 'text' : 'password'
  }
  return props.type
})

/** 输入框样式：正常态与错误态互斥，避免边框 / 聚焦态互相覆盖 */
const inputClass = computed(() =>
  [
    'h-control w-full rounded border bg-[var(--input-bg)] py-1.5 text-base leading-normal text-[var(--input-color)] transition-[border-color,box-shadow] duration-300 ease placeholder:text-[var(--input-placeholder)] focus:outline-none disabled:cursor-not-allowed disabled:bg-disabled-bg disabled:text-disabled-text',
    props.icon ? 'pl-9' : 'pl-3',
    props.passwordToggle ? 'pr-[38px]' : 'pr-3',
    props.error
      ? 'border-danger focus:border-danger focus:shadow-[0_0_0_2px_rgba(237,85,101,0.15)]'
      : 'border-border hover:border-primary-border focus:border-primary focus:shadow-[0_0_0_2px_var(--app-primary-light)]',
  ].join(' '),
)

function onInput(event: Event): void {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="relative flex items-center">
    <span
      v-if="props.icon"
      class="pointer-events-none absolute left-3 inline-flex items-center text-text-placeholder"
    >
      <FaIcon :name="props.icon" :size="16" />
    </span>
    <input
      :id="props.id"
      :class="inputClass"
      :type="inputType"
      :value="props.modelValue"
      :placeholder="props.placeholder"
      :disabled="props.disabled"
      :autocomplete="props.autocomplete"
      @input="onInput"
    />
    <span
      v-if="props.passwordToggle"
      class="absolute right-2 inline-flex h-6 w-6 cursor-pointer items-center justify-center rounded-sm text-text-secondary transition-all duration-300 ease hover:bg-primary-light hover:text-primary"
      :title="visible ? '隐藏密码' : '显示密码'"
      role="button"
      @click="visible = !visible"
    >
      <FaIcon :name="visible ? 'eye-slash' : 'eye'" :size="16" />
    </span>
  </div>
</template>

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

function onInput(event: Event): void {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="input-group">
    <span v-if="props.icon" class="input-group__prefix">
      <FaIcon :name="props.icon" :size="16" />
    </span>
    <input
      :id="props.id"
      class="input"
      :class="{ 'input--error': Boolean(props.error), 'input--has-suffix': props.passwordToggle }"
      :type="inputType"
      :value="props.modelValue"
      :placeholder="props.placeholder"
      :disabled="props.disabled"
      :autocomplete="props.autocomplete"
      @input="onInput"
    />
    <span
      v-if="props.passwordToggle"
      class="input-group__suffix"
      :title="visible ? '隐藏密码' : '显示密码'"
      role="button"
      @click="visible = !visible"
    >
      <FaIcon :name="visible ? 'eye-slash' : 'eye'" :size="16" />
    </span>
  </div>
</template>

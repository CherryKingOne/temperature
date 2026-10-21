<script setup lang="ts">
import { computed } from 'vue'

/** 按钮：圆角 3px，高度 34px（标准）/ 28px（小） */
const props = withDefaults(
  defineProps<{
    /** 按钮风格 */
    type?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
    /** 尺寸 */
    size?: 'default' | 'small' | 'large'
    /** 胶囊圆角 */
    rounded?: boolean
    /** 描边风格 */
    outline?: boolean
    /** 占满整行 */
    block?: boolean
    /** 加载中 */
    loading?: boolean
    disabled?: boolean
    /** 原生按钮类型 */
    nativeType?: 'button' | 'submit' | 'reset'
  }>(),
  {
    type: 'default',
    size: 'default',
    rounded: false,
    outline: false,
    block: false,
    loading: false,
    disabled: false,
    nativeType: 'button',
  },
)

/** 基础样式：不含颜色 / 尺寸，避免与类型、尺寸样式互相覆盖 */
const BASE =
  'inline-flex items-center justify-center gap-1.25 whitespace-nowrap border leading-none transition-all duration-300 ease active:shadow-[inset_0_0_0_1px_var(--app-primary)] disabled:cursor-not-allowed disabled:border-border-light disabled:bg-disabled-bg disabled:text-disabled-text disabled:shadow-none'

/** 各类型的配色（含 hover / active 态） */
const TYPE_CLASS: Record<string, string> = {
  default:
    'border-border bg-surface text-text hover:border-primary-border hover:bg-primary-light hover:text-primary',
  primary:
    'border-primary bg-primary text-white hover:border-primary-hover hover:bg-primary-hover hover:text-white active:border-primary-active-hover active:bg-primary-active-hover',
  success:
    'border-success bg-success text-white hover:border-success-active hover:bg-success-active hover:text-white',
  warning:
    'border-warning bg-warning text-white hover:border-warning-active hover:bg-warning-active hover:text-white',
  danger:
    'border-danger bg-danger text-white hover:border-danger-active hover:bg-danger-active hover:text-white',
  info: 'border-info bg-info text-white hover:border-info-active hover:bg-info-active hover:text-white',
}

/** 各尺寸：高度 / 内边距 / 字号 */
const SIZE_CLASS: Record<string, string> = {
  default: 'h-control px-3 py-1.5 text-sm',
  small: 'h-control-sm px-2.5 py-1 text-xs',
  large: 'h-10 px-4.5 py-2 text-base',
}

const buttonClass = computed(() => {
  const type = TYPE_CLASS[props.type] ?? TYPE_CLASS.default
  const size = SIZE_CLASS[props.size] ?? SIZE_CLASS.default
  return [
    BASE,
    size,
    type,
    props.rounded ? 'rounded-full' : 'rounded-sm',
    props.outline ? 'bg-transparent' : '',
    props.block ? 'w-full' : '',
  ]
    .filter(Boolean)
    .join(' ')
})
</script>

<template>
  <button
    :class="buttonClass"
    :type="props.nativeType"
    :disabled="props.disabled || props.loading"
    :title="props.loading ? '处理中...' : undefined"
  >
    <span
      v-if="props.loading"
      class="inline-block h-3.5 w-3.5 animate-spinner rounded-full border-2 border-current border-t-transparent"
    />
    <span v-else-if="$slots.icon" class="mr-1"><slot name="icon" /></span>
    <slot />
  </button>
</template>

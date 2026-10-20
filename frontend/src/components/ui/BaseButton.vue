<script setup lang="ts">
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
</script>

<template>
  <button
    class="btn"
    :class="{
      'btn--primary': props.type === 'primary',
      'btn--success': props.type === 'success',
      'btn--warning': props.type === 'warning',
      'btn--danger': props.type === 'danger',
      'btn--info': props.type === 'info',
      'btn--rounded': props.rounded,
      'btn--outline': props.outline,
      'btn--sm': props.size === 'small',
      'btn--lg': props.size === 'large',
      'btn--block': props.block,
      'is-disabled': props.disabled || props.loading,
    }"
    :type="props.nativeType"
    :disabled="props.disabled || props.loading"
    :title="props.loading ? '处理中...' : undefined"
  >
    <span v-if="props.loading" class="spinner" />
    <span v-else-if="$slots.icon" class="btn__icon"><slot name="icon" /></span>
    <slot />
  </button>
</template>

<style scoped>
.btn__icon {
  margin-right: 4px;
}
</style>

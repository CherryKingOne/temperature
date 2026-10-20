<script setup lang="ts">
import FaIcon from './FaIcon.vue'

/** 弹窗：遮罩 rgba(0,0,0,.5)，内容圆角 8px 居中 */
const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    /** 尺寸：小 500 / 中 800 / 大 1200 */
    size?: 'sm' | 'md' | 'lg'
  }>(),
  {
    title: '',
    size: 'sm',
  },
)

const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

function close(): void {
  emit('update:modelValue', false)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="props.modelValue" class="modal__mask" @click.self="close">
      <div class="modal" :class="`modal--${props.size}`">
        <div class="modal__header">
          <span>{{ props.title }}</span>
          <span class="modal__close" title="关闭" @click="close">
            <FaIcon name="times" :size="16" />
          </span>
        </div>
        <div class="modal__body">
          <slot />
        </div>
        <div v-if="$slots.footer" class="modal__footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

/** 弹窗宽度：各尺寸互斥 */
const SIZE_CLASS: Record<string, string> = {
  sm: 'w-[500px]',
  md: 'w-[800px]',
  lg: 'w-[1200px]',
}

const modalClass = computed(
  () =>
    `max-h-[90vh] max-w-[92vw] overflow-auto rounded-lg bg-surface shadow-popup ${
      SIZE_CLASS[props.size] ?? SIZE_CLASS.sm
    }`,
)

function close(): void {
  emit('update:modelValue', false)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="props.modelValue" class="fixed inset-0 z-[2000] flex items-center justify-center bg-mask" @click.self="close">
      <div :class="modalClass">
        <div class="flex h-12 items-center justify-between border-b border-border-light px-[15px] text-lg">
          <span>{{ props.title }}</span>
          <span class="cursor-pointer text-text-placeholder hover:text-text" title="关闭" @click="close">
            <FaIcon name="times" :size="16" />
          </span>
        </div>
        <div class="p-[15px]">
          <slot />
        </div>
        <div v-if="$slots.footer" class="flex justify-end gap-2 border-t border-border-light px-[15px] py-2.5">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

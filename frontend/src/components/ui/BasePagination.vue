<script setup lang="ts">
import { computed } from 'vue'

import FaIcon from './FaIcon.vue'

/** 分页：居中对齐，每页条数可选 */
const props = withDefaults(
  defineProps<{
    modelValue: number
    total: number
    pageSize?: number
    pageSizes?: number[]
  }>(),
  {
    pageSize: 10,
    pageSizes: () => [10, 25, 50],
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: number]
  'update:pageSize': [value: number]
}>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const pages = computed(() => {
  const count = totalPages.value
  const current = props.modelValue
  if (count <= 7) return Array.from({ length: count }, (_, i) => i + 1)

  const result: number[] = [1]
  const start = Math.max(2, current - 1)
  const end = Math.min(count - 1, current + 1)
  if (start > 2) result.push(0)
  for (let i = start; i <= end; i += 1) result.push(i)
  if (end < count - 1) result.push(0)
  result.push(count)
  return result
})

function go(page: number): void {
  if (page < 1 || page > totalPages.value || page === props.modelValue) return
  emit('update:modelValue', page)
}

function onPageSizeChange(event: Event): void {
  const size = Number((event.target as HTMLSelectElement).value)
  emit('update:pageSize', size)
  emit('update:modelValue', 1)
}
</script>

<template>
  <div v-if="props.total > 0" class="pagination">
    <span class="pagination__total">共 {{ props.total }} 条</span>

    <button
      class="pagination__item"
      :class="{ 'is-disabled': props.modelValue <= 1 }"
      title="上一页"
      @click="go(props.modelValue - 1)"
    >
      <FaIcon name="chevron-down" :size="12" class="pagination__prev" />
    </button>

    <template v-for="(page, index) in pages" :key="`${page}-${index}`">
      <span v-if="page === 0" class="pagination__dots">...</span>
      <button
        v-else
        class="pagination__item"
        :class="{ 'is-active': page === props.modelValue }"
        @click="go(page)"
      >
        {{ page }}
      </button>
    </template>

    <button
      class="pagination__item"
      :class="{ 'is-disabled': props.modelValue >= totalPages }"
      title="下一页"
      @click="go(props.modelValue + 1)"
    >
      <FaIcon name="chevron-down" :size="12" class="pagination__next" />
    </button>

    <select class="pagination__size" :value="props.pageSize" @change="onPageSizeChange">
      <option v-for="size in props.pageSizes" :key="size" :value="size">{{ size }} 条/页</option>
    </select>
  </div>
</template>

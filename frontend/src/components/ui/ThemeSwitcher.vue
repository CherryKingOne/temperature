<script setup lang="ts">
import { computed } from 'vue'

import { THEME_COLORS, useThemeStore } from '@/stores/theme'
import FaIcon from './FaIcon.vue'

/**
 * 主题切换器：切换主题色与明暗模式
 * - surface=dark：深色背景上（认证页底部、导航条）
 * - surface=light：浅色卡片上（账号菜单）
 */
const props = withDefaults(defineProps<{ surface?: 'dark' | 'light' }>(), {
  surface: 'dark',
})

const theme = useThemeStore()

/** 色板样式：选中态在深色 / 浅色背景下边框与光晕不同 */
const swatchClass = computed(() =>
  props.surface === 'light'
    ? 'border-primary opacity-100 shadow-[0_0_0_2px_var(--app-primary-light)]'
    : 'border-[rgba(255,255,255,0.9)] opacity-100 shadow-[0_0_0_2px_rgba(255,255,255,0.25)]',
)

/** 未选中色板：透明边框、半透明 */
const swatchIdleClass = 'border-transparent opacity-75'

/** 明暗切换按钮样式 */
const actionClass = computed(() =>
  props.surface === 'light'
    ? 'text-text-secondary hover:bg-primary-light hover:text-primary'
    : 'text-white/70 hover:bg-white/15 hover:text-white',
)
</script>

<template>
  <div class="flex items-center gap-2">
    <div class="flex items-center gap-1.5">
      <button
        v-for="item in THEME_COLORS"
        :key="item.value"
        class="h-3 w-3 cursor-pointer rounded-full border transition-all duration-300 ease hover:scale-120 hover:opacity-100"
        :class="theme.color === item.value ? swatchClass : swatchIdleClass"
        :style="{ backgroundColor: item.color }"
        :title="item.label"
        :aria-label="item.label"
        @click="theme.setColor(item.value)"
      />
    </div>
    <span
      class="inline-flex h-5.5 w-5.5 cursor-pointer items-center justify-center rounded-sm text-sm transition-all duration-300 ease"
      :class="actionClass"
      :title="theme.mode === 'light' ? '切换到暗黑模式' : '切换到明亮模式'"
      role="button"
      @click="theme.toggleMode()"
    >
      <FaIcon :name="theme.mode === 'light' ? 'moon-o' : 'sun-o'" :size="15" />
    </span>
  </div>
</template>

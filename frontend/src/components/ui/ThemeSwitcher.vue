<script setup lang="ts">
import { THEME_COLORS, useThemeStore } from '@/stores/theme'
import UiIcon from './UiIcon.vue'

/**
 * 主题切换器：切换主题色与明暗模式
 * - surface=dark：深色背景上（认证页底部、导航条）
 * - surface=light：浅色卡片上（账号菜单）
 */
const props = withDefaults(defineProps<{ surface?: 'dark' | 'light' }>(), {
  surface: 'dark',
})

const theme = useThemeStore()
</script>

<template>
  <div class="theme-switcher" :class="`theme-switcher--${props.surface}`">
    <div class="theme-switcher__swatches">
      <button
        v-for="item in THEME_COLORS"
        :key="item.value"
        class="theme-switcher__swatch"
        :class="{ 'is-active': theme.color === item.value }"
        :style="{ backgroundColor: item.color }"
        :title="item.label"
        :aria-label="item.label"
        @click="theme.setColor(item.value)"
      />
    </div>
    <span
      class="theme-switcher__action"
      :title="theme.mode === 'light' ? '切换到暗黑模式' : '切换到明亮模式'"
      role="button"
      @click="theme.toggleMode()"
    >
      <UiIcon :name="theme.mode === 'light' ? 'moon' : 'sun'" :size="15" />
    </span>
  </div>
</template>

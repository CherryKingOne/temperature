<script setup lang="ts">
import UiIcon from '@/components/ui/UiIcon.vue'
import ThemeSwitcher from '@/components/ui/ThemeSwitcher.vue'

/** 认证页布局：左侧系统介绍 + 右侧表单，宽度 750px */
withDefaults(defineProps<{ title: string; subtitle?: string }>(), {
  subtitle: '',
})
</script>

<template>
  <div class="auth">
    <div class="auth__background" />

    <div class="auth__body">
      <div class="auth__panel">
        <aside class="auth__intro">
          <div class="auth__brand">
            <span class="auth__brand-logo"><UiIcon name="bar-chart" :size="18" /></span>
            <span>Temperature 平台</span>
          </div>
          <h1 class="auth__intro-title">企业级后台管理系统</h1>
          <p class="auth__intro-desc">
            面向中大型团队的一体化管理平台，统一处理账号、角色与菜单权限，让业务管理更清晰、更高效。
          </p>
          <ul class="auth__features">
            <li class="auth__feature">
              <UiIcon class="auth__feature-icon" name="check-circle" :size="15" />
              统一身份认证，支持邮箱验证码校验
            </li>
            <li class="auth__feature">
              <UiIcon class="auth__feature-icon" name="check-circle" :size="15" />
              细粒度的角色与菜单权限体系
            </li>
            <li class="auth__feature">
              <UiIcon class="auth__feature-icon" name="check-circle" :size="15" />
              多主题切换，适配不同团队视觉规范
            </li>
          </ul>
        </aside>

        <section class="auth__form">
          <h2 class="auth__title">{{ title }}</h2>
          <p v-if="subtitle" class="auth__subtitle">{{ subtitle }}</p>
          <slot />
        </section>
      </div>
    </div>

    <footer class="auth__footer">
      <span>Copyright © 2026 Temperature Platform</span>
      <ThemeSwitcher variant="inline" />
    </footer>
  </div>
</template>

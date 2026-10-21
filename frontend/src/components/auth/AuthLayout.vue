<script setup lang="ts">
import FaIcon from '@/components/ui/FaIcon.vue'
import ThemeSwitcher from '@/components/ui/ThemeSwitcher.vue'

/** 认证页布局：左侧系统介绍 + 右侧表单，宽度 750px */
withDefaults(defineProps<{ title: string; subtitle?: string }>(), {
  subtitle: '',
})
</script>

<template>
  <div class="relative flex min-h-full flex-col overflow-hidden">
    <div
      class="fixed inset-0 z-0 bg-[radial-gradient(circle_at_15%_20%,var(--app-primary-active)_0%,transparent_45%),radial-gradient(circle_at_85%_80%,var(--app-primary)_0%,transparent_40%),linear-gradient(135deg,#1d2b3a_0%,#2f4050_45%,#1a2532_100%)] transition-[background] duration-300 ease before:absolute before:inset-0 before:bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] before:[background-size:40px_40px]"
    />

    <div class="relative z-[1] flex flex-1 items-center justify-center px-5 py-10">
      <div
        class="flex w-[750px] max-w-full overflow-hidden rounded-sm border border-white/25 bg-white/20 shadow-[0_12px_40px_rgba(0,0,0,0.25)]"
      >
        <aside
          class="flex w-[370px] flex-col justify-center bg-black/18 p-10 pr-9 pl-9 text-white max-[768px]:hidden"
        >
          <div class="mb-6 flex items-center gap-2.5 text-2xl font-medium">
            <span
              class="inline-flex h-9 w-9 items-center justify-center rounded bg-primary text-lg text-white"
              ><FaIcon name="bar-chart" :size="18" /></span
            >
            <span>Temperature 平台</span>
          </div>
          <h1 class="mb-2.5 text-xl font-medium">企业级后台管理系统</h1>
          <p class="mb-6 text-sm leading-[1.8] text-white/75">
            面向中大型团队的一体化管理平台，统一处理账号、角色与菜单权限，让业务管理更清晰、更高效。
          </p>
          <ul class="flex flex-col gap-2.5">
            <li class="flex items-center gap-2 text-sm text-white/85">
              <FaIcon class="text-white" name="check-circle" :size="15" />
              统一身份认证，支持邮箱验证码校验
            </li>
            <li class="flex items-center gap-2 text-sm text-white/85">
              <FaIcon class="text-white" name="check-circle" :size="15" />
              细粒度的角色与菜单权限体系
            </li>
            <li class="flex items-center gap-2 text-sm text-white/85">
              <FaIcon class="text-white" name="check-circle" :size="15" />
              多主题切换，适配不同团队视觉规范
            </li>
          </ul>
        </aside>

        <section class="w-full bg-white/20 px-6 pt-8 pb-6 min-[769px]:w-[380px] min-[769px]:px-9 min-[769px]:pt-9 min-[769px]:pb-7">
          <h2 class="mb-1 text-2xl font-medium text-white">{{ title }}</h2>
          <p v-if="subtitle" class="mb-6 text-sm text-white/75">{{ subtitle }}</p>
          <slot />
        </section>
      </div>
    </div>

    <footer class="flex items-center justify-center gap-3.5 px-5 pt-3 pb-[18px] text-center text-xs text-white/60">
      <span>Copyright © 2026 Temperature Platform</span>
      <ThemeSwitcher />
    </footer>
  </div>
</template>

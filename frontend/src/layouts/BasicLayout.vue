<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import FaIcon from '@/components/ui/FaIcon.vue'
import UserMenu from '@/components/ui/UserMenu.vue'
import { useAuthStore } from '@/stores/auth'

/** 基本布局：顶部导航 + 侧边栏 + 内容区（页签） */
const auth = useAuthStore()
const route = useRoute()

const collapsed = ref(false)

interface MenuItem {
  key: string
  title: string
  icon: string
  /** 已实现的页面跳转地址；为空表示功能开发中 */
  path?: string
}

const MENU: MenuItem[] = [
  { key: 'home', title: '首页', icon: 'home', path: '/home' },
  { key: 'admin', title: '人员管理', icon: 'user', path: '/admin/personnel' },
  { key: 'system', title: '系统设置', icon: 'cog' },
]

const activeKey = computed(() => route.path.replace(/^\//, '').split('/')[0] ?? '')

const currentTitle = computed(() => (route.meta.title as string | undefined) ?? '个人中心')

/** 侧边栏宽度：收起态只留图标 */
const sidebarClass = computed(() =>
  collapsed.value ? 'w-sidebar-collapsed' : 'w-sidebar',
)

/** 内容区左边距跟随侧边栏宽度 */
const contentClass = computed(() =>
  collapsed.value ? 'pl-sidebar-collapsed' : 'pl-sidebar',
)

/** 菜单项样式：选中 / 禁用 / 常规三态互斥 */
function menuItemClass(item: MenuItem): string {
  if (!item.path) {
    return 'cursor-not-allowed text-sidebar-text opacity-45 hover:bg-transparent'
  }
  if (activeKey.value === item.key) {
    return 'bg-sidebar-active-bg text-sidebar-text-active shadow-[inset_3px_0_0_var(--app-primary)]'
  }
  return 'text-sidebar-text hover:bg-sidebar-hover-bg hover:text-white'
}

onMounted(async () => {
  // 刷新页面后恢复登录态：顶栏头像与账号菜单需要管理员信息
  if (!auth.admin) {
    await auth.loadCurrentAdmin().catch(() => undefined)
  }
})
</script>

<template>
  <div class="min-h-full bg-bg">
    <header
      class="fixed top-0 right-0 left-0 z-[900] flex h-navbar items-center justify-between bg-primary px-3 text-white shadow-[0_1px_4px_rgba(0,0,0,0.15)]"
    >
      <div class="flex items-center gap-2.5">
        <button class="inline-flex cursor-pointer text-white" title="收起/展开菜单" @click="collapsed = !collapsed">
          <FaIcon name="bars" :size="18" />
        </button>
        <span
          class="inline-flex h-7 w-7 items-center justify-center rounded-sm bg-white/20 text-[15px]"
          ><FaIcon name="bar-chart" :size="18" /></span
        >
        <span class="text-[15px] font-medium">Temperature 平台</span>
      </div>

      <div class="flex items-center gap-2.5">
        <UserMenu />
      </div>
    </header>

    <aside class="fixed top-navbar bottom-0 left-0 z-[800] overflow-hidden bg-sidebar-bg transition-[width] duration-300 ease max-[768px]:hidden" :class="sidebarClass">
      <nav class="py-2">
        <template v-for="item in MENU" :key="item.key">
          <router-link
            v-if="item.path"
            class="flex h-12 items-center gap-2.5 px-5 py-3.5 text-sm transition-all duration-300 ease"
            :class="[menuItemClass(item), collapsed ? 'justify-center' : '']"
            :to="item.path"
            :title="item.title"
          >
            <FaIcon :name="item.icon" :size="16" />
            <span v-show="!collapsed" class="whitespace-nowrap">{{ item.title }}</span>
          </router-link>
          <div
            v-else
            class="flex h-12 items-center gap-2.5 px-5 py-3.5 text-sm transition-all duration-300 ease"
            :class="[menuItemClass(item), collapsed ? 'justify-center' : '']"
            :title="`${item.title}（功能开发中）`"
          >
            <FaIcon :name="item.icon" :size="16" />
            <span v-show="!collapsed" class="whitespace-nowrap">{{ item.title }}</span>
          </div>
        </template>
      </nav>
    </aside>

    <main class="pt-navbar transition-[padding-left] duration-300 ease max-[768px]:pl-0" :class="contentClass">
      <div class="flex h-tabs items-center border-b border-border-light bg-surface">
        <div class="inline-flex h-tabs items-center gap-1.5 border-t-[3px] border-t-primary px-[15px] text-sm text-primary">
          <FaIcon name="home" :size="13" />
          {{ currentTitle }}
        </div>
      </div>
      <div class="p-[15px]">
        <RouterView />
      </div>
    </main>
  </div>
</template>

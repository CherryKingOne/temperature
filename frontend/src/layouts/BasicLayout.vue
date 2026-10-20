<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import UiIcon from '@/components/ui/UiIcon.vue'
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
  { key: 'profile', title: '个人中心', icon: 'user', path: '/profile' },
  { key: 'home', title: '首页', icon: 'home', path: '/home' },
  { key: 'admin', title: '管理员管理', icon: 'user' },
  { key: 'system', title: '系统设置', icon: 'cog' },
]

const activeKey = computed(() => route.path.replace(/^\//, '').split('/')[0] ?? '')

const currentTitle = computed(() => (route.meta.title as string | undefined) ?? '个人中心')

onMounted(async () => {
  // 刷新页面后恢复登录态：顶栏头像与账号菜单需要管理员信息
  if (!auth.admin) {
    await auth.loadCurrentAdmin().catch(() => undefined)
  }
})
</script>

<template>
  <div class="layout">
    <header class="layout__navbar">
      <div class="layout__navbar-left">
        <button class="layout__collapse" title="收起/展开菜单" @click="collapsed = !collapsed">
          <UiIcon name="menu" :size="18" />
        </button>
        <span class="layout__logo"><UiIcon name="bar-chart" :size="18" /></span>
        <span class="layout__title">Temperature 平台</span>
      </div>

      <div class="layout__navbar-right">
        <UserMenu />
      </div>
    </header>

    <aside class="layout__sidebar" :class="{ 'is-collapsed': collapsed }">
      <nav class="layout__menu">
        <template v-for="item in MENU" :key="item.key">
          <router-link
            v-if="item.path"
            class="layout__menu-item"
            :class="{ 'is-active': activeKey === item.key }"
            :to="item.path"
            :title="item.title"
          >
            <UiIcon :name="item.icon" :size="16" />
            <span class="layout__menu-text">{{ item.title }}</span>
          </router-link>
          <div v-else class="layout__menu-item is-disabled" :title="`${item.title}（功能开发中）`">
            <UiIcon :name="item.icon" :size="16" />
            <span class="layout__menu-text">{{ item.title }}</span>
          </div>
        </template>
      </nav>
    </aside>

    <main class="layout__content">
      <div class="tabs">
        <div class="tabs__item is-active">
          <UiIcon name="home" :size="13" />
          {{ currentTitle }}
        </div>
      </div>
      <div class="layout__view">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100%;
  background-color: var(--color-bg);
}

.layout__navbar {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 900;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--navbar-height);
  padding: 0 12px;
  color: #fff;
  background-color: var(--color-primary);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.layout__navbar-left,
.layout__navbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.layout__collapse {
  display: inline-flex;
  color: #fff;
  cursor: pointer;
}

.layout__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  font-size: 15px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-sm);
}

.layout__title {
  font-size: 15px;
  font-weight: 500;
}

.layout__sidebar {
  position: fixed;
  top: var(--navbar-height);
  bottom: 0;
  left: 0;
  z-index: 800;
  width: var(--sidebar-width);
  overflow: hidden;
  background-color: var(--sidebar-bg);
  transition: width var(--transition);
}

.layout__sidebar.is-collapsed {
  width: var(--sidebar-width-collapsed);
}

.layout__menu {
  padding: 8px 0;
}

.layout__menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 48px;
  padding: 14px 20px;
  font-size: 13px;
  color: var(--sidebar-text);
  cursor: pointer;
  transition:
    background-color var(--transition),
    color var(--transition);
}

.layout__menu-item:hover {
  color: #fff;
  background-color: var(--sidebar-hover-bg);
}

.layout__menu-item.is-active {
  color: var(--sidebar-text-active);
  background-color: var(--sidebar-active-bg);
  box-shadow: inset 3px 0 0 var(--color-primary);
}

.layout__menu-item.is-disabled {
  color: var(--sidebar-text);
  opacity: 0.45;
  cursor: not-allowed;
}

.layout__menu-item.is-disabled:hover {
  color: var(--sidebar-text);
  background-color: transparent;
}

.layout__menu-text {
  white-space: nowrap;
}

.layout__content {
  padding-top: var(--navbar-height);
  padding-left: var(--sidebar-width);
  transition: padding-left var(--transition);
}

.layout__view {
  padding: 15px;
}

@media (max-width: 768px) {
  .layout__sidebar {
    display: none;
  }

  .layout__content {
    padding-left: 0;
  }
}
</style>

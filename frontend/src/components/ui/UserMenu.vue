<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import ThemeSwitcher from './ThemeSwitcher.vue'
import FaIcon from './FaIcon.vue'

/**
 * 账号菜单：点击头像展开下拉卡片（个人中心 / 退出登录）
 * 点击卡片外部或按 ESC 关闭
 */
const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const open = ref(false)
const root = ref<HTMLElement | null>(null)

const initial = () => (auth.admin?.name ?? 'A').charAt(0)

function close(): void {
  open.value = false
}

function onDocumentClick(event: MouseEvent): void {
  if (root.value && !root.value.contains(event.target as Node)) {
    close()
  }
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    close()
  }
}

watch(open, (value) => {
  if (value) {
    document.addEventListener('click', onDocumentClick)
    document.addEventListener('keydown', onKeydown)
  } else {
    document.removeEventListener('click', onDocumentClick)
    document.removeEventListener('keydown', onKeydown)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
  document.removeEventListener('keydown', onKeydown)
})

async function onLogout(): Promise<void> {
  close()
  await auth.logout()
  toast.success('已安全退出')
  await router.push('/login')
}
</script>

<template>
  <div ref="root" class="user-menu">
    <button class="user-menu__trigger" title="账号菜单" @click="open = !open">
      <span class="user-menu__avatar">{{ initial() }}</span>
      <span class="user-menu__name">{{ auth.admin?.name ?? '管理员' }}</span>
      <em v-if="auth.isSuperAdmin" class="user-menu__role">超级管理员</em>
      <FaIcon class="user-menu__arrow" name="chevron-down" :size="12" />
    </button>

    <transition name="user-menu">
      <div v-if="open" class="user-menu__panel">
        <div class="user-menu__header">
          <span class="user-menu__avatar user-menu__avatar--lg">{{ initial() }}</span>
          <div class="user-menu__info">
            <p class="user-menu__title">{{ auth.admin?.name ?? '管理员' }}</p>
            <p class="user-menu__email">{{ auth.admin?.email ?? '-' }}</p>
          </div>
        </div>

        <div class="user-menu__divider" />

        <div class="user-menu__row">
          <span class="user-menu__label">主题</span>
          <ThemeSwitcher surface="light" />
        </div>

        <div class="user-menu__divider" />

        <router-link class="user-menu__item" to="/profile" @click="close">
          <FaIcon name="user" :size="15" />
          <span>个人中心</span>
        </router-link>

        <button class="user-menu__item user-menu__item--danger" @click="onLogout">
          <FaIcon name="arrow-right" :size="15" />
          <span>退出登录</span>
        </button>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.user-menu {
  position: relative;
}

.user-menu__trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  font-size: 13px;
  color: #fff;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition);
}

.user-menu__trigger:hover {
  background-color: rgba(255, 255, 255, 0.15);
}

.user-menu__avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  font-size: 12px;
  color: #fff;
  background-color: rgba(255, 255, 255, 0.22);
  border-radius: 50%;
}

.user-menu__avatar--lg {
  width: 36px;
  height: 36px;
  font-size: 15px;
}

.user-menu__name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-menu__role {
  padding: 1px 6px;
  font-size: 11px;
  font-style: normal;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.user-menu__arrow {
  opacity: 0.8;
  transition: transform var(--transition);
}

.user-menu__trigger:hover .user-menu__arrow {
  transform: translateY(1px);
}

/* 下拉卡片 */
.user-menu__panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 950;
  width: 210px;
  padding: 6px 0;
  color: var(--color-text);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius);
  box-shadow: var(--shadow-popup);
}

.user-menu__header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px 12px;
}

.user-menu__info {
  min-width: 0;
}

.user-menu__title {
  font-size: 14px;
  font-weight: 500;
}

.user-menu__email {
  font-size: 12px;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-menu__divider {
  height: 1px;
  margin: 0 0 4px;
  background-color: var(--color-border-lighter);
}

.user-menu__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 6px 14px;
}

.user-menu__label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.user-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 14px;
  font-size: 13px;
  color: var(--color-text);
  text-align: left;
  transition: background-color var(--transition);
}

.user-menu__item:hover {
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.user-menu__item--danger:hover {
  color: var(--color-danger);
  background-color: rgba(237, 85, 101, 0.1);
}

.user-menu-enter-active,
.user-menu-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.user-menu-enter-from,
.user-menu-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>

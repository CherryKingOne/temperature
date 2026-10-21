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
  <div ref="root" class="relative">
    <button
      class="group inline-flex items-center gap-1.5 rounded-sm px-2 py-1 text-sm text-white transition-colors duration-300 ease hover:bg-white/15"
      title="账号菜单"
      @click="open = !open"
    >
      <span
        class="inline-flex h-6 w-6 items-center justify-center rounded-full bg-white/22 text-xs text-white"
        >{{ initial() }}</span
      >
      <span class="max-w-[120px] overflow-hidden text-ellipsis whitespace-nowrap">{{
        auth.admin?.name ?? '管理员'
      }}</span>
      <em
        v-if="auth.isSuperAdmin"
        class="rounded-[2px] bg-white/20 px-1.5 py-px text-[11px] not-italic"
        >超级管理员</em
      >
      <FaIcon
        class="opacity-80 transition-transform duration-300 ease group-hover:translate-y-px"
        name="chevron-down"
        :size="12"
      />
    </button>

    <transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1.5"
      leave-active-class="transition-all duration-200 ease-in"
      leave-to-class="opacity-0 -translate-y-1.5"
    >
      <div
        v-if="open"
        class="absolute top-[calc(100%+8px)] right-0 z-[950] w-[210px] rounded border border-border-light bg-surface py-1.5 text-text shadow-popup"
      >
        <div class="flex items-center gap-2.5 px-3 pt-2.5 pb-3">
          <span
            class="inline-flex h-9 w-9 items-center justify-center rounded-full bg-white/22 text-[15px] text-white"
            >{{ initial() }}</span
          >
          <div class="min-w-0">
            <p class="text-base font-medium">{{ auth.admin?.name ?? '管理员' }}</p>
            <p class="overflow-hidden text-ellipsis whitespace-nowrap text-xs text-text-secondary">
              {{ auth.admin?.email ?? '-' }}
            </p>
          </div>
        </div>

        <div class="mx-0 mb-1 h-px bg-border-lighter" />

        <div class="flex items-center justify-between gap-2.5 px-3.5 py-1.5">
          <span class="text-sm text-text-secondary">主题</span>
          <ThemeSwitcher surface="light" />
        </div>

        <div class="mx-0 mb-1 h-px bg-border-lighter" />

        <router-link
          class="flex w-full items-center gap-2 px-3.5 py-2 text-left text-sm text-text transition-colors duration-300 ease hover:bg-primary-light hover:text-primary"
          to="/profile"
          @click="close"
        >
          <FaIcon name="user" :size="15" />
          <span>个人中心</span>
        </router-link>

        <button
          class="flex w-full items-center gap-2 px-3.5 py-2 text-left text-sm text-text transition-colors duration-300 ease hover:bg-[rgba(237,85,101,0.1)] hover:text-danger"
          @click="onLogout"
        >
          <FaIcon name="arrow-right" :size="15" />
          <span>退出登录</span>
        </button>
      </div>
    </transition>
  </div>
</template>

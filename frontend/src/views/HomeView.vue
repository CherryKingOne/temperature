<script setup lang="ts">
import { onMounted } from 'vue'

import FaIcon from '@/components/ui/FaIcon.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(async () => {
  if (!auth.admin) {
    await auth.loadCurrentAdmin().catch(() => undefined)
  }
})
</script>

<template>
  <div>
    <div class="rounded border border-border bg-surface shadow-card">
      <div
        class="flex h-[41px] items-center justify-between border-b border-border-lighter bg-card-header-bg px-[15px] text-base"
      >
        <span>欢迎使用 Temperature 平台</span>
      </div>
      <div class="p-[15px]">
        <p class="mb-2.5">你好，{{ auth.admin?.name ?? '管理员' }}！</p>
        <p class="mb-5 text-sm text-text-secondary">
          这里是管理后台首页，后续将承载管理员列表、菜单与权限体系等功能模块。
        </p>

        <ul class="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-x-5 gap-y-3">
          <li class="flex items-center gap-2.5 text-sm">
            <span class="text-text-secondary">登录邮箱</span>
            <span>{{ auth.admin?.email ?? '-' }}</span>
          </li>
          <li class="flex items-center gap-2.5 text-sm">
            <span class="text-text-secondary">角色</span>
            <span>
              <em
                class="rounded-[2px] bg-primary-light px-2 py-px text-xs not-italic text-primary"
                >{{ auth.isSuperAdmin ? '超级管理员' : '管理员' }}</em
              >
            </span>
          </li>
          <li class="flex items-center gap-2.5 text-sm">
            <span class="text-text-secondary">账号状态</span>
            <span class="text-success">正常</span>
          </li>
          <li class="flex items-center gap-2.5 text-sm">
            <span class="text-text-secondary">最近登录</span>
            <span>{{ auth.admin?.last_login_at ?? '首次登录' }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="mt-[15px] grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-[15px]">
      <div class="rounded border border-border bg-surface shadow-card">
        <div class="flex flex-col items-center justify-center gap-2.5 p-[15px]">
          <FaIcon name="user" :size="26" />
          <span class="text-sm">管理员管理</span>
          <span class="text-xs text-text-placeholder">账号列表、角色调整、启用禁用</span>
        </div>
      </div>
      <div class="rounded border border-border bg-surface shadow-card">
        <div class="flex flex-col items-center justify-center gap-2.5 p-[15px]">
          <FaIcon name="cog" :size="26" />
          <span class="text-sm">菜单与权限</span>
          <span class="text-xs text-text-placeholder">菜单树、角色权限、字段权限</span>
        </div>
      </div>
      <div class="rounded border border-border bg-surface shadow-card">
        <div class="flex flex-col items-center justify-center gap-2.5 p-[15px]">
          <FaIcon name="bar-chart" :size="26" />
          <span class="text-sm">系统监控</span>
          <span class="text-xs text-text-placeholder">在线用户、操作日志、服务状态</span>
        </div>
      </div>
    </div>
  </div>
</template>

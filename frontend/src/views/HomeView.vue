<script setup lang="ts">
import { onMounted } from 'vue'

import UiIcon from '@/components/ui/UiIcon.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(async () => {
  if (!auth.admin) {
    await auth.loadCurrentAdmin().catch(() => undefined)
  }
})
</script>

<template>
  <div class="home">
    <div class="card">
      <div class="card__header">
        <span>欢迎使用 Temperature 平台</span>
      </div>
      <div class="card__body">
        <p class="mb10">你好，{{ auth.admin?.name ?? '管理员' }}！</p>
        <p class="text-secondary text-sm mb20">
          这里是管理后台首页，后续将承载管理员列表、菜单与权限体系等功能模块。
        </p>

        <ul class="home__profile">
          <li class="home__profile-item">
            <span class="home__profile-label">登录邮箱</span>
            <span>{{ auth.admin?.email ?? '-' }}</span>
          </li>
          <li class="home__profile-item">
            <span class="home__profile-label">角色</span>
            <span>
              <em class="home__role">{{ auth.isSuperAdmin ? '超级管理员' : '管理员' }}</em>
            </span>
          </li>
          <li class="home__profile-item">
            <span class="home__profile-label">账号状态</span>
            <span class="text-success">正常</span>
          </li>
          <li class="home__profile-item">
            <span class="home__profile-label">最近登录</span>
            <span>{{ auth.admin?.last_login_at ?? '首次登录' }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="home__cards">
      <div class="card">
        <div class="card__body flex-center flex-col gap10">
          <UiIcon name="user" :size="26" />
          <span class="text-sm">管理员管理</span>
          <span class="text-xs text-placeholder">账号列表、角色调整、启用禁用</span>
        </div>
      </div>
      <div class="card">
        <div class="card__body flex-center flex-col gap10">
          <UiIcon name="cog" :size="26" />
          <span class="text-sm">菜单与权限</span>
          <span class="text-xs text-placeholder">菜单树、角色权限、字段权限</span>
        </div>
      </div>
      <div class="card">
        <div class="card__body flex-center flex-col gap10">
          <UiIcon name="bar-chart" :size="26" />
          <span class="text-sm">系统监控</span>
          <span class="text-xs text-placeholder">在线用户、操作日志、服务状态</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home__profile {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px 20px;
}

.home__profile-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.home__profile-label {
  color: var(--color-text-secondary);
}

.home__role {
  padding: 1px 8px;
  font-size: 12px;
  font-style: normal;
  color: var(--color-primary);
  background-color: var(--color-primary-light);
  border-radius: 2px;
}

.home__cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 15px;
  margin-top: 15px;
}
</style>

import { createRouter, createWebHistory } from 'vue-router'

import { AUTH_EXPIRED_EVENT } from '@/api/client'
import BasicLayout from '@/layouts/BasicLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

declare module 'vue-router' {
  interface RouteMeta {
    /** 仅未登录可访问（登录 / 注册页） */
    guestOnly?: boolean
    title?: string
  }
}

/** 登录后的默认落地页：个人中心（所有账号都能访问，不受权限影响） */
export const DEFAULT_HOME = '/profile'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: BasicLayout,
      children: [
        {
          path: '',
          redirect: DEFAULT_HOME,
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { title: '个人中心' },
        },
        {
          path: 'home',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
          meta: { title: '首页' },
        },
        {
          path: 'admin/personnel',
          name: 'personnel',
          component: () => import('@/views/admin/PersonnelView.vue'),
          meta: { title: '人员管理' },
        },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true, title: '账号登录' },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true, title: '账号注册' },
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: DEFAULT_HOME,
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.guestOnly) {
    // 已登录时不再展示登录 / 注册页
    return auth.isLoggedIn ? { path: DEFAULT_HOME } : true
  }
  if (!auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  return true
})

// 令牌失效（接口返回 401）时统一跳回登录页
window.addEventListener(AUTH_EXPIRED_EVENT, () => {
  const auth = useAuthStore()
  const toast = useToastStore()
  auth.clearSession()
  toast.warning('登录状态已失效，请重新登录')
  const current = router.currentRoute.value
  void router.push({
    path: '/login',
    query: current.name === 'login' ? {} : { redirect: current.fullPath },
  })
})

export default router

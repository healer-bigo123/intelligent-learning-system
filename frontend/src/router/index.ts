import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue')
      },
      {
        path: 'resources',
        name: 'Resources',
        component: () => import('@/pages/Resources.vue')
      },
      {
        path: 'records',
        name: 'Records',
        component: () => import('@/pages/Records.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/pages/Profile.vue')
      },
      {
        path: 'agent',
        name: 'Agent',
        component: () => import('@/immersive-agent.vue')
      },
      {
        path: 'mistakes',
        name: 'Mistakes',
        component: () => import('@/pages/Mistakes.vue')
      },
      {
        path: 'exercises',
        name: 'Exercises',
        component: () => import('@/pages/Exercises.vue')
      },
      {
        path: 'learning-path',
        name: 'LearningPath',
        component: () => import('@/pages/LearningPath.vue')
      },
      {
        path: 'classroom',
        name: 'Classroom',
        component: () => import('@/pages/Classroom.vue')
      },
      {
        path: 'mindmap',
        name: 'MindMap',
        component: () => import('@/pages/MindMap.vue')
      },
      {
        path: 'achievements',
        name: 'Achievements',
        component: () => import('@/pages/Achievements.vue')
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import('@/pages/Notifications.vue')
      },
      {
        path: 'focus',
        name: 'Focus',
        component: () => import('@/pages/Focus.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  console.log('路由守卫:', { path: to.path, hasToken: !!token, requiresAuth })

  if (requiresAuth && !token) {
    // 需要登录但未登录，跳转到登录页
    console.log('跳转到登录页')
    next('/login')
  } else if (to.path === '/login' && token) {
    // 已登录但访问登录页，跳转到首页
    console.log('已登录，跳转到首页')
    next('/')
  } else {
    next()
  }
})

export default router
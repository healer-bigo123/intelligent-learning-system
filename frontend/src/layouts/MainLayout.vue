<template>
  <div class="app-layout">
    <!-- 侧边导航 -->
    <aside class="sidebar" :class="{ collapsed: collapsedSidebar }">
      <div class="sidebar-header">
        <div class="logo" v-if="!collapsedSidebar">
          <div class="logo-icon">
            <component :is="icons.Bot" class="icon" />
          </div>
          <div class="logo-text">
            <h1 class="app-title">智学助手</h1>
            <p class="app-subtitle">AI Learning</p>
          </div>
        </div>
        <div class="logo-mini" v-else>
          <div class="logo-icon">
            <component :is="icons.Bot" class="icon" />
          </div>
        </div>
      </div>

      <nav class="nav-menu">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <component :is="item.icon" class="nav-icon" />
          <span class="nav-text" v-if="!collapsedSidebar">{{ item.label }}</span>
          <div class="nav-indicator" v-if="$route.path === item.path"></div>
        </router-link>
      </nav>

      <button class="collapse-toggle" @click="collapsedSidebar = !collapsedSidebar">
        <component :is="collapsedSidebar ? icons.ChevronRight : icons.ChevronLeft" class="toggle-icon" />
      </button>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部导航 -->
      <header class="top-header">
        <div class="header-left">
          <h2 class="page-title">{{ currentPageTitle }}</h2>
          <p class="page-subtitle">{{ currentPageDesc }}</p>
        </div>
        <div class="header-right">
          <div class="search-box">
            <component :is="icons.Search" class="search-icon" />
            <input type="text" placeholder="搜索..." class="search-input" />
          </div>
          <router-link to="/notifications" class="notification-btn">
            <component :is="icons.Bell" class="bell-icon" />
            <span class="notification-badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
          </router-link>
          <div class="user-menu">
            <div class="user-avatar">
              <component :is="icons.User" class="avatar-icon" />
            </div>
            <span class="user-name" v-if="!collapsedSidebar">{{ userName }}</span>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api/client'
import {
  Bot, LayoutDashboard, BookOpen, BarChart, User,
  MessageCircle, ChevronLeft, ChevronRight, Search, Bell,
  AlertCircle, Zap, Map, GraduationCap, Network,
  Award, BellRing, Timer, PieChart
} from 'lucide-vue-next'

const route = useRoute()

const unreadCount = ref(0)
const userName = ref('用户昵称')

onMounted(async () => {
  // 加载用户名
  try {
    const profileRes = await api.get('/auth/profile')
    userName.value = profileRes.data?.name || profileRes.data?.username || '用户昵称'
  } catch {
    // 使用默认值
  }

  // 加载未读通知数
  try {
    const notifRes = await api.get('/notifications')
    const items = notifRes.data?.items || []
    unreadCount.value = items.filter((n: any) => !n.is_read).length
  } catch {
    // 使用默认值
  }
})

const icons = {
  Bot, LayoutDashboard, BookOpen, BarChart, User,
  MessageCircle, ChevronLeft, ChevronRight, Search, Bell,
  AlertCircle, Zap, Map, GraduationCap, Network,
  Award, BellRing, Timer, PieChart
}

const collapsedSidebar = ref(false)

const menuItems = [
  { path: '/', label: '首页', icon: LayoutDashboard },
  { path: '/resources', label: '学习资源', icon: BookOpen },
  { path: '/records', label: '学习记录', icon: BarChart },
  { path: '/mistakes', label: '错题本', icon: AlertCircle },
  { path: '/exercises', label: '练习测试', icon: Zap },
  { path: '/learning-path', label: '学习路径', icon: Map },
  { path: '/classroom', label: '课堂互动', icon: GraduationCap },
  { path: '/mindmap', label: '思维导图', icon: Network },
  { path: '/achievements', label: '成就系统', icon: Award },
  { path: '/analytics', label: '成绩分析', icon: PieChart },
  { path: '/focus', label: '专注学习', icon: Timer },
  { path: '/agent', label: '智能助手', icon: MessageCircle },
  { path: '/profile', label: '个人中心', icon: User }
]

const pageTitles: Record<string, { title: string; desc: string }> = {
  '/': { title: '学习仪表盘', desc: '查看您的学习进度和推荐内容' },
  '/resources': { title: '学习资源', desc: '发现优质的学习内容' },
  '/records': { title: '学习记录', desc: '追踪您的学习历程' },
  '/mistakes': { title: '错题本', desc: '复习和巩固薄弱知识点' },
  '/exercises': { title: '练习测试', desc: '通过练习提升学习效果' },
  '/learning-path': { title: '学习路径', desc: '规划您的学习路线' },
  '/classroom': { title: '课堂互动', desc: '参与课堂互动和测验' },
  '/mindmap': { title: '思维导图', desc: '可视化知识结构' },
  '/achievements': { title: '成就系统', desc: '查看您的学习成就' },
  '/analytics': { title: '成绩分析', desc: '查看您的学习数据统计和分析报告' },
  '/focus': { title: '专注学习', desc: '番茄钟专注计时' },
  '/notifications': { title: '通知中心', desc: '查看您的消息通知' },
  '/agent': { title: '智能助手', desc: '与 AI 助手互动学习' },
  '/profile': { title: '个人中心', desc: '管理您的账户和设置' }
}

const currentPageTitle = computed(() => pageTitles[route.path]?.title || '学习仪表盘')
const currentPageDesc = computed(() => pageTitles[route.path]?.desc || '')
</script>

<style lang="scss" scoped>
.app-layout {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
}

.sidebar {
  width: 240px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: width 0.3s ease;

  &.collapsed {
    width: 72px;
  }
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-mini {
  display: flex;
  justify-content: center;
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;

  .icon {
    width: 24px;
    height: 24px;
    color: white;
  }
}

.logo-text {
  .app-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
  }

  .app-subtitle {
    font-size: 11px;
    color: var(--text-muted);
    margin: 2px 0 0;
  }
}

.nav-menu {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 102, 241, 0.3) rgba(51, 65, 85, 0.3);

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(51, 65, 85, 0.2);
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.3);
    border-radius: 3px;

    &:hover {
      background: rgba(99, 102, 241, 0.5);
    }
  }
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  &.active {
    background: rgba(99, 102, 241, 0.1);
    color: var(--primary-color);

    .nav-icon {
      color: var(--primary-color);
    }
  }

  .nav-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }

  .nav-text {
    font-size: 14px;
    font-weight: 500;
  }

  .nav-indicator {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 20px;
    background: var(--primary-color);
    border-radius: 0 2px 2px 0;
  }
}

.collapse-toggle {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 48px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-card);
    border-color: var(--primary-color);
  }

  .toggle-icon {
    width: 14px;
    height: 14px;
    color: var(--text-secondary);
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  .page-title {
    font-size: 24px;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.3px;
    text-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
  }

  .page-subtitle {
    font-size: 13px;
    color: #94a3b8;
    margin: 4px 0 0;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  min-width: 220px;
  height: 42px;
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  &:hover,
  &:focus-within {
    border-color: #60a5fa;
    box-shadow:
      0 2px 8px rgba(0, 0, 0, 0.15),
      0 0 0 1px #60a5fa;
  }
  .search-icon {
    width: 16px;
    height: 16px;
    color: #94a3b8;
  }
  .search-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #e2e8f0;
    font-size: 13px;
    &::placeholder {
      color: #64748b;
    }
  }
}

.notification-btn {
  position: relative;
  width: 44px;
  height: 42px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  &:hover {
    background: linear-gradient(145deg, #334155, #273548);
    border-color: #60a5fa;
    box-shadow:
      0 2px 8px rgba(0, 0, 0, 0.15),
      0 0 0 1px #60a5fa;
  }
  .bell-icon {
    width: 18px;
    height: 18px;
    color: #cbd5e1;
  }
  .notification-badge {
    position: absolute;
    top: 4px;
    right: 4px;
    min-width: 18px;
    height: 18px;
    background: linear-gradient(145deg, #ef4444, #dc2626);
    border-radius: 9px;
    font-size: 10px;
    font-weight: 600;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 5px;
    box-shadow: 0 2px 4px rgba(239, 68, 68, 0.4);
  }
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px 6px 6px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-md);
  cursor: pointer;
  height: 42px;
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  &:hover {
    background: linear-gradient(145deg, #334155, #273548);
    border-color: #60a5fa;
    box-shadow:
      0 2px 8px rgba(0, 0, 0, 0.15),
      0 0 0 1px #60a5fa;
  }
  .user-avatar {
    width: 34px;
    height: 34px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);

    .avatar-icon {
      width: 18px;
      height: 18px;
      color: white;
    }
  }
  .user-name {
    font-size: 14px;
    color: #e2e8f0;
    font-weight: 600;
  }
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
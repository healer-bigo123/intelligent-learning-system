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
          <button class="notification-btn">
            <component :is="icons.Bell" class="bell-icon" />
            <span class="notification-badge">3</span>
          </button>
          <div class="user-menu">
            <div class="user-avatar">
              <component :is="icons.User" class="avatar-icon" />
            </div>
            <span class="user-name" v-if="!collapsedSidebar">用户昵称</span>
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
import { ref, computed } from 'vue'
import {
  Bot, LayoutDashboard, BookOpen, BarChart, User,
  MessageCircle, ChevronLeft, ChevronRight, Search, Bell
} from 'lucide-vue-next'

const icons = {
  Bot, LayoutDashboard, BookOpen, BarChart, User,
  MessageCircle, ChevronLeft, ChevronRight, Search, Bell
}

const collapsedSidebar = ref(false)

const menuItems = [
  { path: '/', label: '首页', icon: LayoutDashboard },
  { path: '/resources', label: '学习资源', icon: BookOpen },
  { path: '/records', label: '学习记录', icon: BarChart },
  { path: '/agent', label: '智能助手', icon: MessageCircle },
  { path: '/profile', label: '个人中心', icon: User }
]

const pageTitles: Record<string, { title: string; desc: string }> = {
  '/': { title: '学习仪表盘', desc: '查看您的学习进度和推荐内容' },
  '/resources': { title: '学习资源', desc: '发现优质的学习内容' },
  '/records': { title: '学习记录', desc: '追踪您的学习历程' },
  '/profile': { title: '个人中心', desc: '管理您的账户和设置' },
  '/agent': { title: '智能助手', desc: '与AI助手互动学习' }
}

const currentPageTitle = computed(() => pageTitles[window.location.pathname]?.title || '学习仪表盘')
const currentPageDesc = computed(() => pageTitles[window.location.pathname]?.desc || '')
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
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
  }

  .page-subtitle {
    font-size: 13px;
    color: var(--text-muted);
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
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  min-width: 200px;

  .search-icon {
    width: 16px;
    height: 16px;
    color: var(--text-muted);
  }

  .search-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--text-primary);
    font-size: 13px;

    &::placeholder {
      color: var(--text-muted);
    }
  }
}

.notification-btn {
  position: relative;
  width: 40px;
  height: 40px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: var(--bg-card);
    border-color: var(--primary-color);
  }

  .bell-icon {
    width: 18px;
    height: 18px;
    color: var(--text-secondary);
  }

  .notification-badge {
    position: absolute;
    top: 6px;
    right: 6px;
    min-width: 16px;
    height: 16px;
    background: var(--error-color);
    border-radius: 8px;
    font-size: 10px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 4px;
  }
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px 6px 6px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;

  &:hover {
    background: var(--bg-card);
    border-color: var(--primary-color);
  }

  .user-avatar {
    width: 32px;
    height: 32px;
    background: var(--primary-color);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;

    .avatar-icon {
      width: 16px;
      height: 16px;
      color: white;
    }
  }

  .user-name {
    font-size: 13px;
    color: var(--text-primary);
    font-weight: 500;
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
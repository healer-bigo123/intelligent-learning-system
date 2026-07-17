<template>
  <div class="notifications">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载通知...</p>
    </div>

    <template v-else>
    <!-- 顶部统计栏 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">全部通知</span>
        <span class="stat-count all">{{ notifications.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">未读</span>
        <span class="stat-count unread">{{ unreadCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">已读</span>
        <span class="stat-count read">{{ readCount }}</span>
      </div>
      <button class="mark-all-btn" @click="markAllAsRead" :disabled="unreadCount === 0">
        <component :is="icons.CheckSquare" class="mark-all-icon" />
        全部标为已读
      </button>
    </div>

    <!-- Tab 筛选 -->
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="tab-btn"
        :class="{ active: activeTab === tab.value }"
        @click="onTabChange(tab.value)"
      >
        {{ tab.label }}
        <span class="tab-badge" v-if="tab.value === 'unread' && unreadCount > 0">
          {{ unreadCount }}
        </span>
      </button>
    </div>

    <!-- 通知列表（按日期分组） -->
    <div class="notification-groups" v-if="filteredGroups.length > 0">
      <div class="notification-group" v-for="group in filteredGroups" :key="group.label">
        <div class="group-header">
          <span class="group-label">{{ group.label }}</span>
          <span class="group-count">{{ group.items.length }} 条通知</span>
        </div>

        <div
          class="notification-item"
          v-for="item in group.items"
          :key="item.id"
          :class="{ unread: !item.read }"
          @click="markAsRead(item)"
        >
          <div class="notification-icon" :class="item.type">
            <component :is="getTypeIcon(item.type)" class="icon" />
          </div>

          <div class="notification-content">
            <div class="notification-title">{{ item.title }}</div>
            <div class="notification-desc">{{ item.description }}</div>
          </div>

          <div class="notification-meta">
            <span class="notification-time">{{ item.timeAgo }}</span>
            <span class="unread-dot" v-if="!item.read"></span>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more">
        <button @click="loadMore" :disabled="loadingMore">
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <component :is="icons.Bell" class="empty-icon" />
      <p class="empty-text">暂无{{ activeTab === 'all' ? '' : activeTab === 'unread' ? '未读' : '已读' }}通知</p>
    </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Bell, CheckCircle, BookOpen, Award, FileText, Settings, CheckSquare } from 'lucide-vue-next'
import { getNotifications, getUnreadCount, markAsRead as markAsReadApi, markAllAsRead as markAllAsReadApi, type NotificationItem } from '@/api/notifications'

const icons = { Bell, CheckCircle, BookOpen, Award, FileText, Settings, CheckSquare }

type NotificationType = 'system' | 'course' | 'achievement' | 'homework' | 'exercise' | 'reminder' | 'update'

interface Notification {
  id: string
  type: NotificationType
  title: string
  description: string
  timeAgo: string
  read: boolean
  createdAt: Date
}

const typeIconMap: Record<string, any> = {
  system: Settings,
  course: BookOpen,
  achievement: Award,
  homework: FileText,
  exercise: CheckCircle,
  reminder: Bell,
  update: FileText
}

const getTypeIcon = (type: string) => typeIconMap[type] || Bell

const tabs: { label: string; value: 'all' | 'unread' | 'read' }[] = [
  { label: '全部', value: 'all' },
  { label: '未读', value: 'unread' },
  { label: '已读', value: 'read' }
]

const activeTab = ref<'all' | 'unread' | 'read'>('all')
const loading = ref(true)
const notifications = ref<Notification[]>([])
const unreadCount = ref(0)
const readCount = computed(() => notifications.value.filter(n => n.read).length)

// 分页
const page = ref(1)
const pageSize = 20
const hasMore = ref(true)
const loadingMore = ref(false)

// 计算相对时间
function getTimeAgo(dateStr: string): string {
  const now = new Date()
  const date = new Date(dateStr)
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 30) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

// 加载通知列表
async function loadNotifications(isAppend = false) {
  if (isAppend) {
    loadingMore.value = true
  } else {
    loading.value = true
  }

  try {
    const params: { page: number; page_size: number; is_read?: boolean } = {
      page: isAppend ? page.value : 1,
      page_size: pageSize
    }

    if (activeTab.value === 'unread') params.is_read = false
    else if (activeTab.value === 'read') params.is_read = true

    const res = await getNotifications(params)

    const newNotifications: Notification[] = res.items.map(item => ({
      id: item.id,
      type: item.type as NotificationType,
      title: item.title,
      description: item.content,
      timeAgo: getTimeAgo(item.created_at),
      read: item.is_read,
      createdAt: new Date(item.created_at)
    }))

    if (isAppend) {
      notifications.value = [...notifications.value, ...newNotifications]
    } else {
      notifications.value = newNotifications
    }

    hasMore.value = notifications.value.length < res.total
    if (isAppend) page.value++
  } catch (e) {
    console.error('加载通知失败:', e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// 加载未读数
async function loadUnreadCount() {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.count
  } catch (e) {
    console.error('加载未读数失败:', e)
  }
}

// 标记单条已读
const markAsRead = async (item: Notification) => {
  if (item.read) return
  try {
    await markAsReadApi(item.id)
    item.read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (e) {
    console.error('标记已读失败:', e)
  }
}

// 全部标为已读
const markAllAsRead = async () => {
  try {
    await markAllAsReadApi()
    notifications.value.forEach(n => { n.read = true })
    unreadCount.value = 0
  } catch (e) {
    console.error('全部标为已读失败:', e)
  }
}

// 加载更多
const loadMore = () => {
  if (!loadingMore.value && hasMore.value) {
    loadNotifications(true)
  }
}

// Tab切换时重新加载
const onTabChange = (tab: 'all' | 'unread' | 'read') => {
  activeTab.value = tab
  page.value = 1
  notifications.value = []
  loadNotifications()
}

// 日期分组
interface NotificationGroup {
  label: string
  items: Notification[]
}

const filteredGroups = computed<NotificationGroup[]>(() => {
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const yesterdayStart = todayStart - 86400000

  const groups: Record<string, Notification[]> = {}

  notifications.value.forEach(item => {
    const ts = item.createdAt.getTime()
    let label: string
    if (ts >= todayStart) {
      label = '今天'
    } else if (ts >= yesterdayStart) {
      label = '昨天'
    } else {
      label = '更早'
    }
    if (!groups[label]) groups[label] = []
    groups[label].push(item)
  })

  const order = ['今天', '昨天', '更早']
  return order.filter(label => groups[label]?.length).map(label => ({
    label,
    items: groups[label]
  }))
})

onMounted(() => {
  loadNotifications()
  loadUnreadCount()
})
</script>

<style lang="scss" scoped>
.notifications {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

// 顶部统计栏
.stats-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 16px 24px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.9), rgba(26, 37, 52, 0.95));
  border: 1px solid rgba(71, 85, 105, 0.6);
  border-radius: var(--radius-lg, 16px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary, #a0a0b0);
}

.stat-count {
  font-size: 20px;
  font-weight: 700;
  &.all { color: var(--primary-color, #6366f1); }
  &.unread { color: #3b82f6; }
  &.read { color: var(--success-color, #10b981); }
}

.mark-all-btn {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: var(--radius-md, 12px);
  color: var(--primary-color, #6366f1);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;

  &:hover:not(:disabled) {
    background: rgba(99, 102, 241, 0.25);
    border-color: rgba(99, 102, 241, 0.5);
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.mark-all-icon {
  width: 16px;
  height: 16px;
}

// Tab 筛选
.tab-bar {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.9), rgba(26, 37, 52, 0.95));
  border: 1px solid rgba(71, 85, 105, 0.6);
  border-radius: 10px;
  width: fit-content;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
}

.tab-btn {
  position: relative;
  padding: 9px 24px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgba(148, 163, 184, 0.7);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  gap: 6px;

  &:hover {
    color: rgba(148, 163, 184, 1);
    background: rgba(255, 255, 255, 0.04);
  }

  &.active {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(99, 102, 241, 0.15));
    color: #fff;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
  }
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #3b82f6;
  border-radius: 9px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

// 通知分组
.notification-groups {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.notification-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px 8px;
  border-bottom: 1px solid rgba(71, 85, 105, 0.3);
}

.group-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #fff);
}

.group-count {
  font-size: 12px;
  color: var(--text-muted, #6b7280);
}

// 通知项
.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 18px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg, 12px);
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  &:hover {
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    transform: translateY(-1px);
  }

  &.unread {
    background: linear-gradient(145deg, rgba(59, 130, 246, 0.1), rgba(40, 54, 71, 0.98));
    border-color: rgba(59, 130, 246, 0.25);
  }
}

// 通知图标
.notification-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;

  .icon {
    width: 20px;
    height: 20px;
  }

  &.system {
    background: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
  }

  &.course {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
  }

  &.achievement {
    background: rgba(234, 179, 8, 0.15);
    color: #eab308;
  }

  &.homework {
    background: rgba(139, 92, 246, 0.15);
    color: #8b5cf6;
  }
}

// 通知内容
.notification-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #fff);
  line-height: 1.4;
}

.notification-desc {
  font-size: 13px;
  color: var(--text-secondary, #a0a0b0);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

// 通知元信息
.notification-meta {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.notification-time {
  font-size: 12px;
  color: var(--text-muted, #6b7280);
  white-space: nowrap;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3b82f6;
  box-shadow: 0 0 6px rgba(59, 130, 246, 0.5);
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.empty-icon {
  width: 56px;
  height: 56px;
  color: var(--text-muted, #6b7280);
  opacity: 0.4;
}

.empty-text {
  font-size: 14px;
  color: var(--text-muted, #6b7280);
}

// 加载状态
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(71, 85, 105, 0.3);
    border-top-color: rgba(99, 102, 241, 0.8);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  p {
    font-size: 14px;
    color: var(--text-muted, #6b7280);
  }
}

// 加载更多
.load-more {
  display: flex;
  justify-content: center;
  padding: 20px 0;

  button {
    padding: 10px 32px;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: var(--radius-md, 12px);
    color: var(--primary-color, #6366f1);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s ease;

    &:hover:not(:disabled) {
      background: rgba(99, 102, 241, 0.2);
      border-color: rgba(99, 102, 241, 0.5);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

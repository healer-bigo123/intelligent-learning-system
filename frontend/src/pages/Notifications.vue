<template>
  <div class="notifications">
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
        @click="activeTab = tab.value"
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
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <component :is="icons.Bell" class="empty-icon" />
      <p class="empty-text">暂无{{ activeTab === 'all' ? '' : activeTab === 'unread' ? '未读' : '已读' }}通知</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Bell, CheckCircle, BookOpen, Award, FileText, Settings, CheckSquare } from 'lucide-vue-next'

const icons = { Bell, CheckCircle, BookOpen, Award, FileText, Settings, CheckSquare }

type NotificationType = 'system' | 'course' | 'achievement' | 'homework'

interface Notification {
  id: number
  type: NotificationType
  title: string
  description: string
  timeAgo: string
  read: boolean
  createdAt: Date
}

const typeIconMap: Record<NotificationType, any> = {
  system: Settings,
  course: BookOpen,
  achievement: Award,
  homework: FileText
}

const getTypeIcon = (type: NotificationType) => typeIconMap[type]

const tabs: { label: string; value: 'all' | 'unread' | 'read' }[] = [
  { label: '全部', value: 'all' },
  { label: '未读', value: 'unread' },
  { label: '已读', value: 'read' }
]

const activeTab = ref<'all' | 'unread' | 'read'>('all')

const now = new Date()
const minutesAgo = (m: number) => new Date(now.getTime() - m * 60 * 1000)

const notifications = ref<Notification[]>([
  {
    id: 1,
    type: 'achievement',
    title: '🎉 成就解锁：连续学习 7 天',
    description: '恭喜！你已连续学习 7 天，超越了 85% 的用户，继续加油！',
    timeAgo: '5分钟前',
    read: false,
    createdAt: minutesAgo(5)
  },
  {
    id: 2,
    type: 'homework',
    title: '作业提醒：高等数学期中测验',
    description: '《高等数学》期中测验将于明天 9:00 开始，请提前做好准备。',
    timeAgo: '30分钟前',
    read: false,
    createdAt: minutesAgo(30)
  },
  {
    id: 3,
    type: 'course',
    title: '课程更新：Python 进阶编程 第8章',
    description: '你关注的《Python 进阶编程》已更新第8章「装饰器与元类」，快来学习吧。',
    timeAgo: '1小时前',
    read: false,
    createdAt: minutesAgo(60)
  },
  {
    id: 4,
    type: 'system',
    title: '系统维护通知',
    description: '平台将于本周六凌晨 2:00-4:00 进行系统维护升级，届时部分功能可能暂时不可用。',
    timeAgo: '2小时前',
    read: false,
    createdAt: minutesAgo(120)
  },
  {
    id: 5,
    type: 'course',
    title: '直播提醒：AI 辅导答疑课',
    description: '今晚 20:00 有一场 AI 辅导答疑直播课，主讲老师将在线解答你的疑问。',
    timeAgo: '3小时前',
    read: true,
    createdAt: minutesAgo(180)
  },
  {
    id: 6,
    type: 'achievement',
    title: '🏆 成就解锁：完成 100 道练习',
    description: '太棒了！你已累计完成 100 道练习题，学习进度超越 90% 的同学。',
    timeAgo: '昨天 18:30',
    read: true,
    createdAt: minutesAgo(60 * 18)
  },
  {
    id: 7,
    type: 'homework',
    title: '作业批改完成：线性代数第三章',
    description: '你提交的《线性代数》第三章作业已批改完成，得分 92 分，点击查看详细反馈。',
    timeAgo: '昨天 14:20',
    read: true,
    createdAt: minutesAgo(60 * 22)
  },
  {
    id: 8,
    type: 'system',
    title: '新功能上线：智能错题本',
    description: '我们上线了全新的智能错题本功能，系统会自动收集你的错题并生成针对性练习。',
    timeAgo: '昨天 10:00',
    read: true,
    createdAt: minutesAgo(60 * 26)
  },
  {
    id: 9,
    type: 'course',
    title: '课程推荐：机器学习入门',
    description: '根据你的学习记录，我们推荐你学习《机器学习入门》课程，适合你的当前水平。',
    timeAgo: '3天前',
    read: true,
    createdAt: minutesAgo(60 * 24 * 3)
  },
  {
    id: 10,
    type: 'achievement',
    title: '⭐ 成就解锁：本周学习之星',
    description: '你本周累计学习时长达到 20 小时，荣获「本周学习之星」称号！',
    timeAgo: '5天前',
    read: true,
    createdAt: minutesAgo(60 * 24 * 5)
  }
])

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)
const readCount = computed(() => notifications.value.filter(n => n.read).length)

const filteredNotifications = computed(() => {
  if (activeTab.value === 'unread') return notifications.value.filter(n => !n.read)
  if (activeTab.value === 'read') return notifications.value.filter(n => n.read)
  return notifications.value
})

interface NotificationGroup {
  label: string
  items: Notification[]
}

const filteredGroups = computed<NotificationGroup[]>(() => {
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const yesterdayStart = todayStart - 86400000

  const groups: Record<string, Notification[]> = {}

  filteredNotifications.value.forEach(item => {
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

const markAsRead = (item: Notification) => {
  item.read = true
}

const markAllAsRead = () => {
  notifications.value.forEach(n => { n.read = true })
}
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
  background: var(--bg-card, #16213e);
  border: 1px solid var(--border-color, #374151);
  border-radius: var(--radius-md, 12px);
  cursor: pointer;
  transition: all 0.25s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transform: translateY(-1px);
  }

  &.unread {
    background: linear-gradient(145deg, rgba(59, 130, 246, 0.06), rgba(22, 33, 62, 0.95));
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
</style>

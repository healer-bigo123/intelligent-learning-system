<template>
  <div class="profile">
    <!-- 用户信息卡片 -->
    <div class="profile-card">
      <div class="profile-header">
        <div class="avatar-section">
          <div class="avatar" :style="{ background: avatarColor }">
            <component :is="icons.User" class="avatar-icon" />
          </div>
          <div class="avatar-badge">
            <component :is="icons.Camera" class="badge-icon" />
          </div>
        </div>
        <div class="user-info">
          <h2 class="user-name">{{ user.name }}</h2>
          <p class="user-title">{{ user.title }}</p>
          <div class="user-stats">
            <span class="stat-item">
              <span class="stat-value">{{ user.courses }}</span>
              <span class="stat-label">已学课程</span>
            </span>
            <span class="stat-divider"></span>
            <span class="stat-item">
              <span class="stat-value">{{ user.hours }}h</span>
              <span class="stat-label">学习时长</span>
            </span>
            <span class="stat-divider"></span>
            <span class="stat-item">
              <span class="stat-value">{{ user.streak }}</span>
              <span class="stat-label">连续天数</span>
            </span>
          </div>
        </div>
      </div>

      <div class="profile-actions">
        <button class="action-btn primary">
          <component :is="icons.Pencil" class="btn-icon" />
          编辑资料
        </button>
        <button class="action-btn secondary">
          <component :is="icons.Share2" class="btn-icon" />
          分享主页
        </button>
      </div>
    </div>

    <div class="profile-content">
      <!-- 左侧设置菜单 -->
      <div class="settings-sidebar">
        <div class="menu-section">
          <h3 class="section-title">账户设置</h3>
          <nav class="settings-menu">
            <button
              v-for="item in menuItems"
              :key="item.id"
              class="menu-item"
              :class="{ active: activeMenu === item.id }"
              @click="activeMenu = item.id"
            >
              <component :is="item.icon" class="menu-icon" />
              <span class="menu-text">{{ item.label }}</span>
            </button>
          </nav>
        </div>
      </div>

      <!-- 右侧内容区域 -->
      <div class="settings-content">
        <!-- 个人资料 -->
        <div v-if="activeMenu === 'profile'" class="content-section">
          <div class="content-header">
            <h2 class="content-title">个人资料</h2>
          </div>

          <form class="profile-form">
            <div class="form-row">
              <div class="form-group">
                <label>用户名</label>
                <input type="text" v-model="formData.username" class="form-input" />
              </div>
              <div class="form-group">
                <label>昵称</label>
                <input type="text" v-model="formData.nickname" class="form-input" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>邮箱</label>
                <input type="email" v-model="formData.email" class="form-input" />
              </div>
              <div class="form-group">
                <label>手机号</label>
                <input type="tel" v-model="formData.phone" class="form-input" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group full-width">
                <label>个人简介</label>
                <textarea v-model="formData.bio" rows="4" class="form-textarea"></textarea>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn-cancel">取消</button>
              <button type="submit" class="btn-save">保存更改</button>
            </div>
          </form>
        </div>

        <!-- 学习目标 -->
        <div v-if="activeMenu === 'goals'" class="content-section">
          <div class="content-header">
            <h2 class="content-title">学习目标</h2>
            <button class="add-btn">
              <component :is="icons.Plus" class="add-icon" />
              添加目标
            </button>
          </div>

          <div class="goals-list">
            <div v-for="goal in goals" :key="goal.id" class="goal-card">
              <div class="goal-header">
                <div class="goal-icon" :style="{ background: goal.color }">
                  <component :is="goal.icon" class="icon" />
                </div>
                <div class="goal-info">
                  <h3 class="goal-title">{{ goal.title }}</h3>
                  <p class="goal-desc">{{ goal.description }}</p>
                </div>
              </div>
              <div class="goal-progress">
                <div class="progress-header">
                  <span class="progress-label">完成进度</span>
                  <span class="progress-value">{{ goal.progress }}%</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: goal.progress + '%', background: goal.color }"></div>
                </div>
              </div>
              <div class="goal-footer">
                <span class="goal-deadline">截止日期: {{ goal.deadline }}</span>
                <button class="goal-action">
                  <component :is="icons.MoreHorizontal" class="action-icon" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 成就墙 -->
        <div v-if="activeMenu === 'achievements'" class="content-section">
          <div class="content-header">
            <h2 class="content-title">我的成就</h2>
            <button class="add-btn" @click="$router.push('/achievements')">
              <component :is="icons.ChevronRight" class="add-icon" />
              查看全部
            </button>
          </div>

          <div class="achievements-grid">
            <div v-for="achievement in myAchievements" :key="achievement.id" class="achievement-card">
              <div class="achievement-icon" :style="{ background: achievement.color }">
                <component :is="achievement.icon" class="icon" />
              </div>
              <div class="achievement-info">
                <h3 class="achievement-title">{{ achievement.title }}</h3>
                <p class="achievement-desc">{{ achievement.description }}</p>
              </div>
              <div class="achievement-status" :class="{ unlocked: achievement.unlocked }">
                {{ achievement.unlocked ? '已解锁' : '未解锁' }}
              </div>
            </div>
          </div>
        </div>

        <!-- 通知设置 -->
        <div v-if="activeMenu === 'notifications'" class="content-section">
          <div class="content-header">
            <h2 class="content-title">通知设置</h2>
          </div>

          <div class="notifications-list">
            <div v-for="notification in notifications" :key="notification.id" class="notification-item">
              <div class="notification-info">
                <h3 class="notification-title">{{ notification.title }}</h3>
                <p class="notification-desc">{{ notification.description }}</p>
              </div>
              <div class="notification-toggle">
                <button 
                  class="toggle-btn"
                  :class="{ active: notification.enabled }"
                  @click="notification.enabled = !notification.enabled"
                >
                  <span class="toggle-thumb"></span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 隐私设置 -->
        <div v-if="activeMenu === 'privacy'" class="content-section">
          <div class="content-header">
            <h2 class="content-title">隐私设置</h2>
          </div>

          <div class="privacy-list">
            <div v-for="privacy in privacySettings" :key="privacy.id" class="privacy-item">
              <div class="privacy-info">
                <h3 class="privacy-title">{{ privacy.title }}</h3>
                <p class="privacy-desc">{{ privacy.description }}</p>
              </div>
              <div class="privacy-toggle">
                <button 
                  class="toggle-btn"
                  :class="{ active: privacy.enabled }"
                  @click="privacy.enabled = !privacy.enabled"
                >
                  <span class="toggle-thumb"></span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 安全设置 -->
        <div v-if="activeMenu === 'security'" class="content-section">
          <div class="content-header">
            <h2 class="content-title">安全设置</h2>
          </div>

          <div class="security-list">
            <div v-for="item in securityOptions" :key="item.id" class="security-item">
              <div class="security-info">
                <component :is="item.icon" class="security-icon" />
                <div class="security-text">
                  <h3 class="security-title">{{ item.title }}</h3>
                  <p class="security-desc">{{ item.description }}</p>
                </div>
              </div>
              <button class="security-action">{{ item.action }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  User, Camera, Pencil, Share2, Settings, Target, Bell,
  Shield, ChevronRight, Plus, MoreHorizontal, Lock,
  Key, Mail, AlertCircle, Award
} from 'lucide-vue-next'

const icons = {
  User, Camera, Pencil, Share2, Settings, Target, Bell,
  Shield, ChevronRight, Plus, MoreHorizontal, Lock,
  Key, Mail, AlertCircle, Award
}

const avatarColor = '#6366f1'

const user = ref({
  name: '学习者小明',
  title: '勤奋的学习者',
  courses: 12,
  hours: 156,
  streak: 15
})

const activeMenu = ref('profile')

const menuItems = [
  { id: 'profile', label: '个人资料', icon: User },
  { id: 'goals', label: '学习目标', icon: Target },
  { id: 'achievements', label: '成就墙', icon: Award },
  { id: 'notifications', label: '通知设置', icon: Bell },
  { id: 'privacy', label: '隐私设置', icon: Shield },
  { id: 'security', label: '安全设置', icon: Lock }
]

const formData = ref({
  username: 'learner_xm',
  nickname: '学习者小明',
  email: 'learner@example.com',
  phone: '138****8888',
  bio: '热爱学习，每天进步一点点！'
})

const goals = ref([
  {
    id: 1,
    title: '完成高等数学课程',
    description: '掌握微积分基础知识，为大学学习打下基础',
    progress: 75,
    deadline: '2026-08-31',
    color: '#3b82f6',
    icon: Target
  },
  {
    id: 2,
    title: 'Python编程入门',
    description: '学习Python基础语法，能够独立编写简单程序',
    progress: 45,
    deadline: '2026-09-15',
    color: '#10b981',
    icon: Settings
  },
  {
    id: 3,
    title: '英语四级备考',
    description: '提高英语水平，通过大学英语四级考试',
    progress: 30,
    deadline: '2026-12-20',
    color: '#f59e0b',
    icon: Target
  }
])

const notifications = ref([
  { id: 1, title: '学习提醒', description: '每日学习计划提醒', enabled: true },
  { id: 2, title: '课程更新', description: '关注的课程有新内容时通知', enabled: true },
  { id: 3, title: '成就通知', description: '获得新成就时通知', enabled: true },
  { id: 4, title: '社区互动', description: '有人评论或回复您的内容', enabled: false },
  { id: 5, title: '周报推送', description: '每周学习总结报告', enabled: true }
])

const privacySettings = ref([
  { id: 1, title: '公开学习动态', description: '允许他人查看您的学习动态', enabled: true },
  { id: 2, title: '公开学习时长', description: '在个人主页显示学习时长', enabled: true },
  { id: 3, title: '允许被关注', description: '允许其他用户关注您', enabled: true },
  { id: 4, title: '推荐给好友', description: '可能将您推荐给其他用户', enabled: false }
])

const securityOptions = ref([
  { id: 1, title: '修改密码', description: '定期更新密码以保护账户安全', icon: Lock, action: '修改' },
  { id: 2, title: '绑定手机号', description: '已绑定: 138****8888', icon: Key, action: '更换' },
  { id: 3, title: '绑定邮箱', description: '已绑定: learner@example.com', icon: Mail, action: '更换' },
  { id: 4, title: '登录设备管理', description: '查看并管理当前登录的设备', icon: AlertCircle, action: '管理' }
])

const myAchievements = ref([
  { id: 1, title: '首次登录', description: '第一次成功登录学习平台', icon: Award, color: '#f59e0b', unlocked: true },
  { id: 2, title: '连续学习7天', description: '连续7天保持学习打卡', icon: Target, color: '#10b981', unlocked: true },
  { id: 3, title: '完成100道题', description: '累计完成100道练习题', icon: Target, color: '#3b82f6', unlocked: true },
  { id: 4, title: '连续学习30天', description: '连续30天保持学习打卡', icon: Target, color: '#8b5cf6', unlocked: false },
  { id: 5, title: '完成500道题', description: '累计完成500道练习题', icon: Target, color: '#ec4899', unlocked: false },
  { id: 6, title: '全学科精通', description: '所有学科学习进度达到80%以上', icon: Award, color: '#f97316', unlocked: false }
])
</script>

<style lang="scss" scoped>
.profile {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.profile-header {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.avatar-section {
  position: relative;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;

  .avatar-icon {
    width: 56px;
    height: 56px;
    color: white;
  }
}

.avatar-badge {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  border: 3px solid var(--bg-secondary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }

  .badge-icon {
    width: 14px;
    height: 14px;
    color: white;
  }
}

.user-info {
  flex: 1;

  .user-name {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 8px;
  }

  .user-title {
    font-size: 14px;
    color: var(--text-muted);
    margin: 0 0 20px;
  }
}

.user-stats {
  display: flex;
  align-items: center;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;

  .stat-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary-color);
  }

  .stat-label {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: var(--border-color);
}

.profile-actions {
  display: flex;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &.primary {
    background: var(--primary-color);
    border: none;
    color: white;

    &:hover {
      background: var(--primary-dark);
    }
  }

  &.secondary {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);

    &:hover {
      background: var(--bg-card);
      border-color: var(--primary-color);
    }
  }

  .btn-icon {
    width: 16px;
    height: 16px;
  }
}

.profile-content {
  display: flex;
  gap: 24px;
}

.settings-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.menu-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-title {
  padding: 16px 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.settings-menu {
  padding: 8px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  &.active {
    background: rgba(99, 102, 241, 0.1);
    color: var(--primary-color);
  }

  .menu-icon {
    width: 18px;
    height: 18px;
  }
}

.settings-content {
  flex: 1;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  min-height: 500px;
}

.content-section {
  padding: 24px;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.content-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: var(--primary-color);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--primary-dark);
  }

  .add-icon {
    width: 14px;
    height: 14px;
  }
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group {
  flex: 1;

  &.full-width {
    flex: unset;
    width: 100%;
  }

  label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }

  .form-input,
  .form-textarea {
    width: 100%;
    padding: 12px 16px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: 14px;
    outline: none;
    transition: all 0.2s ease;

    &:focus {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }

    &::placeholder {
      color: var(--text-muted);
    }
  }

  .form-textarea {
    resize: vertical;
    min-height: 100px;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  padding: 12px 24px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-card);
  }
}

.btn-save {
  padding: 12px 24px;
  background: var(--primary-color);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--primary-dark);
  }
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.goal-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 20px;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
  }
}

.goal-header {
  display: flex;
  gap: 14px;
  margin-bottom: 16px;
}

.goal-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  .icon {
    width: 22px;
    height: 22px;
    color: white;
  }
}

.goal-info {
  flex: 1;

  .goal-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 4px;
  }

  .goal-desc {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0;
  }
}

.goal-progress {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;

  .progress-label {
    font-size: 12px;
    color: var(--text-muted);
  }

  .progress-value {
    font-size: 13px;
    font-weight: 600;
    color: var(--primary-color);
  }
}

.progress-bar {
  height: 8px;
  background: var(--bg-card);
  border-radius: 4px;
  overflow: hidden;

  .progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
  }
}

.goal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);

  .goal-deadline {
    font-size: 12px;
    color: var(--text-muted);
  }

  .goal-action {
    width: 32px;
    height: 32px;
    background: var(--bg-card);
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover {
      background: var(--border-color);
    }

    .action-icon {
      width: 16px;
      height: 16px;
      color: var(--text-muted);
    }
  }
}

.notifications-list,
.privacy-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item,
.privacy-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.notification-info,
.privacy-info {
  flex: 1;

  .notification-title,
  .privacy-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    margin: 0 0 4px;
  }

  .notification-desc,
  .privacy-desc {
    font-size: 12px;
    color: var(--text-muted);
    margin: 0;
  }
}

.toggle-btn {
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--border-color);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  &.active {
    background: var(--primary-color);

    .toggle-thumb {
      left: 22px;
    }
  }

  .toggle-thumb {
    position: absolute;
    top: 4px;
    left: 4px;
    width: 16px;
    height: 16px;
    background: white;
    border-radius: 50%;
    transition: left 0.2s ease;
  }
}

.security-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.security-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
  }
}

.security-info {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;

  .security-icon {
    width: 40px;
    height: 40px;
    padding: 10px;
    background: rgba(99, 102, 241, 0.1);
    border-radius: var(--radius-md);
    color: var(--primary-color);
  }

  .security-text {
    .security-title {
      font-size: 15px;
      font-weight: 500;
      color: var(--text-primary);
      margin: 0 0 4px;
    }

    .security-desc {
      font-size: 12px;
      color: var(--text-muted);
      margin: 0;
    }
  }
}

.security-action {
  padding: 10px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--primary-color);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
  }
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.achievement-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
  }

  .achievement-icon {
    width: 44px;
    height: 44px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .icon {
      width: 22px;
      height: 22px;
      color: white;
    }
  }

  .achievement-info {
    flex: 1;

    .achievement-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 4px;
    }

    .achievement-desc {
      font-size: 12px;
      color: var(--text-muted);
      margin: 0;
    }
  }

  .achievement-status {
    font-size: 12px;
    color: var(--text-muted);
    padding: 4px 10px;
    background: var(--bg-card);
    border-radius: 12px;
    flex-shrink: 0;

    &.unlocked {
      color: var(--primary-color);
      background: rgba(99, 102, 241, 0.1);
    }
  }
}
</style>
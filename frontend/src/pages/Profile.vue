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

          <form class="profile-form" @submit.prevent="handleSave">
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
            <button class="add-btn" @click="showAddGoalModal = true">
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
                <div class="goal-actions">
                  <button class="goal-action" @click="toggleGoalMenu(goal.id)">
                    <component :is="icons.MoreHorizontal" class="action-icon" />
                  </button>
                  <div v-if="activeGoalMenu === goal.id" class="goal-menu">
                    <button class="menu-item" @click="editGoal(goal)">
                      <component :is="icons.Pencil" class="menu-icon" />
                      编辑
                    </button>
                    <button class="menu-item danger" @click="deleteGoal(goal.id)">
                      <component :is="icons.Trash2" class="menu-icon" />
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 添加目标弹窗 -->
        <div v-if="showAddGoalModal" class="modal-overlay" @click.self="showAddGoalModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <h3>添加学习目标</h3>
              <button class="modal-close" @click="showAddGoalModal = false">
                <component :is="icons.X" class="close-icon" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>目标标题</label>
                <input v-model="newGoal.title" type="text" class="form-input" placeholder="请输入目标标题" />
              </div>
              <div class="form-group">
                <label>目标描述</label>
                <textarea v-model="newGoal.description" rows="3" class="form-textarea" placeholder="请输入目标描述"></textarea>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>目标颜色</label>
                  <div class="color-picker">
                    <button 
                      v-for="color in colorOptions" 
                      :key="color" 
                      class="color-btn" 
                      :class="{ active: newGoal.color === color }"
                      :style="{ background: color }"
                      @click="newGoal.color = color"
                    ></button>
                  </div>
                </div>
                <div class="form-group">
                  <label>截止日期</label>
                  <input v-model="newGoal.deadline" type="date" class="form-input" />
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="showAddGoalModal = false">取消</button>
              <button class="btn-save" @click="addGoal">添加目标</button>
            </div>
          </div>
        </div>

        <!-- 编辑目标弹窗 -->
        <div v-if="showEditGoalModal && editingGoal" class="modal-overlay" @click.self="showEditGoalModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <h3>编辑学习目标</h3>
              <button class="modal-close" @click="showEditGoalModal = false">
                <component :is="icons.X" class="close-icon" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>目标标题</label>
                <input v-model="editingGoal.title" type="text" class="form-input" placeholder="请输入目标标题" />
              </div>
              <div class="form-group">
                <label>目标描述</label>
                <textarea v-model="editingGoal.description" rows="3" class="form-textarea" placeholder="请输入目标描述"></textarea>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>目标颜色</label>
                  <div class="color-picker">
                    <button 
                      v-for="color in colorOptions" 
                      :key="color" 
                      class="color-btn" 
                      :class="{ active: editingGoal.color === color }"
                      :style="{ background: color }"
                      @click="editingGoal.color = color"
                    ></button>
                  </div>
                </div>
                <div class="form-group">
                  <label>截止日期</label>
                  <input v-model="editingGoal.deadline" type="date" class="form-input" />
                </div>
              </div>
              <div class="form-group">
                <label>完成进度</label>
                <input v-model.number="editingGoal.progress" type="range" min="0" max="100" class="progress-slider" />
                <span class="progress-display">{{ editingGoal.progress }}%</span>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="showEditGoalModal = false">取消</button>
              <button class="btn-save" @click="saveEditGoal">保存修改</button>
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
import { ref, onMounted } from 'vue'
import {
  User, Camera, Pencil, Share2, Settings, Target, Bell,
  Shield, ChevronRight, Plus, MoreHorizontal, Lock,
  Key, Mail, AlertCircle, Award, X, Trash2,
  Lightbulb, Cpu, Aperture, Search, Code, Globe, BookOpen
} from 'lucide-vue-next'
import { getProfile, updateProfile, type UserInfo } from '@/api/auth'

const icons = {
  User, Camera, Pencil, Share2, Settings, Target, Bell,
  Shield, ChevronRight, Plus, MoreHorizontal, Lock,
  Key, Mail, AlertCircle, Award, X, Trash2,
  Lightbulb, Cpu, Aperture, Search, Code, Globe, BookOpen
}

const avatarColor = '#6366f1'
const loading = ref(false)
const saving = ref(false)

const user = ref({
  name: '',
  title: '',
  courses: 0,
  hours: 0,
  streak: 0
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
  username: '',
  nickname: '',
  email: '',
  phone: '',
  bio: ''
})

async function loadProfile() {
  try {
    loading.value = true
    const res = await getProfile()
    const info: UserInfo = res.data
    user.value.name = info.nickname || info.username
    user.value.title = info.role === 'teacher' ? '教师' : '学生'
    formData.value = {
      username: info.username,
      nickname: info.nickname || '',
      email: info.email || '',
      phone: info.phone || '',
      bio: ''
    }
  } catch (e) {
    console.error('获取用户信息失败', e)
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  try {
    saving.value = true
    await updateProfile({
      nickname: formData.value.nickname,
      email: formData.value.email,
      phone: formData.value.phone,
    })
    user.value.name = formData.value.nickname || formData.value.username
    alert('保存成功')
  } catch (e: any) {
    alert(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})

interface Goal {
  id: number
  title: string
  description: string
  progress: number
  deadline: string
  color: string
  icon: any
}

const goals = ref<Goal[]>([
  {
    id: 1,
    title: '完成人工智能概述学习',
    description: '理解人工智能的基本概念、发展历程与典型应用领域',
    progress: 80,
    deadline: '2026-08-15',
    color: '#3b82f6',
    icon: BookOpen
  },
  {
    id: 2,
    title: '掌握搜索与推理基础',
    description: '掌握盲目搜索、启发式搜索及基本知识表示方法',
    progress: 60,
    deadline: '2026-08-31',
    color: '#f59e0b',
    icon: Search
  },
  {
    id: 3,
    title: '机器学习入门',
    description: '理解监督学习、无监督学习及常见机器学习算法原理',
    progress: 40,
    deadline: '2026-09-20',
    color: '#10b981',
    icon: Code
  },
  {
    id: 4,
    title: '深度学习基础',
    description: '掌握神经网络、CNN 与 RNN 的基本结构与训练方法',
    progress: 20,
    deadline: '2026-10-15',
    color: '#ef4444',
    icon: Cpu
  },
  {
    id: 5,
    title: '自然语言处理实践',
    description: '学习文本分类、序列标注与 Transformer 模型基础',
    progress: 0,
    deadline: '2026-11-01',
    color: '#8b5cf6',
    icon: Globe
  },
  {
    id: 6,
    title: '计算机视觉探索',
    description: '了解图像分类、目标检测与图像分割的基本方法',
    progress: 0,
    deadline: '2026-11-20',
    color: '#06b6d4',
    icon: Aperture
  },
  {
    id: 7,
    title: '理解人工智能伦理',
    description: '理解 AI 公平性、隐私保护、安全与社会影响等伦理议题',
    progress: 0,
    deadline: '2026-12-10',
    color: '#ec4899',
    icon: Shield
  }
])

const showAddGoalModal = ref(false)
const colorOptions = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#f97316']
const newGoal = ref({
  title: '',
  description: '',
  color: '#3b82f6',
  deadline: ''
})

function addGoal() {
  if (!newGoal.value.title.trim()) {
    alert('请输入目标标题')
    return
  }
  if (!newGoal.value.deadline) {
    alert('请选择截止日期')
    return
  }
  goals.value.push({
    id: Date.now(),
    title: newGoal.value.title,
    description: newGoal.value.description || '暂无描述',
    progress: 0,
    deadline: newGoal.value.deadline,
    color: newGoal.value.color,
    icon: Target
  })
  newGoal.value = { title: '', description: '', color: '#3b82f6', deadline: '' }
  showAddGoalModal.value = false
}

const activeGoalMenu = ref<number | null>(null)
const editingGoal = ref<Goal | null>(null)
const showEditGoalModal = ref(false)

function toggleGoalMenu(goalId: number) {
  activeGoalMenu.value = activeGoalMenu.value === goalId ? null : goalId
}

function deleteGoal(goalId: number) {
  if (confirm('确定要删除这个学习目标吗？')) {
    goals.value = goals.value.filter(g => g.id !== goalId)
    activeGoalMenu.value = null
  }
}

function editGoal(goal: Goal) {
  editingGoal.value = { ...goal }
  showEditGoalModal.value = true
  activeGoalMenu.value = null
}

function saveEditGoal() {
  if (!editingGoal.value) return
  if (!editingGoal.value.title.trim()) {
    alert('请输入目标标题')
    return
  }
  if (!editingGoal.value.deadline) {
    alert('请选择截止日期')
    return
  }
  const index = goals.value.findIndex(g => g.id === editingGoal.value!.id)
  if (index !== -1) {
    goals.value[index] = { ...editingGoal.value }
  }
  showEditGoalModal.value = false
  editingGoal.value = null
}

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
  { id: 1, title: 'AI 探索者', description: '完成「人工智能概述」章节学习', icon: Lightbulb, color: '#3b82f6', unlocked: true },
  { id: 2, title: '搜索大师', description: '完成「搜索与推理」章节学习', icon: Search, color: '#f59e0b', unlocked: true },
  { id: 3, title: '连续学习7天', description: '连续7天保持学习打卡', icon: Target, color: '#10b981', unlocked: true },
  { id: 4, title: '完成100道 AI 题', description: '累计完成100道人工智能导论练习题', icon: BookOpen, color: '#3b82f6', unlocked: true },
  { id: 5, title: '机器学习学徒', description: '完成「机器学习」章节学习', icon: Code, color: '#10b981', unlocked: false },
  { id: 6, title: '深度学习先锋', description: '完成「深度学习」章节学习', icon: Cpu, color: '#ef4444', unlocked: false },
  { id: 7, title: 'NLP 实践者', description: '完成「自然语言处理」章节学习', icon: Globe, color: '#8b5cf6', unlocked: false },
  { id: 8, title: 'CV 研究者', description: '完成「计算机视觉」章节学习', icon: Aperture, color: '#06b6d4', unlocked: false }
])
</script>

<style lang="scss" scoped>
.profile {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: linear-gradient(145deg, rgba(50, 65, 85, 0.98), rgba(30, 45, 65, 0.99));
  border: 2px solid rgba(99, 102, 241, 0.4);
  border-radius: var(--radius-lg);
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), 0 0 40px rgba(99, 102, 241, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.08);
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
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 8px;
    text-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
  }

  .user-title {
    font-size: 14px;
    color: #94a3b8;
    margin: 0 0 20px;
    font-weight: 500;
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
  padding: 16px 24px;
  background: rgba(99, 102, 241, 0.08);
  border-radius: var(--radius-md);
  border: 1px solid rgba(99, 102, 241, 0.2);

  .stat-value {
    font-size: 28px;
    font-weight: 800;
    color: #818cf8;
    text-shadow: 0 0 10px rgba(99, 102, 241, 0.4);
  }

  .stat-label {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 500;
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
  background: linear-gradient(145deg, rgba(50, 65, 85, 0.98), rgba(30, 45, 65, 0.99));
  border: 2px solid rgba(99, 102, 241, 0.4);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), 0 0 40px rgba(99, 102, 241, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.08);
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
  padding: 14px 18px;
  background: rgba(0, 0, 0, 0.1);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: #94a3b8;
  font-size: 14px;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(99, 102, 241, 0.12);
    color: #ffffff;
    border-color: rgba(99, 102, 241, 0.3);
  }

  &.active {
    background: rgba(99, 102, 241, 0.18);
    color: #818cf8;
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.15);
  }

  .menu-icon {
    width: 18px;
    height: 18px;
  }
}

.settings-content {
  flex: 1;
  background: linear-gradient(145deg, rgba(50, 65, 85, 0.98), rgba(30, 45, 65, 0.99));
  border: 2px solid rgba(99, 102, 241, 0.4);
  border-radius: var(--radius-lg);
  min-height: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), 0 0 40px rgba(99, 102, 241, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.08);
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
  background: linear-gradient(145deg, rgba(60, 75, 95, 0.95), rgba(40, 55, 75, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.6);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  &:hover {
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25), 0 0 20px rgba(99, 102, 241, 0.1);
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

  .goal-actions {
    position: relative;
    display: flex;
    align-items: center;

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

    .goal-menu {
      position: absolute;
      right: 0;
      top: 40px;
      background: linear-gradient(145deg, rgba(40, 54, 71, 0.98), rgba(26, 37, 52, 0.99));
      border: 2px solid rgba(71, 85, 105, 0.7);
      border-radius: var(--radius-md);
      padding: 6px;
      min-width: 120px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
      z-index: 100;

      .menu-item {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
        padding: 10px 12px;
        background: transparent;
        border: none;
        border-radius: var(--radius-sm);
        color: var(--text-primary);
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
          background: rgba(99, 102, 241, 0.1);
        }

        &.danger {
          color: #ef4444;

          &:hover {
            background: rgba(239, 68, 68, 0.1);
          }
        }

        .menu-icon {
          width: 14px;
          height: 14px;
        }
      }
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.98), rgba(26, 37, 52, 0.99));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 480px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  animation: slideUp 0.2s ease;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);

  h3 {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
  }
}

.modal-close {
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-tertiary);
    border-color: var(--primary-color);
  }

  .close-icon {
    width: 16px;
    height: 16px;
    color: var(--text-secondary);
  }
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  justify-content: flex-end;
}

.color-picker {
  display: flex;
  gap: 10px;

  .color-btn {
    width: 32px;
    height: 32px;
    border: 2px solid transparent;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s ease;

    &.active {
      border-color: #ffffff;
      transform: scale(1.15);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
    }

    &:hover {
      transform: scale(1.1);
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.progress-slider {
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: var(--bg-card);
  border-radius: 4px;
  cursor: pointer;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--primary-color);
    border-radius: 50%;
    cursor: pointer;
    border: 3px solid #ffffff;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
    transition: all 0.2s ease;

    &:hover {
      transform: scale(1.1);
    }
  }

  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--primary-color);
    border-radius: 50%;
    cursor: pointer;
    border: 3px solid #ffffff;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
  }
}

.progress-display {
  display: block;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-color);
  margin-top: 8px;
}</style>
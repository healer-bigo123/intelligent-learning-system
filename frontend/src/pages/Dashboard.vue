<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <component :is="icons.BookOpen" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalCourses }}</div>
          <div class="stat-label">学习课程</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon green">
          <component :is="icons.Clock" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalHours }}h</div>
          <div class="stat-label">累计学时</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon purple">
          <component :is="icons.Award" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.completedTasks }}</div>
          <div class="stat-label">完成任务</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon orange">
          <component :is="icons.TrendingUp" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.streakDays }}天</div>
          <div class="stat-label">连续学习</div>
        </div>
      </div>
    </div>

    <!-- 今日任务和学习进度 -->
    <div class="row-section">
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">
            <component :is="icons.ListChecks" class="title-icon" />
            今日任务
          </h3>
          <span class="task-count">{{ todayTasks.length }} 项待完成</span>
        </div>

        <div class="task-scroll-container">
          <div class="task-scroll-wrapper" ref="taskScrollRef">
            <div class="task-cards">
              <div
                v-for="task in todayTasks"
                :key="task.id"
                class="task-card"
                :class="{ completed: task.completed, urgent: task.priority === 'high' }"
              >
                <div class="task-card-header">
                  <div 
                    class="task-checkbox" 
                    :class="{ checked: task.completed }"
                    @click.stop="toggleTask(task.id)"
                  >
                    <component :is="icons.Check" class="check-icon" v-if="task.completed" />
                  </div>
                  <div class="task-priority" :class="task.priority">
                    {{ task.priority === 'high' ? '紧急' : task.priority === 'medium' ? '中等' : '普通' }}
                  </div>
                  <button 
                    class="task-delete-btn" 
                    @click.stop="deleteTask(task.id)"
                    title="删除任务"
                  >
                    <component :is="icons.Trash2" class="delete-icon" />
                  </button>
                </div>
                <div class="task-card-body" @click="toggleTask(task.id)">
                  <div class="task-title">{{ task.title }}</div>
                  <div class="task-meta">
                    <span class="task-subject">{{ task.subject }}</span>
                    <span class="task-time">{{ task.time }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 自定义滚动条 -->
          <div class="custom-scrollbar">
            <div 
              class="scrollbar-thumb" 
              :style="{ left: scrollProgress + '%' }"
              @mousedown="startDrag"
            ></div>
          </div>
        </div>
        
        <!-- 任务栏 -->
        <div class="add-task-bar">
          <input 
            v-model="newTaskTitle" 
            type="text" 
            class="task-input" 
            placeholder="添加新任务..."
            @keyup.enter="addTask"
          />
          <select v-model="newTaskSubject" class="task-select subject-select">
            <option value="数学">数学</option>
            <option value="英语">英语</option>
            <option value="物理">物理</option>
            <option value="化学">化学</option>
            <option value="综合">综合</option>
          </select>
          <select v-model="newTaskPriority" class="task-select priority-select">
            <option value="high">紧急</option>
            <option value="medium">中等</option>
            <option value="low">普通</option>
          </select>
          <button class="add-task-btn" @click="addTask">
            <component :is="icons.Plus" class="plus-icon" />
          </button>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">
            <component :is="icons.PieChart" class="title-icon" />
            学习内容分布
          </h3>
          <div class="range-selector">
            <button
              v-for="r in timeRanges"
              :key="r.value"
              class="range-btn"
              :class="{ active: selectedRange === r.value }"
              @click="selectedRange = r.value"
            >
              {{ r.label }}
            </button>
          </div>
        </div>

        <div class="distribution-chart">
          <div class="pie-chart-wrap">
            <svg class="pie-svg" viewBox="0 0 100 100">
              <circle
                v-for="(segment, index) in pieSegments"
                :key="index"
                cx="50"
                cy="50"
                r="40"
                :stroke="segment.color"
                stroke-width="40"
                :stroke-dasharray="segment.dashArray"
                :stroke-dashoffset="segment.dashOffset"
                transform="rotate(-90 50 50)"
                fill="none"
              />
            </svg>
            <div class="pie-center">
              <span class="pie-total">{{ distributionTotalHours }}h</span>
              <span class="pie-label">总计</span>
            </div>
          </div>
          <div class="pie-legend">
            <div
              v-for="item in contentDistribution"
              :key="item.name"
              class="legend-item"
            >
              <div class="legend-color" :style="{ background: item.color }"></div>
              <span class="legend-name">{{ item.name }}</span>
              <span class="legend-value">{{ item.percent }}%</span>
            </div>
            <div v-if="contentDistribution.length === 0" class="no-data">暂无学习数据</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 推荐课程和最近学习 -->
    <div class="row-section">
      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">
            <component :is="icons.Star" class="title-icon" />
            为你推荐
          </h3>
          <a href="/resources" class="view-all">查看全部</a>
        </div>

        <div class="course-list">
          <div v-for="course in recommendedCourses" :key="course.id" class="course-item">
            <div class="course-cover" :style="{ background: course.color }">
              <component :is="getCourseIcon(course.category)" class="cover-icon" />
            </div>
            <div class="course-info">
              <div class="course-title">{{ course.title }}</div>
              <div class="course-meta">
                <span class="course-instructor">{{ course.instructor }}</span>
                <span class="course-duration">{{ course.duration }}</span>
              </div>
              <div class="course-tags">
                <span v-for="tag in course.tags" :key="tag" class="course-tag">{{ tag }}</span>
              </div>
            </div>
            <button class="course-action">
              <component :is="icons.Play" class="play-icon" />
            </button>
          </div>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h3 class="section-title">
            <component :is="icons.History" class="title-icon" />
            最近学习
          </h3>
        </div>

        <div class="history-list">
          <div v-for="item in recentHistory" :key="item.id" class="history-item">
            <div class="history-cover" :style="{ background: item.color }">
              <component :is="getCourseIcon(item.category)" class="cover-icon" />
            </div>
            <div class="history-info">
              <div class="history-title">{{ item.title }}</div>
              <div class="history-progress">
                <div class="mini-progress-bar">
                  <div class="mini-progress-fill" :style="{ width: item.progress + '%' }"></div>
                </div>
                <span class="history-percent">{{ item.progress }}%</span>
              </div>
            </div>
            <div class="history-time">{{ item.time }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, type Component, onMounted, onUnmounted } from 'vue'
import {
  BookOpen, Clock, Award, TrendingUp, ListChecks, Target,
  Star, History, Check, Play, Calculator, MessageSquare,
  FlaskConical, Globe, Plus, Trash2, PieChart
} from 'lucide-vue-next'
import { api } from '@/api/client'

const icons = {
  BookOpen, Clock, Award, TrendingUp, ListChecks, Target,
  Star, History, Check, Play, Calculator, MessageSquare,
  FlaskConical, Globe, Plus, Trash2, PieChart
}

const courseIconMap: Record<string, Component> = {
  math: Calculator,
  english: Globe,
  physics: FlaskConical,
  chemistry: FlaskConical,
  programming: Code,
  default: BookOpen
}

import { Code } from 'lucide-vue-next'

const getCourseIcon = (category: string): Component => {
  return courseIconMap[category] || courseIconMap.default
}

const stats = ref({
  totalCourses: 0,
  totalHours: 0,
  completedTasks: 0,
  streakDays: 0,
  totalTasks: 0
})

const weeklyGoal = ref(78)

const todayTasks = ref<any[]>([])

const toggleTask = async (taskId: string) => {
  const task = todayTasks.value.find(t => t.id === taskId)
  if (!task) return

  const newStatus = task.completed ? 'pending' : 'completed'
  try {
    await api.put(`/tasks/${taskId}`, { status: newStatus })
    task.completed = !task.completed
    task.status = newStatus
    // 更新统计
    stats.value.completedTasks = todayTasks.value.filter(t => t.completed).length
  } catch (error) {
    console.error('更新任务状态失败:', error)
    alert('更新任务状态失败，请重试')
  }
}

const deleteTask = async (taskId: string) => {
  if (!confirm('确定要删除这个任务吗？')) return

  try {
    await api.delete(`/tasks/${taskId}`)
    const index = todayTasks.value.findIndex(t => t.id === taskId)
    if (index !== -1) {
      todayTasks.value.splice(index, 1)
    }
    // 更新统计
    stats.value.completedTasks = todayTasks.value.filter(t => t.completed).length
    stats.value.totalTasks = todayTasks.value.length
  } catch (error) {
    console.error('删除任务失败:', error)
    alert('删除任务失败，请重试')
  }
}

const taskScrollRef = ref<HTMLElement | null>(null)
const scrollProgress = ref(0)
const isDragging = ref(false)

const updateScrollProgress = () => {
  if (taskScrollRef.value) {
    const { scrollLeft, scrollWidth, clientWidth } = taskScrollRef.value
    const maxScroll = scrollWidth - clientWidth
    scrollProgress.value = maxScroll > 0 ? (scrollLeft / maxScroll) * 100 : 0
  }
}

const handleScroll = () => {
  updateScrollProgress()
}

const startDrag = (_e: MouseEvent) => {
  isDragging.value = true
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value || !taskScrollRef.value) return
  
  const scrollbar = taskScrollRef.value.parentElement?.querySelector('.custom-scrollbar')
  if (!scrollbar) return
  
  const rect = scrollbar.getBoundingClientRect()
  const x = e.clientX - rect.left
  const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100))
  
  const { scrollWidth, clientWidth } = taskScrollRef.value
  const maxScroll = scrollWidth - clientWidth
  taskScrollRef.value.scrollLeft = (percentage / 100) * maxScroll
  scrollProgress.value = percentage
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

const newTaskTitle = ref('')
const newTaskSubject = ref('数学')
const newTaskPriority = ref('medium')

const addTask = async () => {
  if (!newTaskTitle.value.trim()) return

  try {
    const response = await api.post('/tasks', {
      title: newTaskTitle.value.trim(),
      description: '',
      subject: newTaskSubject.value,
      priority: newTaskPriority.value
    })

    const newTask = response.data
    todayTasks.value.push({
      id: newTask.id,
      title: newTask.title,
      subject: newTask.subject,
      time: new Date(newTask.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      priority: newTask.priority,
      completed: newTask.status === 'completed',
      status: newTask.status
    })

    // 按优先级排序：紧急 > 中等 > 普通
    todayTasks.value.sort((a, b) => {
      const priorityOrder: Record<string, number> = { high: 0, medium: 1, low: 2 }
      return priorityOrder[a.priority] - priorityOrder[b.priority]
    })

    stats.value.totalTasks = todayTasks.value.length
    newTaskTitle.value = ''
  } catch (error) {
    console.error('添加任务失败:', error)
    alert('添加任务失败，请重试')
  }
}

const progressItems = ref([
  { name: '数学', percent: 0, color: '#3b82f6' },
  { name: '英语', percent: 0, color: '#10b981' },
  { name: '物理', percent: 0, color: '#f59e0b' },
  { name: '化学', percent: 0, color: '#ef4444' }
])

const recommendedCourses = ref<any[]>([])

const recentHistory = ref<any[]>([])

// ========== 学习内容分布（扇形图）==========
const timeRanges = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '全部', value: 'all' }
]

const selectedRange = ref('week')

const subjectColorMap: Record<string, string> = {
  '数学': '#3b82f6',
  '英语': '#f59e0b',
  '物理': '#10b981',
  '化学': '#ef4444',
  '编程': '#8b5cf6',
  '生物': '#06b6d4'
}

const fallbackColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

const contentDistribution = ref<{ name: string; percent: number; color: string; hours: number }[]>([])

const distributionTotalHours = computed(() =>
  Math.round(contentDistribution.value.reduce((sum, item) => sum + item.hours, 0) * 10) / 10
)

const pieSegments = computed(() => {
  let currentOffset = 0
  const circumference = 2 * Math.PI * 40
  return contentDistribution.value.map(item => {
    const percentage = item.percent
    const dashArray = `${(percentage / 100) * circumference} ${circumference}`
    const dashOffset = -currentOffset * (circumference / 100)
    currentOffset += percentage
    return { color: item.color, dashArray, dashOffset }
  })
})

const getDateRange = (range: string) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const endDate = new Date(today)
  endDate.setHours(23, 59, 59, 999)
  let startDate = new Date(today)
  switch (range) {
    case 'today': break
    case 'week': startDate.setDate(today.getDate() - 6); break
    case 'month': startDate.setDate(1); break
    case 'all': startDate = new Date('2000-01-01'); break
    default: startDate.setDate(today.getDate() - 6)
  }
  return {
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0]
  }
}

const inferSubject = (title: string): string => {
  const t = (title || '').toLowerCase()
  if (t.includes('python') || t.includes('编程') || t.includes('排序') || t.includes('程序') || t.includes('代码')) return '编程'
  if (t.includes('数学') || t.includes('函数') || t.includes('方程') || t.includes('几何') || t.includes('三角') || t.includes('代数')) return '数学'
  if (t.includes('英语') || t.includes('语法') || t.includes('阅读') || t.includes('词汇')) return '英语'
  if (t.includes('物理') || t.includes('力学') || t.includes('电场') || t.includes('运动') || t.includes('光学')) return '物理'
  if (t.includes('化学') || t.includes('物质') || t.includes('反应') || t.includes('元素')) return '化学'
  return '其他'
}

const loadDistributionData = async () => {
  try {
    const range = getDateRange(selectedRange.value)
    const res = await api.get('/timeline', {
      params: { start_date: range.start_date, end_date: range.end_date, page_size: 100 }
    })
    const activities = res.data?.items || []
    const subjectDuration: Record<string, number> = {}
    activities.forEach((a: any) => {
      const subject = inferSubject(a.title || '')
      subjectDuration[subject] = (subjectDuration[subject] || 0) + (a.duration || 0)
    })
    const totalDuration = Object.values(subjectDuration).reduce((sum, d) => sum + d, 0)
    contentDistribution.value = Object.entries(subjectDuration)
      .filter(([, d]) => d > 0)
      .sort(([, a], [, b]) => b - a)
      .map(([name, duration], index) => ({
        name,
        percent: totalDuration > 0 ? Math.round((duration / totalDuration) * 100) : 0,
        color: subjectColorMap[name] || fallbackColors[index % fallbackColors.length],
        hours: Math.round((duration / 3600) * 10) / 10
      }))
  } catch (error) {
    console.error('加载学习内容分布失败:', error)
    contentDistribution.value = []
  }
}

watch(selectedRange, () => { loadDistributionData() })

// 从后端加载数据
const loadDashboardData = async () => {
  try {
    // 并行加载多个数据源
    const [
      overviewRes,
      materialsRes,
      subjectsRes,
      timelineRes,
      tasksRes,
      taskStatsRes
    ] = await Promise.all([
      api.get('/analytics/overview'),
      api.get('/study-materials?page_size=100'),
      api.get('/analytics/subjects'),
      api.get('/timeline?page_size=20'),
      api.get('/tasks/today'),
      api.get('/tasks/stats')
    ])

    const overview = overviewRes.data || {}
    const materials = materialsRes.data?.items || []
    const subjectItems = subjectsRes.data?.items || []
    const activities = timelineRes.data?.items || []
    const taskItems = tasksRes.data?.items || []
    const taskStats = taskStatsRes.data || {}

    // 更新统计数据
    stats.value = {
      totalCourses: materials.length,
      totalHours: Math.round((overview.total_duration || 0) / 3600),
      completedTasks: taskStats.completed || 0,
      streakDays: overview.streak_days || 0,
      totalTasks: taskStats.total || 0
    }

    // 更新今日任务
    todayTasks.value = taskItems.map((t: any) => ({
      id: t.id,
      title: t.title,
      subject: t.subject,
      time: new Date(t.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      priority: t.priority,
      completed: t.status === 'completed',
      status: t.status
    }))

    // 更新推荐课程
    const colorList = [
      'linear-gradient(135deg, #3b82f6, #6366f1)',
      'linear-gradient(135deg, #10b981, #34d399)',
      'linear-gradient(135deg, #f59e0b, #fbbf24)'
    ]
    recommendedCourses.value = materials.slice(0, 3).map((r: any, index: number) => ({
      id: r.id,
      title: r.title,
      instructor: r.generated_by || '系统推荐',
      duration: `${r.duration || 30}分钟`,
      category: r.subject === '数学' ? 'math' : r.subject === '英语' ? 'english' : r.subject === '物理' ? 'physics' : r.subject === '化学' ? 'chemistry' : 'default',
      color: colorList[index % colorList.length],
      tags: r.tags || [r.subject, r.type || '课程']
    }))

    // 更新最近学习
    recentHistory.value = activities.slice(0, 4).map((a: any) => ({
      id: a.id,
      title: a.title || '学习活动',
      category: 'default',
      progress: Math.round(a.score || 0),
      time: new Date(a.created_at).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    }))

    // 更新学习进度（从学科成绩趋势）
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
    if (subjectItems.length > 0) {
      progressItems.value = subjectItems.slice(0, 4).map((item: any, index: number) => ({
        name: item.subject,
        percent: Math.round(item.accuracy_rate || 0),
        color: colors[index % colors.length]
      }))
    } else {
      progressItems.value = [
        { name: '数学', percent: 0, color: '#3b82f6' },
        { name: '英语', percent: 0, color: '#10b981' },
        { name: '物理', percent: 0, color: '#f59e0b' },
        { name: '化学', percent: 0, color: '#ef4444' }
      ]
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  if (taskScrollRef.value) {
    taskScrollRef.value.addEventListener('scroll', handleScroll)
    updateScrollProgress()
  }
  // 加载后端数据
  loadDashboardData()
  loadDistributionData()
})

onUnmounted(() => {
  if (taskScrollRef.value) {
    taskScrollRef.value.removeEventListener('scroll', handleScroll)
  }
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style lang="scss" scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    border-color: rgba(99, 102, 241, 0.5);
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

  &.blue { background: linear-gradient(145deg, rgba(99, 102, 241, 0.2), rgba(79, 70, 229, 0.1)); .icon { color: #818cf8; } }
  &.green { background: linear-gradient(145deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1)); .icon { color: #34d399; } }
  &.purple { background: linear-gradient(145deg, rgba(139, 92, 246, 0.2), rgba(126, 34, 206, 0.1)); .icon { color: #c084fc; } }
  &.orange { background: linear-gradient(145deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.1)); .icon { color: #fbbf24; } }

  .icon {
    width: 24px;
    height: 24px;
  }
}

.stat-info {
  .stat-value {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    line-height: 1.2;
  }

  .stat-label {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 4px;
    font-weight: 500;
  }
}

.row-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.section-card {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  overflow: hidden;
  min-height: auto;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(71, 85, 105, 0.4);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  color: rgba(241, 245, 249, 0.9);
  margin: 0;

  .title-icon {
    width: 18px;
    height: 18px;
    color: rgba(99, 102, 241, 0.7);
  }
}

.task-count {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.7);
  padding: 3px 10px;
  background: rgba(51, 65, 85, 0.5);
  border-radius: 10px;
}

.progress-text {
  font-size: 12px;
  color: rgba(99, 102, 241, 0.7);
  font-weight: 500;
}

.view-all {
  font-size: 11px;
  color: rgba(99, 102, 241, 0.7);
  text-decoration: none;

  &:hover {
    color: rgba(99, 102, 241, 0.9);
    text-decoration: underline;
  }
}

.task-scroll-container {
  padding: 24px 14px 4px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 180px;
  justify-content: center;
}

.task-scroll-wrapper {
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
  width: 100%;

  &::-webkit-scrollbar {
    display: none;
  }
}

.custom-scrollbar {
  width: 90%;
  height: 8px;
  background: rgba(51, 65, 85, 0.4);
  border-radius: 4px;
  margin-top: 12px;
  position: relative;
  cursor: pointer;

  &:hover {
    background: rgba(51, 65, 85, 0.5);
  }
}

.scrollbar-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 100%;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.7), rgba(139, 92, 246, 0.7));
  border-radius: 4px;
  cursor: grab;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: background 0.2s ease, transform 0.1s ease;

  &:hover {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.9), rgba(139, 92, 246, 0.9));
    transform: translate(-50%, -50%) scale(1.1);
  }

  &:active {
    cursor: grabbing;
    transform: translate(-50%, -50%) scale(1.15);
  }
}

.task-cards {
  display: flex;
  gap: 12px;
  padding-bottom: 12px;
}

.task-card {
  flex: 0 0 200px;
  padding: 14px;
  background: rgba(51, 65, 85, 0.4);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;

  &:hover {
    background: rgba(51, 65, 85, 0.6);
    transform: translateY(-2px);
  }

  &.completed {
    opacity: 0.5;

    .task-title {
      text-decoration: line-through;
    }
  }

  &.urgent {
    border-left-color: rgba(239, 68, 68, 0.7);
  }
}

.task-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.task-delete-btn {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0.4;
  transition: all 0.2s ease;
  margin-left: auto;

  &:hover {
    opacity: 1;
    background: rgba(239, 68, 68, 0.2);
  }

  .delete-icon {
    width: 12px;
    height: 12px;
    color: rgba(148, 163, 184, 0.8);
  }
}

.scroll-indicator {
  text-align: center;
  font-size: 10px;
  color: rgba(148, 163, 184, 0.5);
  margin-top: 6px;
}

.task-checkbox {
  width: 18px;
  height: 18px;
  border: 1.5px solid rgba(148, 163, 184, 0.5);
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &.checked {
    background: rgba(99, 102, 241, 0.6);
    border-color: rgba(99, 102, 241, 0.6);
  }

  .check-icon {
    width: 10px;
    height: 10px;
    color: rgba(255, 255, 255, 0.9);
  }
}

.task-content {
  flex: 1;

  .task-title {
    font-size: 13px;
    color: rgba(241, 245, 249, 0.85);
    margin-bottom: 4px;
  }

  .task-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 11px;

    .task-subject {
      color: rgba(99, 102, 241, 0.7);
      padding: 2px 7px;
      background: rgba(99, 102, 241, 0.1);
      border-radius: 3px;
    }

    .task-time {
      color: rgba(148, 163, 184, 0.6);
    }
  }
}

.task-priority {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 500;

  &.high {
    background: rgba(239, 68, 68, 0.1);
    color: rgba(239, 68, 68, 0.7);
  }

  &.medium {
    background: rgba(245, 158, 11, 0.1);
    color: rgba(245, 158, 11, 0.7);
  }

  &.low {
    background: rgba(16, 185, 129, 0.1);
    color: rgba(16, 185, 129, 0.7);
  }
}

.add-task-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid rgba(71, 85, 105, 0.4);
  background: rgba(15, 23, 42, 0.6);
}

.task-input {
  flex: 1;
  height: 34px;
  padding: 0 12px;
  background: rgba(51, 65, 85, 0.5);
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: var(--radius-sm);
  color: rgba(241, 245, 249, 0.9);
  font-size: 12px;
  outline: none;
  transition: all 0.2s ease;

  &::placeholder {
    color: rgba(148, 163, 184, 0.5);
  }

  &:focus {
    border-color: rgba(99, 102, 241, 0.6);
    background: rgba(51, 65, 85, 0.7);
  }
}

.task-select {
  height: 34px;
  padding: 0 10px;
  background: rgba(51, 65, 85, 0.5);
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: var(--radius-sm);
  color: rgba(241, 245, 249, 0.8);
  font-size: 12px;
  outline: none;
  cursor: pointer;
  transition: all 0.2s ease;

  &:focus {
    border-color: rgba(99, 102, 241, 0.6);
  }

  option {
    background: rgba(30, 41, 59, 0.9);
    color: rgba(241, 245, 249, 0.9);
  }
}

.subject-select {
  min-width: 80px;
}

.priority-select {
  min-width: 70px;
}

.add-task-btn {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.6), rgba(139, 92, 246, 0.6));
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.8), rgba(139, 92, 246, 0.8));
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  .plus-icon {
    width: 16px;
    height: 16px;
    color: rgba(255, 255, 255, 0.9);
  }
}

.progress-chart {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-item {
  .progress-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;

    .progress-name {
      font-size: 12px;
      color: rgba(148, 163, 184, 0.8);
    }

    .progress-percent {
      font-size: 12px;
      color: rgba(241, 245, 249, 0.85);
      font-weight: 500;
    }
  }

  .progress-bar {
    height: 6px;
    background: rgba(51, 65, 85, 0.5);
    border-radius: 3px;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.5s ease;
      opacity: 0.8;
    }
  }
}

.course-list {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.course-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(51, 65, 85, 0.4);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(51, 65, 85, 0.6);
  }
}

.course-cover {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  opacity: 0.85;

  .cover-icon {
    width: 20px;
    height: 20px;
    color: rgba(255, 255, 255, 0.9);
  }
}

.course-info {
  flex: 1;
  min-width: 0;

  .course-title {
    font-size: 13px;
    color: rgba(241, 245, 249, 0.85);
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .course-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 11px;
    color: rgba(148, 163, 184, 0.6);
    margin-bottom: 6px;
  }

  .course-tags {
    display: flex;
    gap: 5px;

    .course-tag {
      font-size: 9px;
      padding: 2px 6px;
      background: rgba(71, 85, 105, 0.6);
      border-radius: 3px;
      color: rgba(148, 163, 184, 0.8);
    }
  }
}

.course-action {
  width: 30px;
  height: 30px;
  background: rgba(99, 102, 241, 0.5);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: rgba(99, 102, 241, 0.7);
  }

  .play-icon {
    width: 14px;
    height: 14px;
    color: rgba(255, 255, 255, 0.9);
    margin-left: 1px;
  }
}

.history-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--bg-card);
  }
}

.history-cover {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  .cover-icon {
    width: 20px;
    height: 20px;
    color: white;
  }
}

.history-info {
  flex: 1;
  min-width: 0;

  .history-title {
    font-size: 13px;
    color: var(--text-primary);
    margin-bottom: 8px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .history-progress {
    display: flex;
    align-items: center;
    gap: 10px;

    .mini-progress-bar {
      flex: 1;
      height: 4px;
      background: var(--bg-card);
      border-radius: 2px;
      overflow: hidden;

      .mini-progress-fill {
        height: 100%;
        background: var(--primary-color);
        border-radius: 2px;
      }
    }

    .history-percent {
      font-size: 11px;
      color: var(--primary-color);
      font-weight: 500;
      min-width: 35px;
      text-align: right;
    }
  }
}

.history-time {
  font-size: 11px;
  color: var(--text-muted);
  flex-shrink: 0;
}

/* ========== 学习内容分布扇形图 ========== */
.range-selector {
  display: flex;
  gap: 3px;
  padding: 2px;
  background: rgba(51, 65, 85, 0.4);
  border-radius: 8px;
}

.range-btn {
  padding: 4px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(148, 163, 184, 0.7);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;

  &:hover {
    background: rgba(71, 85, 105, 0.5);
    color: rgba(241, 245, 249, 0.9);
  }

  &.active {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    box-shadow: 0 2px 6px rgba(99, 102, 241, 0.4);
  }
}

.distribution-chart {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px;
}

.pie-chart-wrap {
  position: relative;
  width: 140px;
  height: 140px;
  flex-shrink: 0;

  .pie-svg {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.25));
  }

  .pie-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.98), rgba(15, 23, 42, 0.99));
    width: 72px;
    height: 72px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    border: 2px solid rgba(71, 85, 105, 0.5);

    .pie-total {
      font-size: 20px;
      font-weight: 700;
      color: rgba(241, 245, 249, 0.98);
      line-height: 1.1;
    }

    .pie-label {
      font-size: 10px;
      color: rgba(148, 163, 184, 0.8);
      font-weight: 500;
    }
  }
}

.pie-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 120px;

  .no-data {
    font-size: 12px;
    color: rgba(148, 163, 184, 0.5);
    text-align: center;
    padding: 20px 0;
  }
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 8px;
  background: rgba(51, 65, 85, 0.3);
  transition: all 0.2s ease;
  border: 1px solid rgba(71, 85, 105, 0.2);

  &:hover {
    background: rgba(51, 65, 85, 0.5);
    transform: translateX(4px);
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 3px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    flex-shrink: 0;
  }

  .legend-name {
    flex: 1;
    font-size: 12px;
    color: rgba(241, 245, 249, 0.9);
    font-weight: 500;
  }

  .legend-value {
    font-size: 13px;
    color: rgba(241, 245, 249, 0.95);
    font-weight: 700;
    min-width: 38px;
    text-align: right;
  }
}
</style>
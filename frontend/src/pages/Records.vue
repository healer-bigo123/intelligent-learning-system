<template>
  <div class="records">
    <!-- 时间范围选择 -->
    <div class="time-selector">
      <button
        v-for="range in timeRanges"
        :key="range.value"
        class="time-btn"
        :class="{ active: selectedRange === range.value }"
        @click="selectedRange = range.value"
      >
        {{ range.label }}
      </button>
    </div>

    <!-- 数据概览 -->
    <div class="overview-cards">
      <div class="overview-card">
        <div class="overview-icon blue">
          <component :is="icons.Clock" class="icon" />
        </div>
        <div class="overview-content">
          <div class="overview-value">{{ totalHours }}h</div>
          <div class="overview-label">学习时长</div>
          <div class="overview-change positive">
            <component :is="icons.TrendingUp" class="change-icon" />
            +12% vs 上周
          </div>
        </div>
      </div>

      <div class="overview-card">
        <div class="overview-icon green">
          <component :is="icons.Target" class="icon" />
        </div>
        <div class="overview-content">
          <div class="overview-value">{{ completedCourses }}</div>
          <div class="overview-label">完成课程</div>
          <div class="overview-change positive">
            <component :is="icons.TrendingUp" class="change-icon" />
            +3 门
          </div>
        </div>
      </div>

      <div class="overview-card">
        <div class="overview-icon purple">
          <component :is="icons.CheckSquare" class="icon" />
        </div>
        <div class="overview-content">
          <div class="overview-value">{{ completedTasks }}</div>
          <div class="overview-label">完成任务</div>
          <div class="overview-change positive">
            <component :is="icons.TrendingUp" class="change-icon" />
            +8 个
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="chart-card card">
        <div class="chart-header">
          <h3 class="chart-title">
            <component :is="icons.BarChart" class="title-icon" />
            每日学习时长
          </h3>
        </div>
        <div class="bar-chart">
          <div class="y-axis">
            <span v-for="label in yAxisLabels" :key="label" class="y-label">{{ label }}h</span>
          </div>
          <div class="bars-container">
            <div
              v-for="(item, index) in dailyData"
              :key="item.day"
              class="bar-item"
            >
              <div class="bar-wrapper">
                <div
                  class="bar"
                  :style="{ 
                    height: (item.hours / maxDailyHours * 100) + '%',
                    background: `linear-gradient(180deg, ${item.color}dd, ${item.color}40)`
                  }"
                  :class="{ today: index === dailyData.length - 1 }"
                >
                  <span class="bar-value">{{ item.hours }}h</span>
                </div>
              </div>
              <span class="bar-label">{{ item.day }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="chart-header">
          <h3 class="chart-title">
            <component :is="icons.PieChart" class="title-icon" />
            学习内容分布
          </h3>
        </div>
        <div class="pie-chart-container">
          <div class="pie-chart">
            <svg viewBox="0 0 100 100">
              <circle
                v-for="(segment, index) in pieSegments"
                :key="index"
                cx="50"
                cy="50"
                r="40"
                :fill="segment.color"
                :stroke="segment.color"
                stroke-width="40"
                :stroke-dasharray="segment.dashArray"
                :stroke-dashoffset="segment.dashOffset"
                transform="rotate(-90 50 50)"
                style="fill: none;"
              />
            </svg>
            <div class="pie-center">
              <span class="pie-total">{{ totalHours }}h</span>
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
          </div>
        </div>
      </div>
    </div>

    <!-- 学习记录列表 -->
    <div class="history-section">
      <div class="section-header">
        <h3 class="section-title">
          <component :is="icons.History" class="title-icon" />
          学习记录
        </h3>
      </div>

      <div class="history-table">
        <table>
          <thead>
            <tr>
              <th>课程名称</th>
              <th>学科</th>
              <th>进度</th>
              <th>上次学习</th>
              <th>学习时长</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in learningHistory" :key="record.id">
              <td>
                <div class="course-cell">
                  <div class="course-icon" :style="{ background: record.color }">
                    <component :is="getCourseIcon(record.category)" class="icon" />
                  </div>
                  <span class="course-name">{{ record.title }}</span>
                </div>
              </td>
              <td>
                <span class="category-badge">{{ record.category }}</span>
              </td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: record.progress + '%' }"></div>
                  </div>
                  <span class="progress-text">{{ record.progress }}%</span>
                </div>
              </td>
              <td>{{ record.lastStudy }}</td>
              <td>{{ record.totalTime }}</td>
              <td>
                <button class="action-btn continue">
                  <component :is="icons.Play" class="btn-icon" />
                  继续
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, type Component, onMounted, watch } from 'vue'
import {
  Clock, Target, CheckSquare, TrendingUp, BarChart,
  PieChart, History, Play, BookOpen, Search, Code, Cpu, Globe, Aperture, Shield
} from 'lucide-vue-next'
import { api } from '@/api/client'

const icons = {
  Clock, Target, CheckSquare, TrendingUp, BarChart,
  PieChart, History, Play, BookOpen, Search, Code, Cpu, Globe, Aperture, Shield
}

const courseIconMap: Record<string, Component> = {
  '人工智能概述': BookOpen,
  '搜索与推理': Search,
  '机器学习': Code,
  '深度学习': Cpu,
  '自然语言处理': Globe,
  '计算机视觉': Aperture,
  '人工智能伦理': Shield,
  default: Code
}

const getCourseIcon = (category: string): Component => {
  return courseIconMap[category] || courseIconMap.default
}

const timeRanges = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '全部', value: 'all' }
]

const selectedRange = ref('week')

const totalHours = ref(0)
const completedCourses = ref(0)
const completedTasks = ref(0)

// 生成最近7天的日期标签和颜色
const dayColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899']
const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const generateLast7Days = () => {
  const days = []
  const today = new Date()
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    days.push({
      date: d.toISOString().split('T')[0],
      day: dayNames[d.getDay()],
      hours: 0,
      color: dayColors[(6 - i) % dayColors.length]
    })
  }
  return days
}

const dailyData = ref(generateLast7Days())

const maxDailyHours = computed(() => Math.max(...dailyData.value.map(d => d.hours), 1))

const yAxisLabels = computed(() => {
  const max = Math.ceil(maxDailyHours.value)
  const labels = []
  for (let i = max; i >= 0; i -= 2) {
    labels.push(i)
  }
  return labels
})

const contentDistribution = ref([
  { name: '人工智能概述', percent: 0, color: '#3b82f6', hours: 0 },
  { name: '搜索与推理', percent: 0, color: '#f59e0b', hours: 0 },
  { name: '机器学习', percent: 0, color: '#10b981', hours: 0 },
  { name: '深度学习', percent: 0, color: '#ef4444', hours: 0 },
  { name: '自然语言处理', percent: 0, color: '#8b5cf6', hours: 0 },
  { name: '计算机视觉', percent: 0, color: '#06b6d4', hours: 0 },
  { name: '人工智能伦理', percent: 0, color: '#ec4899', hours: 0 }
])

const pieSegments = computed(() => {
  const total = 100
  let currentOffset = 0
  const circumference = 2 * Math.PI * 40

  return contentDistribution.value.map(item => {
    const percentage = item.percent
    const dashArray = `${(percentage / total) * circumference} ${circumference}`
    const dashOffset = -currentOffset * (circumference / total)
    currentOffset += percentage

    return {
      color: item.color,
      dashArray,
      dashOffset
    }
  })
})

const learningHistory = ref<any[]>([])

// 根据时间范围计算起止日期
const getDateRange = (range: string) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const endDate = new Date(today)
  endDate.setHours(23, 59, 59, 999)
  let startDate = new Date(today)

  switch (range) {
    case 'today':
      break
    case 'week':
      startDate.setDate(today.getDate() - 6)
      break
    case 'month':
      startDate.setDate(1)
      break
    case 'all':
      startDate = new Date('2000-01-01')
      break
    default:
      startDate.setDate(today.getDate() - 6)
  }

  return {
    start_date: startDate.toISOString().split('T')[0],
    end_date: endDate.toISOString().split('T')[0]
  }
}

const subjectColorMap: Record<string, string> = {
  '人工智能概述': '#3b82f6',
  '搜索与推理': '#f59e0b',
  '机器学习': '#10b981',
  '深度学习': '#ef4444',
  '自然语言处理': '#8b5cf6',
  '计算机视觉': '#06b6d4',
  '人工智能伦理': '#ec4899'
}

// 从后端加载学习记录
const loadRecords = async () => {
  try {
    const range = getDateRange(selectedRange.value)
    const isAll = selectedRange.value === 'all'

    // 并行加载多个数据源
    const [timelineRes, dailyRes, overviewRes, subjectsRes] = await Promise.all([
      api.get('/timeline', {
        params: {
          start_date: range.start_date,
          end_date: range.end_date,
          page_size: 50
        }
      }).catch(() => ({ data: { items: [] } })),
      api.get('/timeline/stats/daily', {
        params: isAll ? {} : { start_date: range.start_date, end_date: range.end_date }
      }).catch(() => ({ data: { items: [] } })),
      api.get('/timeline/stats/overview').catch(() => ({ data: { total_duration: 0, total_activities: 0, streak_days: 0 } })),
      api.get('/analytics/subjects').catch(() => ({ data: { items: [] } }))
    ])

    const timeline = timelineRes.data.items || []
    const dailyStats = dailyRes.data.items || []
    const overview = overviewRes.data
    const subjects = subjectsRes.data.items || []

    // 更新每日学习时长（基于日期）
    const dailyMap: Record<string, number> = {}
    dailyStats.forEach((item: any) => {
      const dateKey = item.date?.split('T')[0]
      if (dateKey) {
        dailyMap[dateKey] = (dailyMap[dateKey] || 0) + ((item.total_duration || 0) / 3600)
      }
    })

    // 以最近7天为图表维度
    const last7Days = generateLast7Days()
    dailyData.value = last7Days.map(item => ({
      ...item,
      hours: Math.round((dailyMap[item.date] || 0) * 10) / 10
    }))

    // 根据时间范围决定统计口径
    if (isAll) {
      // "全部" 使用后端总览数据（所有历史累计）
      totalHours.value = Math.round((overview.total_duration || 0) / 3600 * 10) / 10
      completedTasks.value = overview.total_activities || 0
    } else {
      // 其他范围按起止日期计算
      const rangeDuration = Object.values(dailyMap).reduce((sum: number, h: number) => sum + h, 0)
      totalHours.value = Math.round(rangeDuration * 10) / 10
      completedTasks.value = timeline.length
    }

    // 完成课程数：material_read / session_complete 类型的活动数
    completedCourses.value = timeline.filter((a: any) =>
      a.activity_type === 'material_read' || a.activity_type === 'session_complete'
    ).length

    // 更新内容分布（基于各学科练习数）
    const subjectTotals: Record<string, number> = {}
    subjects.forEach((subject: any) => {
      const name = subject.subject || '其他'
      subjectTotals[name] = (subjectTotals[name] || 0) + (subject.total_exercises || 0)
    })

    const totalExercises = Object.values(subjectTotals).reduce((sum: number, h: any) => sum + h, 0)

    contentDistribution.value = Object.entries(subjectTotals)
      .sort(([, a], [, b]) => (b as number) - (a as number))
      .slice(0, 5)
      .map(([name, count], index) => ({
        name,
        percent: totalExercises > 0 ? Math.round(((count as number) / totalExercises) * 100) : 0,
        color: subjectColorMap[name] || dayColors[index % dayColors.length],
        hours: Math.round((count as number) * 10) / 10
      }))

    // 更新学习历史
    learningHistory.value = timeline.slice(0, 8).map((activity: any) => {
      // 根据活动标题或类型推断章节
      let category = '其他'
      const title = (activity.title || '').toLowerCase()
      if (title.includes('人工智能概述') || title.includes('图灵') || title.includes('智能体') || title.includes('应用领域')) {
        category = '人工智能概述'
      } else if (title.includes('搜索') || title.includes('推理') || title.includes('a*') || title.includes('知识表示')) {
        category = '搜索与推理'
      } else if (title.includes('机器学习') || title.includes('监督') || title.includes('无监督') || title.includes('聚类') || title.includes('回归')) {
        category = '机器学习'
      } else if (title.includes('深度学习') || title.includes('神经网络') || title.includes('cnn') || title.includes('rnn')) {
        category = '深度学习'
      } else if (title.includes('自然语言') || title.includes('nlp') || title.includes('transformer') || title.includes('翻译') || title.includes('文本')) {
        category = '自然语言处理'
      } else if (title.includes('计算机视觉') || title.includes('图像') || title.includes('目标检测') || title.includes('人脸识别')) {
        category = '计算机视觉'
      } else if (title.includes('伦理') || title.includes('隐私') || title.includes('公平') || title.includes('安全')) {
        category = '人工智能伦理'
      }

      return {
        id: activity.id,
        title: activity.title || '学习活动',
        category,
        progress: Math.min(100, Math.round((activity.score || 0))),
        lastStudy: new Date(activity.created_at).toLocaleString('zh-CN', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }),
        totalTime: `${Math.round((activity.duration || 0) / 60)}分钟`,
        color: subjectColorMap[category] || '#6366f1'
      }
    })
  } catch (error) {
    console.error('加载学习记录失败:', error)
  }
}

onMounted(() => {
  loadRecords()
})

// 时间范围切换时重新加载数据
watch(selectedRange, () => {
  loadRecords()
})
</script>

<style lang="scss" scoped>
.records {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.time-selector {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.9), rgba(26, 37, 52, 0.95));
  border: 1px solid rgba(71, 85, 105, 0.6);
  border-radius: 10px;
  width: fit-content;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
}

.time-btn {
  padding: 9px 20px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgba(148, 163, 184, 0.7);
  font-size: 12px;
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
    box-shadow: 0 3px 8px rgba(99, 102, 241, 0.4);
    transform: translateY(-1px);
  }
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.85), rgba(26, 37, 52, 0.9));
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: 12px;
  transition: all 0.35s ease;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.5), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    border-color: rgba(99, 102, 241, 0.5);

    &::before {
      opacity: 1;
    }
  }
}

.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 12px;
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  &.blue { 
    background: linear-gradient(145deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.08)); 
    .icon { color: #60a5fa; }
    &::after { background: radial-gradient(circle at center, rgba(59, 130, 246, 0.3), transparent 70%); }
  }
  &.green { 
    background: linear-gradient(145deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.08)); 
    .icon { color: #34d399; }
    &::after { background: radial-gradient(circle at center, rgba(16, 185, 129, 0.3), transparent 70%); }
  }
  &.purple { 
    background: linear-gradient(145deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.08)); 
    .icon { color: #a78bfa; }
    &::after { background: radial-gradient(circle at center, rgba(139, 92, 246, 0.3), transparent 70%); }
  }

  &:hover::after {
    opacity: 1;
  }

  .icon {
    width: 24px;
    height: 24px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
  }
}

.overview-content {
  flex: 1;
  min-width: 0;

  .overview-value {
    font-size: 28px;
    font-weight: 700;
    color: rgba(241, 245, 249, 0.98);
    margin-bottom: 2px;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    letter-spacing: -0.5px;
  }

  .overview-label {
    font-size: 12px;
    color: rgba(148, 163, 184, 0.75);
    margin-bottom: 6px;
    font-weight: 500;
  }

  .overview-change {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 500;

    &.positive {
      color: #34d399;
    }

    &.negative {
      color: #f87171;
    }

    .change-icon {
      width: 12px;
      height: 12px;
    }
  }
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.chart-card {
}

.chart-header {
  margin-bottom: 24px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;

  .title-icon {
    width: 20px;
    height: 20px;
    color: var(--primary-color);
  }
}

.bar-chart {
  display: flex;
  height: 240px;
  padding: 10px 16px;
  gap: 16px;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 12px;
  padding-bottom: 36px;
  min-width: 35px;

  .y-label {
    font-size: 11px;
    color: rgba(148, 163, 184, 0.7);
    text-align: right;
  }
}

.bars-container {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  padding-bottom: 36px;
  padding-top: 0;
  border-left: 1px solid rgba(71, 85, 105, 0.5);
  border-bottom: 1px solid rgba(71, 85, 105, 0.5);
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 36px;
    background: repeating-linear-gradient(
      180deg,
      rgba(71, 85, 105, 0.15) 0px,
      rgba(71, 85, 105, 0.15) 1px,
      transparent 1px
    );
  }
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  max-width: 55px;
  height: calc(100% - 36px);
}

.bar-wrapper {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  min-height: 100px;
}

.bar {
  width: 44px;
  border-radius: 10px 10px 6px 6px;
  position: relative;
  transition: all 0.3s ease;
  min-height: 6px;

  &:hover {
    transform: translateY(-3px) scaleY(1.05);
  }

  .bar-value {
    position: absolute;
    top: -32px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
    color: rgba(241, 245, 249, 0.9);
    white-space: nowrap;
    font-weight: 700;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  }
}

.bar-label {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.8);
  font-weight: 500;
}

.pie-chart-container {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 20px;
  justify-content: center;
}

.pie-chart {
  position: relative;
  width: 160px;
  height: 160px;
  flex-shrink: 0;

  svg {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 6px 14px rgba(0, 0, 0, 0.3));
  }

  .pie-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.98), rgba(15, 23, 42, 0.99));
    width: 85px;
    height: 85px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
    border: 2px solid rgba(71, 85, 105, 0.5);

    .pie-total {
      display: block;
      font-size: 24px;
      font-weight: 800;
      color: rgba(241, 245, 249, 0.98);
      line-height: 1.1;
    }

    .pie-label {
      font-size: 11px;
      color: rgba(148, 163, 184, 0.8);
      font-weight: 500;
    }
  }
}

.pie-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 160px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  border-radius: 10px;
  background: rgba(51, 65, 85, 0.4);
  transition: all 0.25s ease;
  border: 1px solid rgba(71, 85, 105, 0.3);

  &:hover {
    background: rgba(51, 65, 85, 0.6);
    transform: translateX(6px);
    border-color: rgba(99, 102, 241, 0.4);
  }

  .legend-color {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
    flex-shrink: 0;
  }

  .legend-name {
    flex: 1;
    font-size: 14px;
    color: rgba(241, 245, 249, 0.92);
    font-weight: 600;
  }

  .legend-value {
    font-size: 15px;
    color: rgba(241, 245, 249, 0.98);
    font-weight: 700;
    font-family: 'Inter', system-ui, sans-serif;
    min-width: 45px;
    text-align: right;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  }
}

.history-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;

  .title-icon {
    width: 20px;
    height: 20px;
    color: var(--primary-color);
  }
}

.history-table {
  padding: 24px;
  overflow-x: auto;
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th {
  text-align: left;
  padding: 14px 16px;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--border-color);
}

.history-table td {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  font-size: 13px;
  color: var(--text-secondary);

  &:last-child {
    text-align: center;
  }
}

.history-table tbody tr:hover {
  background: var(--bg-tertiary);
}

.course-cell {
  display: flex;
  align-items: center;
  gap: 12px;

  .course-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;

    .icon {
      width: 18px;
      height: 18px;
      color: white;
    }
  }

  .course-name {
    color: var(--text-primary);
    font-weight: 500;
  }
}

.category-badge {
  padding: 4px 12px;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 4px;
  color: var(--primary-color);
  font-size: 11px;
  font-weight: 500;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 120px;

  .progress-bar {
    flex: 1;
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: 3px;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      background: var(--primary-color);
      border-radius: 3px;
    }
  }

  .progress-text {
    font-size: 12px;
    color: var(--primary-color);
    font-weight: 500;
    min-width: 35px;
  }
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;

  &.continue {
    background: rgba(99, 102, 241, 0.1);
    color: var(--primary-color);

    &:hover {
      background: var(--primary-color);
      color: white;
    }
  }

  .btn-icon {
    width: 14px;
    height: 14px;
  }
}
</style>
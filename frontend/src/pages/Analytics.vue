<template>
  <div class="analytics">
    <!-- 统计概览卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <component :is="icons.FileText" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ overview.total_exercises }}</div>
          <div class="stat-label">总练习数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon green">
          <component :is="icons.CheckCircle2" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ overview.accuracy_rate }}%</div>
          <div class="stat-label">正确率</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon red">
          <component :is="icons.XCircle" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ overview.unsolved_mistakes }}</div>
          <div class="stat-label">待解决错题</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon orange">
          <component :is="icons.Flame" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ overview.streak_days }}天</div>
          <div class="stat-label">连续学习</div>
        </div>
      </div>
    </div>

    <div class="row-section">
      <!-- 各科成绩趋势 -->
      <div class="section-card half">
        <div class="section-header">
          <h3 class="section-title">
            <component :is="icons.PieChart" class="title-icon" />
            各科成绩趋势
          </h3>
        </div>

        <div v-if="subjectTrends.length > 0" class="subject-list">
          <div v-for="item in subjectTrends" :key="item.subject" class="subject-bar-row">
            <div class="subject-label">{{ item.subject }}</div>
            <div class="subject-bar-track">
              <div
                class="subject-bar-fill"
                :style="{ width: item.accuracy_rate + '%', background: getSubjectColor(item.subject) }"
              ></div>
            </div>
            <div class="subject-value" :style="{ color: getSubjectColor(item.subject) }">
              {{ item.accuracy_rate }}%
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <component :is="icons.PieChart" class="empty-icon" />
          <p>暂无练习数据，完成练习后将在此展示各科成绩趋势</p>
        </div>
      </div>

      <!-- 薄弱知识点 -->
      <div class="section-card half">
        <div class="section-header">
          <h3 class="section-title">
            <component :is="icons.AlertTriangle" class="title-icon" />
            薄弱知识点
          </h3>
        </div>

        <div v-if="weakPoints.length > 0" class="weak-list">
          <div v-for="(item, index) in weakPoints" :key="item.knowledge_point" class="weak-item">
            <div class="weak-rank" :class="getRankClass(index)">{{ index + 1 }}</div>
            <div class="weak-info">
              <div class="weak-name">{{ item.knowledge_point }}</div>
              <div class="weak-meta">
                共 {{ item.total_attempts }} 次，错 {{ item.wrong_count }} 次
              </div>
            </div>
            <div class="weak-rate" :class="getRateClass(item.error_rate)">
              {{ item.error_rate }}%
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <component :is="icons.AlertTriangle" class="empty-icon" />
          <p>暂无薄弱知识点数据</p>
        </div>
      </div>
    </div>

    <!-- AI 评估报告 -->
    <div class="section-card full">
      <div class="section-header">
        <h3 class="section-title">
          <component :is="icons.FileSearch" class="title-icon" />
          AI 学习评估报告
        </h3>
        <button
          class="generate-btn"
          :disabled="generating"
          @click="handleGenerateReport"
        >
          <component :is="generating ? icons.Loader2 : icons.FileSearch" class="btn-icon" :class="{ spinning: generating }" />
          {{ generating ? '生成中...' : (latestReport ? '重新生成' : '生成报告') }}
        </button>
      </div>

      <div v-if="latestReport" class="report-content">
        <div class="report-meta">
          <span class="report-date">生成时间：{{ formatDate(latestReport.created_at) }}</span>
        </div>
        <div class="report-text">{{ latestReport.content }}</div>
      </div>
      <div v-else-if="!generating" class="empty-state">
        <component :is="icons.FileSearch" class="empty-icon" />
        <p>点击"生成报告"按钮，AI 将根据你的学习数据生成专属评估报告</p>
      </div>
      <div v-if="generating" class="generating-state">
        <component :is="icons.Loader2" class="loading-icon spinning" />
        <p>AI 正在分析你的学习数据，请稍候...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  FileText, CheckCircle2, XCircle, Flame, PieChart,
  AlertTriangle, FileSearch, Loader2
} from 'lucide-vue-next'
import {
  getOverview, getSubjectTrends, getWeakPoints,
  generateReport, getLatestReport,
  type OverviewData, type SubjectTrendItem, type WeakPointItem, type ReportData
} from '@/api/analytics'

const icons = {
  FileText, CheckCircle2, XCircle, Flame, PieChart,
  AlertTriangle, FileSearch, Loader2
}

const overview = ref<OverviewData>({
  total_exercises: 0,
  correct_count: 0,
  accuracy_rate: 0,
  total_mistakes: 0,
  unsolved_mistakes: 0,
  streak_days: 0
})

const subjectTrends = ref<SubjectTrendItem[]>([])
const weakPoints = ref<WeakPointItem[]>([])
const latestReport = ref<ReportData | null>(null)
const generating = ref(false)

const subjectColors: Record<string, string> = {
  '数学': '#3b82f6',
  '语文': '#ef4444',
  '英语': '#10b981',
  '物理': '#f59e0b',
  '化学': '#8b5cf6',
  '生物': '#06b6d4',
  '历史': '#ec4899',
  '地理': '#14b8a6',
  '政治': '#f97316',
}

function getSubjectColor(subject: string): string {
  return subjectColors[subject] || '#6366f1'
}

function getRankClass(index: number): string {
  if (index === 0) return 'rank-1'
  if (index === 1) return 'rank-2'
  if (index === 2) return 'rank-3'
  return ''
}

function getRateClass(rate: number): string {
  if (rate >= 70) return 'rate-high'
  if (rate >= 40) return 'rate-mid'
  return 'rate-low'
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

async function loadData() {
  try {
    const [overviewRes, subjectsRes, weakRes] = await Promise.all([
      getOverview(),
      getSubjectTrends(),
      getWeakPoints()
    ])
    overview.value = overviewRes.data
    subjectTrends.value = subjectsRes.data.items
    weakPoints.value = weakRes.data.items
  } catch (e) {
    console.error('加载成绩分析数据失败', e)
  }
}

async function loadLatestReport() {
  try {
    const res = await getLatestReport()
    latestReport.value = res.data
  } catch {
    // 无报告时不报错
  }
}

async function handleGenerateReport() {
  try {
    generating.value = true
    const res = await generateReport()
    latestReport.value = res.data
  } catch (e: any) {
    alert(e.response?.data?.detail || '生成报告失败')
  } finally {
    generating.value = false
  }
}

onMounted(() => {
  loadData()
  loadLatestReport()
})
</script>

<style lang="scss" scoped>
.analytics {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.blue { background: rgba(59, 130, 246, 0.15); }
  &.green { background: rgba(16, 185, 129, 0.15); }
  &.red { background: rgba(239, 68, 68, 0.15); }
  &.orange { background: rgba(245, 158, 11, 0.15); }

  .icon {
    width: 24px;
    height: 24px;
  }

  &.blue .icon { color: #3b82f6; }
  &.green .icon { color: #10b981; }
  &.red .icon { color: #ef4444; }
  &.orange .icon { color: #f59e0b; }
}

.stat-info {
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
  }

  .stat-label {
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 2px;
  }
}

.row-section {
  display: flex;
  gap: 16px;
}

.section-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;

  &.half { flex: 1; }
  &.full { width: 100%; }
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;

  .title-icon {
    width: 18px;
    height: 18px;
    color: var(--primary-color);
  }
}

// 各科成绩趋势
.subject-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.subject-bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.subject-label {
  width: 48px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.subject-bar-track {
  flex: 1;
  height: 10px;
  background: var(--bg-tertiary);
  border-radius: 5px;
  overflow: hidden;
}

.subject-bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.6s ease;
}

.subject-value {
  width: 52px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

// 薄弱知识点
.weak-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.weak-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.weak-rank {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  background: var(--border-color);
  flex-shrink: 0;

  &.rank-1 { background: #ef4444; }
  &.rank-2 { background: #f59e0b; }
  &.rank-3 { background: #3b82f6; }
}

.weak-info {
  flex: 1;
  min-width: 0;

  .weak-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .weak-meta {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 2px;
  }
}

.weak-rate {
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;

  &.rate-high { color: #ef4444; }
  &.rate-mid { color: #f59e0b; }
  &.rate-low { color: #10b981; }
}

// 评估报告
.generate-btn {
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

  &:hover:not(:disabled) {
    background: var(--primary-dark);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .btn-icon {
    width: 14px;
    height: 14px;
  }
}

.report-content {
  .report-meta {
    margin-bottom: 16px;

    .report-date {
      font-size: 12px;
      color: var(--text-muted);
    }
  }

  .report-text {
    font-size: 14px;
    line-height: 1.8;
    color: var(--text-secondary);
    white-space: pre-wrap;
  }
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;

  .empty-icon {
    width: 40px;
    height: 40px;
    color: var(--text-muted);
    opacity: 0.4;
    margin-bottom: 12px;
  }

  p {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0;
  }
}

.generating-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;

  .loading-icon {
    width: 32px;
    height: 32px;
    color: var(--primary-color);
    margin-bottom: 12px;
  }

  p {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0;
  }
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

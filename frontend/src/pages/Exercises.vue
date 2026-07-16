<template>
  <div class="exercises-page">
    <!-- 统计概览 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <component :is="icons.BookOpen" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ exerciseTotal }}</div>
          <div class="stat-label">题库总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <component :is="icons.CheckCircle" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ historyTotal }}</div>
          <div class="stat-label">已练习</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <component :is="icons.Target" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ accuracyRate }}%</div>
          <div class="stat-label">正确率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <component :is="icons.Zap" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ sessionTotal }}</div>
          <div class="stat-label">练习次数</div>
        </div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="tab-btn"
        :class="{ active: activeTab === tab.value }"
        @click="activeTab = tab.value"
      >
        <component :is="tab.icon" class="tab-icon" />
        {{ tab.label }}
      </button>
    </div>

    <!-- 题库列表 -->
    <div v-if="activeTab === 'library'" class="tab-content">
      <div class="filter-bar">
        <div class="filter-left">
          <select v-model="filterSubject" class="filter-select" @change="loadExercises">
            <option value="">全部章节</option>
            <option value="人工智能概述">人工智能概述</option>
            <option value="搜索与推理">搜索与推理</option>
            <option value="机器学习">机器学习</option>
            <option value="深度学习">深度学习</option>
            <option value="自然语言处理">自然语言处理</option>
            <option value="计算机视觉">计算机视觉</option>
            <option value="人工智能伦理">人工智能伦理</option>
          </select>
          <select v-model="filterType" class="filter-select" @change="loadExercises">
            <option value="">全部题型</option>
            <option value="choice">选择题</option>
            <option value="fill_blank">填空题</option>
            <option value="short_answer">简答题</option>
            <option value="programming">编程题</option>
          </select>
        </div>
        <div class="filter-right">
          <button class="btn-primary" @click="showStartSession = true">
            <component :is="icons.Play" class="btn-icon" />
            开始练习
          </button>
        </div>
      </div>

      <div v-if="loadingExercises" class="loading-state">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <div v-else-if="exercises.length === 0" class="empty-state">
        <component :is="icons.BookOpen" class="empty-icon" />
        <p>暂无练习题</p>
      </div>

      <div v-else class="exercise-list">
        <div
          v-for="exercise in exercises"
          :key="exercise.id"
          class="exercise-card card"
        >
          <div class="exercise-header">
            <span class="type-tag" :class="exercise.type">{{ getTypeText(exercise.type) }}</span>
            <span class="difficulty-badge" :class="'d' + exercise.difficulty">
              {{ '★'.repeat(exercise.difficulty) }}
            </span>
          </div>
          <div class="exercise-question">{{ exercise.question }}</div>
          <div class="exercise-footer">
            <span class="subject-label">{{ exercise.subject }}</span>
            <span class="kp-label" v-if="exercise.knowledge_point">{{ exercise.knowledge_point }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 练习历史 -->
    <div v-if="activeTab === 'history'" class="tab-content">
      <div v-if="loadingHistory" class="loading-state">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <div v-else-if="historyItems.length === 0" class="empty-state">
        <component :is="icons.History" class="empty-icon" />
        <p>暂无练习记录</p>
      </div>

      <div v-else class="history-table">
        <table>
          <thead>
            <tr>
              <th>题目</th>
              <th>学科</th>
              <th>我的答案</th>
              <th>正确答案</th>
              <th>结果</th>
              <th>耗时</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in historyItems" :key="item.record_id">
              <td class="question-cell">{{ item.question }}</td>
              <td><span class="subject-badge">{{ item.subject }}</span></td>
              <td class="answer-cell">{{ item.user_answer || '-' }}</td>
              <td class="answer-cell">{{ item.correct_answer }}</td>
              <td>
                <span class="result-tag" :class="item.is_correct ? 'correct' : 'wrong'">
                  {{ item.is_correct ? '正确' : '错误' }}
                </span>
              </td>
              <td>{{ item.time_spent }}s</td>
              <td>{{ formatTime(item.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 练习会话 -->
    <div v-if="activeTab === 'sessions'" class="tab-content">
      <div v-if="loadingSessions" class="loading-state">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <div v-else-if="sessions.length === 0" class="empty-state">
        <component :is="icons.List" class="empty-icon" />
        <p>暂无练习会话</p>
      </div>

      <div v-else class="sessions-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-card"
        >
          <div class="session-header">
            <h4 class="session-title">{{ session.title || session.subject + ' 练习' }}</h4>
            <span class="session-status" :class="session.status">
              {{ session.status === 'completed' ? '已完成' : '进行中' }}
            </span>
          </div>
          <div class="session-stats">
            <div class="session-stat">
              <span class="stat-label">题目数</span>
              <span class="stat-val">{{ session.total_count }}</span>
            </div>
            <div class="session-stat">
              <span class="stat-label">正确数</span>
              <span class="stat-val">{{ session.correct_count }}</span>
            </div>
            <div class="session-stat">
              <span class="stat-label">得分</span>
              <span class="stat-val score">{{ session.score }}</span>
            </div>
          </div>
          <div class="session-time">
            {{ formatTime(session.created_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 开始练习弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div class="modal-overlay" v-if="showStartSession" @click.self="showStartSession = false">
          <div class="modal-content">
            <div class="modal-header">
              <h3>开始练习</h3>
              <button class="modal-close" @click="showStartSession = false">
                <component :is="icons.X" class="close-icon" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>选择章节</label>
                <select v-model="sessionForm.subject">
                  <option value="">请选择</option>
                  <option value="人工智能概述">人工智能概述</option>
                  <option value="搜索与推理">搜索与推理</option>
                  <option value="机器学习">机器学习</option>
                  <option value="深度学习">深度学习</option>
                  <option value="自然语言处理">自然语言处理</option>
                  <option value="计算机视觉">计算机视觉</option>
                  <option value="人工智能伦理">人工智能伦理</option>
                </select>
              </div>
              <div class="form-group">
                <label>题目数量</label>
                <input v-model.number="sessionForm.exercise_count" type="number" min="1" max="20" />
              </div>
              <div class="form-group">
                <label>难度筛选（可选）</label>
                <select v-model="sessionForm.difficulty">
                  <option :value="null">不限</option>
                  <option :value="1">★</option>
                  <option :value="2">★★</option>
                  <option :value="3">★★★</option>
                  <option :value="4">★★★★</option>
                  <option :value="5">★★★★★</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="showStartSession = false">取消</button>
              <button class="btn-confirm" @click="handleStartSession" :disabled="startingSession">
                {{ startingSession ? '生成中...' : '开始' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  BookOpen, CheckCircle, Target, Zap, History, List,
  Play, X
} from 'lucide-vue-next'
import {
  getExercises, getExerciseHistory, getSessionHistory,
  generateExerciseSession,
  type ExerciseItem, type ExerciseHistoryItem, type ExerciseSessionItem
} from '@/api/exercises'

const icons = { BookOpen, CheckCircle, Target, Zap, History, List, Play, X }

const tabs = [
  { value: 'library', label: '题库', icon: BookOpen },
  { value: 'history', label: '练习历史', icon: History },
  { value: 'sessions', label: '练习会话', icon: List }
]

const activeTab = ref('library')

// 题库
const exercises = ref<ExerciseItem[]>([])
const exerciseTotal = ref(0)
const loadingExercises = ref(false)
const filterSubject = ref('')
const filterType = ref('')

// 练习历史
const historyItems = ref<ExerciseHistoryItem[]>([])
const historyTotal = ref(0)
const loadingHistory = ref(false)
const correctCount = computed(() =>
  historyItems.value.filter(h => h.is_correct).length
)
const accuracyRate = computed(() =>
  historyTotal.value > 0 ? Math.round((correctCount.value / historyTotal.value) * 100) : 0
)

// 练习会话
const sessions = ref<ExerciseSessionItem[]>([])
const sessionTotal = ref(0)
const loadingSessions = ref(false)

// 开始练习弹窗
const showStartSession = ref(false)
const startingSession = ref(false)
const sessionForm = ref({
  subject: '',
  exercise_count: 5,
  difficulty: null as number | null
})

const getTypeText = (type: string): string => {
  const map: Record<string, string> = {
    choice: '选择题',
    fill_blank: '填空题',
    short_answer: '简答题',
    programming: '编程题'
  }
  return map[type] || type
}

const formatTime = (dateStr: string): string => {
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载题库
const loadExercises = async () => {
  loadingExercises.value = true
  try {
    const res = await getExercises({
      subject: filterSubject.value || undefined,
      type: filterType.value || undefined,
      page_size: 50
    })
    exercises.value = res.items
    exerciseTotal.value = res.total
  } catch (e) {
    console.error('加载题库失败:', e)
  } finally {
    loadingExercises.value = false
  }
}

// 加载练习历史
const loadHistory = async () => {
  loadingHistory.value = true
  try {
    const res = await getExerciseHistory({ page_size: 50 })
    historyItems.value = res.items
    historyTotal.value = res.total
  } catch (e) {
    console.error('加载练习历史失败:', e)
  } finally {
    loadingHistory.value = false
  }
}

// 加载练习会话
const loadSessions = async () => {
  loadingSessions.value = true
  try {
    const res = await getSessionHistory({ page_size: 50 })
    sessions.value = res.items
    sessionTotal.value = res.total
  } catch (e) {
    console.error('加载练习会话失败:', e)
  } finally {
    loadingSessions.value = false
  }
}

// 开始练习
const handleStartSession = async () => {
  if (!sessionForm.value.subject) {
    alert('请选择学科')
    return
  }

  startingSession.value = true
  try {
    await generateExerciseSession({
      subject: sessionForm.value.subject,
      exercise_count: sessionForm.value.exercise_count,
      difficulty: sessionForm.value.difficulty || undefined
    })
    showStartSession.value = false
    sessionForm.value = { subject: '', exercise_count: 5, difficulty: null }
    await loadSessions()
  } catch (e: any) {
    console.error('生成练习失败:', e)
    alert(e.response?.data?.detail || '生成练习失败，请重试')
  } finally {
    startingSession.value = false
  }
}

onMounted(() => {
  loadExercises()
  loadHistory()
  loadSessions()
})
</script>

<style lang="scss" scoped>
.exercises-page {
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
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.85), rgba(26, 37, 52, 0.9));
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: 12px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.5);
  }
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;

  .icon { width: 22px; height: 22px; }

  &.blue { background: rgba(59, 130, 246, 0.15); .icon { color: #60a5fa; } }
  &.green { background: rgba(16, 185, 129, 0.15); .icon { color: #34d399; } }
  &.purple { background: rgba(139, 92, 246, 0.15); .icon { color: #a78bfa; } }
  &.orange { background: rgba(245, 158, 11, 0.15); .icon { color: #fbbf24; } }
}

.stat-info {
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
  }
  .stat-label {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 2px;
  }
}

.tab-bar {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.9), rgba(26, 37, 52, 0.95));
  border: 1px solid rgba(71, 85, 105, 0.6);
  border-radius: 10px;
  width: fit-content;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 20px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgba(148, 163, 184, 0.7);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;

  .tab-icon { width: 16px; height: 16px; }

  &:hover {
    background: rgba(71, 85, 105, 0.5);
    color: rgba(241, 245, 249, 0.9);
  }

  &.active {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    box-shadow: 0 3px 8px rgba(99, 102, 241, 0.4);
  }
}

.tab-content {
  min-height: 300px;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.filter-left {
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 8px 12px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-md);
  color: #e2e8f0;
  font-size: 13px;
  cursor: pointer;
  height: 40px;
  min-width: 120px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  &:focus {
    outline: none;
    border-color: #6366f1;
  }

  option {
    background: #1e293b;
    color: #e2e8f0;
  }
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border: none;
  border-radius: var(--radius-sm);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  .btn-icon { width: 14px; height: 14px; }

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: var(--text-muted);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-muted);

  .empty-icon { width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.5; }
  p { font-size: 15px; margin: 0; }
}

.exercise-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 14px;
}

.exercise-card {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  &:hover {
    border-color: rgba(99, 102, 241, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  }
}

.exercise-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.type-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;

  &.choice { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
  &.fill_blank { background: rgba(16, 185, 129, 0.15); color: #34d399; }
  &.short_answer { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
  &.programming { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
}

.difficulty-badge {
  font-size: 11px;
  color: #fbbf24;

  &.d1 { opacity: 0.4; }
  &.d2 { opacity: 0.6; }
  &.d3 { opacity: 0.8; }
  &.d4 { opacity: 0.9; }
  &.d5 { opacity: 1; }
}

.exercise-question {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.exercise-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.subject-label {
  font-size: 11px;
  color: var(--primary-color);
  font-weight: 500;
}

.kp-label {
  font-size: 11px;
  color: var(--text-muted);
  padding: 2px 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
}

.history-table {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th {
    text-align: left;
    padding: 12px 16px;
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 600;
    border-bottom: 2px solid var(--border-color);
  }

  td {
    padding: 12px 16px;
    font-size: 13px;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border-color);
  }

  tbody tr:hover { background: var(--bg-tertiary); }
}

.question-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.answer-cell {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subject-badge {
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 3px;
  color: var(--primary-color);
  font-size: 11px;
}

.result-tag {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;

  &.correct { background: rgba(16, 185, 129, 0.15); color: #34d399; }
  &.wrong { background: rgba(239, 68, 68, 0.15); color: #f87171; }
}

.sessions-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

.session-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.2s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.4);
  }
}

.session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  .session-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }
}

.session-status {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;

  &.completed { background: rgba(16, 185, 129, 0.15); color: #34d399; }
  &.in_progress { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
}

.session-stats {
  display: flex;
  gap: 20px;
}

.session-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;

  .stat-label {
    font-size: 11px;
    color: var(--text-muted);
  }

  .stat-val {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);

    &.score { color: var(--primary-color); }
  }
}

.session-time {
  font-size: 12px;
  color: var(--text-muted);
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  width: 100%;
  max-width: 440px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: modalIn 0.3s ease-out;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-color);

  h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0; }
}

.modal-close {
  width: 32px;
  height: 32px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;

  .close-icon { width: 14px; height: 14px; color: var(--text-secondary); }
  &:hover { background: var(--bg-card); border-color: var(--primary-color); }
}

.modal-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;

  label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
  }

  input, select {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    color: var(--text-primary);
    font-size: 13px;

    &:focus { outline: none; border-color: var(--primary-color); }
    option { background: var(--bg-secondary); }
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

.btn-cancel {
  padding: 8px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  &:hover { background: var(--bg-primary); }
}

.btn-confirm {
  padding: 8px 20px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border: none;
  border-radius: var(--radius-sm);
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }

  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

.modal-enter-active,
.modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
</style>

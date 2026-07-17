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
            <div class="header-actions">
              <button
                class="favorite-btn"
                :class="{ favorited: exerciseFavorites[exercise.id] }"
                :disabled="favoriteLoading[exercise.id]"
                @click.stop="toggleFavorite(exercise.id)"
                :title="exerciseFavorites[exercise.id] ? '取消收藏' : '收藏'"
              >
                <Heart class="btn-icon" :fill="exerciseFavorites[exercise.id] ? 'currentColor' : 'none'" />
              </button>
              <span class="difficulty-badge" :class="'d' + exercise.difficulty">
                {{ '★'.repeat(exercise.difficulty) }}
              </span>
            </div>
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
          <div class="session-actions">
            <button
              v-if="session.status !== 'completed'"
              class="session-btn continue"
              @click="continueSession(session)"
              :disabled="loadingSessionDetail"
            >
              <component :is="icons.Play" class="btn-icon" />
              {{ loadingSessionDetail ? '加载中...' : '继续练习' }}
            </button>
            <button
              v-else
              class="session-btn review"
              @click="continueSession(session)"
              :disabled="loadingSessionDetail"
            >
              <component :is="icons.Eye" class="btn-icon" />
              回顾
            </button>
            <span class="session-time">{{ formatTime(session.created_at) }}</span>
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

    <!-- 答题会话面板 -->
    <Teleport to="body">
      <Transition name="modal">
        <div class="session-overlay" v-if="currentSession" @click.self="closeSession">
          <div class="session-panel">
            <div class="session-panel-header">
              <div>
                <h3>{{ currentSession.title || currentSession.subject + ' 练习' }}</h3>
                <p class="session-progress-text">
                  第 {{ currentExerciseIndex + 1 }} / {{ currentExercises.length }} 题
                </p>
              </div>
              <button class="modal-close" @click="closeSession">
                <component :is="icons.X" class="close-icon" />
              </button>
            </div>

            <div class="session-panel-body">
              <div v-if="sessionCompleted && sessionSummary" class="session-summary">
                <div class="summary-score" :class="sessionSummary.score >= 60 ? 'pass' : 'fail'">
                  <span class="score-num">{{ sessionSummary.score }}</span>
                  <span class="score-label">分</span>
                </div>
                <div class="summary-stats">
                  <div class="summary-stat">
                    <span class="label">总题数</span>
                    <span class="value">{{ sessionSummary.total }}</span>
                  </div>
                  <div class="summary-stat correct">
                    <span class="label">正确</span>
                    <span class="value">{{ sessionSummary.correct }}</span>
                  </div>
                  <div class="summary-stat wrong">
                    <span class="label">错误</span>
                    <span class="value">{{ sessionSummary.wrong }}</span>
                  </div>
                </div>
                <button class="btn-confirm" @click="closeSession">完成</button>
              </div>

              <div v-else-if="currentExercise" class="question-area">
                <div class="question-meta">
                  <span class="type-tag" :class="currentExercise.type">
                    {{ getTypeText(currentExercise.type) }}
                  </span>
                  <span class="difficulty-badge" :class="'d' + currentExercise.difficulty">
                    {{ '★'.repeat(currentExercise.difficulty) }}
                  </span>
                  <span class="kp-label" v-if="currentExercise.knowledge_point">
                    {{ currentExercise.knowledge_point }}
                  </span>
                </div>

                <div class="question-content">{{ currentExercise.question }}</div>

                <div v-if="currentExercise.type === 'choice' && currentExercise.options" class="options-list">
                  <label
                    v-for="(option, idx) in currentExercise.options"
                    :key="idx"
                    class="option-item"
                    :class="{
                      selected: currentAnswer?.user_answer === option,
                      correct: currentAnswer?.submitted && option === currentAnswer?.correct_answer,
                      wrong: currentAnswer?.submitted && currentAnswer?.user_answer === option && !currentAnswer?.is_correct
                    }"
                  >
                    <input
                      type="radio"
                      :name="currentExercise.id"
                      :value="option"
                      v-model="currentAnswer!.user_answer"
                      :disabled="currentAnswer?.submitted"
                    />
                    <span class="option-index">{{ String.fromCharCode(65 + idx) }}.</span>
                    <span class="option-text">{{ option }}</span>
                  </label>
                </div>

                <div v-else class="answer-input-area">
                  <label>你的答案</label>
                  <textarea
                    v-model="currentAnswer!.user_answer"
                    rows="4"
                    placeholder="请输入你的答案"
                    :disabled="currentAnswer?.submitted"
                  ></textarea>
                </div>

                <div v-if="currentAnswer?.submitted" class="answer-result" :class="currentAnswer.is_correct ? 'correct' : 'wrong'">
                  <div class="result-title">
                    <component :is="currentAnswer.is_correct ? icons.CheckCircle : icons.X" class="result-icon" />
                    {{ currentAnswer.is_correct ? '回答正确' : '回答错误' }}
                  </div>
                  <div class="result-detail">
                    <p><strong>正确答案：</strong>{{ currentAnswer.correct_answer }}</p>
                    <p v-if="currentAnswer.explanation"><strong>解析：</strong>{{ currentAnswer.explanation }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="session-panel-footer">
              <button
                class="btn-secondary"
                :disabled="currentExerciseIndex <= 0"
                @click="currentExerciseIndex--"
              >
                <component :is="icons.ChevronLeft" class="btn-icon" />
                上一题
              </button>

              <button
                v-if="!currentAnswer?.submitted"
                class="btn-confirm"
                @click="submitCurrentAnswer"
              >
                提交答案
              </button>
              <button
                v-else-if="currentExerciseIndex < currentExercises.length - 1"
                class="btn-confirm"
                @click="currentExerciseIndex++"
              >
                下一题
                <component :is="icons.ChevronRight" class="btn-icon" />
              </button>
              <button
                v-else
                class="btn-confirm"
                @click="finishSession"
                :disabled="completingSession"
              >
                <component :is="icons.Flag" class="btn-icon" />
                {{ completingSession ? '提交中...' : '完成练习' }}
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
  Play, X, Heart, ChevronRight, ChevronLeft, Flag, Eye
} from 'lucide-vue-next'
import {
  getExercises, getExerciseHistory, getSessionHistory,
  generateExerciseSession, getExerciseSession, completeExerciseSession,
  submitAnswer,
  type ExerciseItem, type ExerciseHistoryItem, type ExerciseSessionItem
} from '@/api/exercises'
import {
  getFavorites, createFavorite, removeFavoriteByTarget,
  type FavoriteItem
} from '@/api/favorites'

const icons = { BookOpen, CheckCircle, Target, Zap, History, List, Play, X, Heart, ChevronRight, ChevronLeft, Flag, Eye }

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

// 收藏状态
const exerciseFavorites = ref<Record<string, FavoriteItem | undefined>>({})
const favoriteLoading = ref<Record<string, boolean>>({})

// 开始练习弹窗
const showStartSession = ref(false)
const startingSession = ref(false)
const sessionForm = ref({
  subject: '',
  exercise_count: 5,
  difficulty: null as number | null
})

// 当前练习会话（答题模式）
interface CurrentExercise {
  id: string
  type: string
  question: string
  options: string[] | null
  difficulty: number
  knowledge_point: string | null
}

interface AnswerRecord {
  exercise_id: string
  user_answer: string
  is_correct?: boolean
  correct_answer?: string
  explanation?: string | null
  score?: number
  submitted: boolean
}

const currentSession = ref<ExerciseSessionItem | null>(null)
const currentExercises = ref<CurrentExercise[]>([])
const currentAnswers = ref<Record<string, AnswerRecord>>({})
const currentExerciseIndex = ref(0)
const loadingSessionDetail = ref(false)
const completingSession = ref(false)
const sessionCompleted = ref(false)
const sessionSummary = ref<{ total: number; correct: number; wrong: number; score: number } | null>(null)

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
    await loadExerciseFavorites()
  } catch (e) {
    console.error('加载题库失败:', e)
  } finally {
    loadingExercises.value = false
  }
}

// 加载练习题收藏状态
const loadExerciseFavorites = async () => {
  try {
    const res = await getFavorites({ target_type: 'exercise', page_size: 100 })
    const map: Record<string, FavoriteItem | undefined> = {}
    res.items.forEach(item => {
      map[item.target_id] = item
    })
    exerciseFavorites.value = map
  } catch (e) {
    console.error('加载练习题收藏状态失败:', e)
  }
}

// 切换收藏状态
const toggleFavorite = async (exerciseId: string) => {
  if (favoriteLoading.value[exerciseId]) return
  favoriteLoading.value[exerciseId] = true
  try {
    if (exerciseFavorites.value[exerciseId]) {
      await removeFavoriteByTarget('exercise', exerciseId)
      exerciseFavorites.value[exerciseId] = undefined
    } else {
      const favorite = await createFavorite({ target_type: 'exercise', target_id: exerciseId })
      exerciseFavorites.value[exerciseId] = favorite
    }
  } catch (e) {
    console.error('收藏操作失败:', e)
    alert('收藏操作失败，请重试')
  } finally {
    favoriteLoading.value[exerciseId] = false
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
    const res = await generateExerciseSession({
      subject: sessionForm.value.subject,
      exercise_count: sessionForm.value.exercise_count,
      difficulty: sessionForm.value.difficulty || undefined
    })
    showStartSession.value = false
    sessionForm.value = { subject: '', exercise_count: 5, difficulty: null }
    await enterSession(res.session, res.exercises)
    await loadSessions()
  } catch (e: any) {
    console.error('生成练习失败:', e)
    alert(e.response?.data?.detail || '生成练习失败，请重试')
  } finally {
    startingSession.value = false
  }
}

// 进入答题会话
const enterSession = (session: ExerciseSessionItem, exercises: CurrentExercise[]) => {
  currentSession.value = session
  currentExercises.value = exercises
  currentExerciseIndex.value = 0
  currentAnswers.value = {}
  sessionCompleted.value = false
  sessionSummary.value = null
  exercises.forEach(ex => {
    currentAnswers.value[ex.id] = {
      exercise_id: ex.id,
      user_answer: '',
      submitted: false
    }
  })
}

// 重置答题会话
const closeSession = () => {
  currentSession.value = null
  currentExercises.value = []
  currentAnswers.value = {}
  currentExerciseIndex.value = 0
  sessionCompleted.value = false
  sessionSummary.value = null
}

// 当前题目
const currentExercise = computed(() =>
  currentExercises.value[currentExerciseIndex.value] || null
)

const currentAnswer = computed(() =>
  currentExercise.value ? currentAnswers.value[currentExercise.value.id] : null
)

// 提交当前题目答案
const submitCurrentAnswer = async () => {
  if (!currentExercise.value || !currentAnswer.value) return
  const ex = currentExercise.value
  const answer = currentAnswer.value
  if (!answer.user_answer.trim()) {
    alert('请填写答案')
    return
  }
  try {
    const res = await submitAnswer(ex.id, { user_answer: answer.user_answer, time_spent: 0 })
    answer.is_correct = res.is_correct
    answer.correct_answer = res.correct_answer
    answer.explanation = res.explanation
    answer.score = res.score
    answer.submitted = true
  } catch (e) {
    console.error('提交答案失败:', e)
    alert('提交答案失败，请重试')
  }
}

// 完成练习会话
const finishSession = async () => {
  if (!currentSession.value) return
  completingSession.value = true
  try {
    const res = await completeExerciseSession(currentSession.value.id)
    sessionSummary.value = res.summary
    sessionCompleted.value = true
    await loadHistory()
    await loadSessions()
  } catch (e) {
    console.error('完成练习会话失败:', e)
    alert('完成练习失败，请重试')
  } finally {
    completingSession.value = false
  }
}

// 继续历史会话
const continueSession = async (session: ExerciseSessionItem) => {
  loadingSessionDetail.value = true
  try {
    const res = await getExerciseSession(session.id)
    enterSession(res.session, res.exercises)
  } catch (e) {
    console.error('加载练习会话失败:', e)
    alert('加载练习会话失败')
  } finally {
    loadingSessionDetail.value = false
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
}

.session-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.session-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;

  .btn-icon { width: 12px; height: 12px; }

  &.continue {
    background: rgba(59, 130, 246, 0.1);
    color: #60a5fa;
    &:hover:not(:disabled) { background: rgba(59, 130, 246, 0.2); }
  }

  &.review {
    background: rgba(16, 185, 129, 0.1);
    color: #34d399;
    &:hover:not(:disabled) { background: rgba(16, 185, 129, 0.2); }
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.favorite-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;

  .btn-icon { width: 13px; height: 13px; }

  &:hover:not(:disabled) {
    border-color: #ec4899;
    color: #ec4899;
  }

  &.favorited {
    border-color: #ec4899;
    color: #ec4899;
    background: rgba(236, 72, 153, 0.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
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

.session-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 20px;
}

.session-panel {
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: modalIn 0.3s ease-out;
}

.session-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-tertiary);

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .session-progress-text {
    font-size: 12px;
    color: var(--text-muted);
    margin: 4px 0 0;
  }
}

.session-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.session-panel-footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;

  &:hover:not(:disabled) { background: var(--bg-primary); }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-icon { width: 14px; height: 14px; }
}

.question-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.question-content {
  font-size: 15px;
  color: var(--text-primary);
  line-height: 1.6;
  padding: 16px;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;

  input {
    width: 16px;
    height: 16px;
    accent-color: var(--primary-color);
    cursor: pointer;
  }

  &:hover:not(.selected):not(.correct):not(.wrong) {
    border-color: rgba(99, 102, 241, 0.5);
  }

  &.selected {
    border-color: var(--primary-color);
    background: rgba(99, 102, 241, 0.1);
  }

  &.correct {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.1);
    color: #34d399;
  }

  &.wrong {
    border-color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
  }
}

.answer-input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
  }

  textarea {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 12px;
    color: var(--text-primary);
    font-size: 14px;
    resize: vertical;

    &:focus { outline: none; border-color: var(--primary-color); }
    &:disabled { opacity: 0.7; cursor: not-allowed; }
  }
}

.answer-result {
  padding: 16px;
  border-radius: var(--radius-md);
  border: 1px solid;

  &.correct {
    background: rgba(16, 185, 129, 0.1);
    border-color: rgba(16, 185, 129, 0.3);
    color: #34d399;
  }

  &.wrong {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
    color: #f87171;
  }

  .result-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 10px;

    .result-icon { width: 18px; height: 18px; }
  }

  .result-detail {
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-secondary);

    strong { color: var(--text-primary); }

    p { margin: 4px 0; }
  }
}

.session-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 20px;

  .summary-score {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    align-items: baseline;
    justify-content: center;
    border: 4px solid;

    &.pass { border-color: #10b981; color: #34d399; }
    &.fail { border-color: #ef4444; color: #f87171; }

    .score-num {
      font-size: 48px;
      font-weight: 800;
      line-height: 120px;
    }

    .score-label {
      font-size: 16px;
      font-weight: 600;
    }
  }

  .summary-stats {
    display: flex;
    gap: 24px;
  }

  .summary-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;

    .label {
      font-size: 12px;
      color: var(--text-muted);
    }

    .value {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
    }

    &.correct .value { color: #34d399; }
    &.wrong .value { color: #f87171; }
  }
}

.modal-enter-active,
.modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
</style>

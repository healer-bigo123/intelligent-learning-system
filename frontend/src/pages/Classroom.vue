<template>
  <div class="classroom">
    <!-- 顶部操作栏 -->
    <div class="action-bar">
      <button class="btn-primary" @click="showCreateDialog = true">
        <component :is="icons.Plus" class="btn-icon" />
        创建课堂
      </button>
    </div>

    <!-- 课堂列表 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">
          <component :is="icons.GraduationCap" class="title-icon" />
          我的课堂
        </h2>
        <span class="count-badge">{{ classrooms.length }} 个课堂</span>
      </div>

      <div v-if="classrooms.length === 0" class="empty-state">
        <component :is="icons.GraduationCap" class="empty-icon" />
        <p>还没有课堂，点击上方按钮创建一个吧</p>
      </div>

      <div v-else class="classroom-grid">
        <div v-for="cls in classrooms" :key="cls.id" class="classroom-card">
          <div class="card-header">
            <h3 class="card-title">{{ cls.name }}</h3>
          </div>
          <div class="card-meta">
            <span>课堂码: <strong>{{ cls.code }}</strong></span>
            <span v-if="cls.description">{{ cls.description }}</span>
          </div>
          <div class="card-actions">
            <button class="action-btn" @click="openClassroom(cls)">
              <component :is="icons.Play" class="action-icon" />
              进入课堂
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建课堂对话框 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <h3 class="dialog-title">创建课堂</h3>
        <div class="form-group">
          <label>课堂名称</label>
          <input v-model="createForm.name" class="input-field" placeholder="例如：高三数学冲刺班" />
        </div>
        <div class="form-group">
          <label>描述（可选）</label>
          <textarea v-model="createForm.description" class="input-field" rows="3" placeholder="课堂描述..."></textarea>
        </div>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="showCreateDialog = false">取消</button>
          <button class="btn-primary" @click="createClassroom" :disabled="!createForm.name">
            创建
          </button>
        </div>
      </div>
    </div>

    <!-- 课堂详情面板 -->
    <div v-if="activeClassroom" class="dialog-overlay" @click.self="closeClassroom">
      <div class="dialog dialog-wide">
        <div class="dialog-header">
          <h3 class="dialog-title">{{ activeClassroom.name }}</h3>
          <button class="close-btn" @click="closeClassroom">&times;</button>
        </div>

        <!-- 功能标签页 -->
        <div class="tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            <component :is="tab.icon" class="tab-icon" />
            {{ tab.label }}
          </button>
        </div>

        <!-- PPT 生成 -->
        <div v-if="activeTab === 'ppt'" class="tab-content">
          <div class="form-group">
            <label>PPT 主题</label>
            <input v-model="pptForm.topic" class="input-field" placeholder="例如：一元二次方程" />
          </div>
          <button class="btn-primary" @click="generatePPT" :disabled="!pptForm.topic || pptLoading">
            {{ pptLoading ? '生成中...' : '生成 PPT' }}
          </button>
          <div v-if="pptResult" class="result-box">
            <h4>{{ pptResult.title }}</h4>
            <div v-if="pptResult.slides" class="slides-list">
              <div v-for="(slide, idx) in pptResult.slides" :key="idx" class="slide-item">
                <strong>第 {{ idx + 1 }} 页：{{ slide.title }}</strong>
                <p>{{ slide.content }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 投票 -->
        <div v-if="activeTab === 'vote'" class="tab-content">
          <div class="form-group">
            <label>投票标题</label>
            <input v-model="voteForm.title" class="input-field" placeholder="例如：最喜欢的学科" />
          </div>
          <div class="form-group">
            <label>选项（每行一个）</label>
            <textarea v-model="voteForm.optionsText" class="input-field" rows="4" placeholder="数学&#10;英语&#10;物理&#10;化学"></textarea>
          </div>
          <button class="btn-primary" @click="createVote" :disabled="!voteForm.title || !voteForm.optionsText">
            发起投票
          </button>
          <div v-if="voteResult" class="result-box">
            <h4>{{ voteResult.title }}</h4>
            <div v-for="option in voteResult.options" :key="option.id" class="vote-option">
              <div class="vote-option-header">
                <span>{{ option.text }}</span>
                <span>{{ option.vote_count }} 票</span>
              </div>
              <div class="vote-bar">
                <div class="vote-bar-fill" :style="{ width: option.percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 抽奖 -->
        <div v-if="activeTab === 'lottery'" class="tab-content">
          <div class="form-group">
            <label>抽奖标题</label>
            <input v-model="lotteryForm.title" class="input-field" placeholder="例如：课堂随机提问" />
          </div>
          <div class="form-group">
            <label>候选人（每行一个名字）</label>
            <textarea v-model="lotteryForm.candidatesText" class="input-field" rows="4" placeholder="张三&#10;李四&#10;王五&#10;赵六"></textarea>
          </div>
          <button class="btn-primary" @click="createLottery" :disabled="!lotteryForm.title || !lotteryForm.candidatesText">
            发起抽奖
          </button>
          <div v-if="lotteryResult" class="result-box">
            <h4>{{ lotteryResult.title }}</h4>
            <div v-if="lotteryResult.winner" class="winner-item">
              <component :is="icons.Trophy" class="winner-icon" />
              <span>中奖者：<strong>{{ lotteryResult.winner }}</strong></span>
            </div>
            <p v-else>暂无中奖结果</p>
          </div>
        </div>

        <!-- 测验 -->
        <div v-if="activeTab === 'quiz'" class="tab-content">
          <div class="form-group">
            <label>测验标题</label>
            <input v-model="quizForm.title" class="input-field" placeholder="例如：函数与导数测验" />
          </div>
          <div class="form-group">
            <label>题目（JSON 格式）</label>
            <textarea v-model="quizForm.questionsText" class="input-field" rows="6" placeholder='[{"question":"2+2=?","options":["3","4","5"],"correct_answer":"4"}]'></textarea>
          </div>
          <button class="btn-primary" @click="createQuiz" :disabled="!quizForm.title || quizLoading">
            {{ quizLoading ? '生成中...' : '发起测验' }}
          </button>
          <div v-if="quizResult" class="result-box">
            <h4>{{ quizResult.title }}</h4>
            <div v-if="quizResult.questions" class="quiz-list">
              <div v-for="(q, idx) in quizResult.questions" :key="idx" class="quiz-item">
                <strong>第 {{ idx + 1 }} 题：{{ q.question }}</strong>
                <div v-if="q.options" class="quiz-options">
                  <span v-for="(opt, oi) in q.options" :key="oi" class="quiz-option-tag">{{ opt }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  GraduationCap, Plus, Play, Award,
  BookOpen, Zap, Timer, BarChart
} from 'lucide-vue-next'
import { api } from '@/api/client'

const icons = {
  GraduationCap, Plus, Play, Trophy: Award,
  Presentation: BookOpen, Vote: Zap, Lottery: Timer, Quiz: BarChart
}

interface Classroom {
  id: string
  name: string
  code: string
  description?: string
}

const classrooms = ref<Classroom[]>([])
const showCreateDialog = ref(false)
const activeClassroom = ref<Classroom | null>(null)
const activeTab = ref('ppt')

const tabs = [
  { key: 'ppt', label: 'PPT 生成', icon: BookOpen },
  { key: 'vote', label: '投票', icon: Zap },
  { key: 'lottery', label: '抽奖', icon: Timer },
  { key: 'quiz', label: '测验', icon: BarChart }
]

// 创建课堂表单
const createForm = reactive({
  name: '',
  description: ''
})

// PPT 表单
const pptForm = reactive({ topic: '' })
const pptLoading = ref(false)
const pptResult = ref<any>(null)

// 投票表单
const voteForm = reactive({ title: '', optionsText: '' })
const voteResult = ref<any>(null)

// 抽奖表单
const lotteryForm = reactive({ title: '', candidatesText: '' })
const lotteryResult = ref<any>(null)

// 测验表单
const quizForm = reactive({ title: '', questionsText: '' })
const quizLoading = ref(false)
const quizResult = ref<any>(null)

// 加载课堂列表
async function loadClassrooms() {
  try {
    const res = await api.get('/classrooms')
    classrooms.value = res.data?.items || res.data || []
  } catch (e) {
    console.error('加载课堂列表失败:', e)
  }
}

// 创建课堂
async function createClassroom() {
  try {
    const res = await api.post('/classrooms', {
      name: createForm.name,
      description: createForm.description
    })
    classrooms.value.push(res.data)
    showCreateDialog.value = false
    createForm.name = ''
    createForm.description = ''
  } catch (e: any) {
    console.error('创建课堂失败:', e)
    alert('创建课堂失败: ' + (e.response?.data?.detail || e.message))
  }
}

// 打开课堂详情
function openClassroom(cls: Classroom) {
  activeClassroom.value = cls
  activeTab.value = 'ppt'
  pptResult.value = null
  voteResult.value = null
  lotteryResult.value = null
  quizResult.value = null
}

function closeClassroom() {
  activeClassroom.value = null
}

// 生成 PPT
async function generatePPT() {
  if (!activeClassroom.value) return
  pptLoading.value = true
  try {
    const res = await api.post(`/classrooms/${activeClassroom.value.id}/ppt`, {
      topic: pptForm.topic
    })
    pptResult.value = res.data
  } catch (e: any) {
    console.error('生成 PPT 失败:', e)
    alert('生成 PPT 失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    pptLoading.value = false
  }
}

// 发起投票
async function createVote() {
  if (!activeClassroom.value) return
  const options = voteForm.optionsText.split('\n').filter(o => o.trim())
  try {
    const res = await api.post(`/classrooms/${activeClassroom.value.id}/votes`, {
      title: voteForm.title,
      options: options
    })
    voteResult.value = res.data
  } catch (e: any) {
    console.error('发起投票失败:', e)
    alert('发起投票失败: ' + (e.response?.data?.detail || e.message))
  }
}

// 发起抽奖
async function createLottery() {
  if (!activeClassroom.value) return
  const candidates = lotteryForm.candidatesText.split('\n').filter(c => c.trim())
  try {
    const res = await api.post(`/classrooms/${activeClassroom.value.id}/lottery`, {
      title: lotteryForm.title,
      candidates: candidates
    })
    lotteryResult.value = res.data
  } catch (e: any) {
    console.error('发起抽奖失败:', e)
    alert('发起抽奖失败: ' + (e.response?.data?.detail || e.message))
  }
}

// 发起测验
async function createQuiz() {
  if (!activeClassroom.value) return
  quizLoading.value = true
  try {
    const questions = JSON.parse(quizForm.questionsText)
    const res = await api.post(`/classrooms/${activeClassroom.value.id}/quizzes`, {
      title: quizForm.title,
      questions: questions
    })
    quizResult.value = res.data
  } catch (e: any) {
    console.error('发起测验失败:', e)
    if (e instanceof SyntaxError) {
      alert('题目 JSON 格式错误，请检查输入')
    } else {
      alert('发起测验失败: ' + (e.response?.data?.detail || e.message))
    }
  } finally {
    quizLoading.value = false
  }
}

onMounted(() => {
  loadClassrooms()
})
</script>

<style lang="scss" scoped>
.classroom {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.action-bar {
  display: flex;
  gap: 12px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  .btn-icon {
    width: 18px;
    height: 18px;
  }
}

.section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;

  .title-icon {
    width: 22px;
    height: 22px;
    color: var(--primary-color);
  }
}

.count-badge {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 4px 12px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;

  .empty-icon {
    width: 48px;
    height: 48px;
    color: var(--text-muted);
  }

  p {
    font-size: 14px;
    color: var(--text-secondary);
    margin: 0;
  }
}

.classroom-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 24px;
}

.classroom-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;

  strong {
    color: var(--primary-light);
  }
}

.card-actions {
  .action-btn {
    width: 100%;
    padding: 10px;
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid var(--primary-color);
    border-radius: var(--radius-md);
    color: var(--primary-color);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.2s ease;

    &:hover {
      background: rgba(99, 102, 241, 0.2);
    }

    .action-icon {
      width: 16px;
      height: 16px;
    }
  }
}

// 对话框
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  width: 90%;
  max-width: 480px;
  max-height: 80vh;
  overflow-y: auto;
}

.dialog-wide {
  max-width: 640px;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.dialog-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
  padding: 0 8px;

  &:hover {
    color: var(--text-primary);
  }
}

.form-group {
  margin-bottom: 16px;

  label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 6px;
  }

  .input-field {
    width: 100%;
    padding: 10px 14px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s ease;

    &:focus {
      border-color: var(--primary-color);
    }

    &::placeholder {
      color: var(--text-muted);
    }
  }
}

.dialog-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;

  .btn-cancel {
    padding: 10px 20px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    font-size: 14px;
    cursor: pointer;

    &:hover {
      background: var(--bg-hover);
      color: var(--text-primary);
    }
  }
}

// 标签页
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;

  .tab-icon {
    width: 15px;
    height: 15px;
  }

  &:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  &.active {
    background: rgba(99, 102, 241, 0.15);
    border-color: var(--primary-color);
    color: var(--primary-light);
  }
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-box {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-top: 12px;

  h4 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 12px 0;
  }
}

// 投票结果
.vote-option {
  margin-bottom: 12px;

  .vote-option-header {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 4px;
  }

  .vote-bar {
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    overflow: hidden;

    .vote-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
      border-radius: 4px;
      transition: width 0.5s ease;
    }
  }
}

// PPT 幻灯片
.slides-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.slide-item {
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--primary-color);

  strong {
    display: block;
    font-size: 14px;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  p {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 0;
  }
}

// 抽奖中奖者
.winner-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;

  .winner-icon {
    width: 18px;
    height: 18px;
    color: rgba(245, 158, 11, 0.9);
  }

  strong {
    color: rgba(245, 158, 11, 0.9);
  }
}

// 测验题目
.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quiz-item {
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);

  strong {
    display: block;
    font-size: 14px;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .quiz-options {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
  }

  .quiz-option-tag {
    padding: 4px 12px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    font-size: 12px;
    color: var(--text-secondary);
  }
}

@media (max-width: 768px) {
  .classroom-grid {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .dialog {
    width: 95%;
    padding: 16px;
  }

  .tabs {
    flex-wrap: wrap;
  }
}
</style>

<template>
  <div class="mistakes-page">
    <!-- 统计概览 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <component :is="icons.FileText" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总错题数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <component :is="icons.AlertCircle" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.unsolved }}</div>
          <div class="stat-label">待解决</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <component :is="icons.Eye" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.reviewing }}</div>
          <div class="stat-label">复习中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <component :is="icons.CheckCircle" class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.mastered }}</div>
          <div class="stat-label">已掌握</div>
        </div>
      </div>
    </div>

    <!-- 学科分布 -->
    <div class="subject-distribution" v-if="Object.keys(stats.by_subject).length > 0">
      <h3 class="section-title">
        <component :is="icons.BarChart" class="title-icon" />
        学科分布
      </h3>
      <div class="subject-bars">
        <div
          v-for="(count, subject) in stats.by_subject"
          :key="subject"
          class="subject-bar-item"
        >
          <span class="subject-name">{{ subject }}</span>
          <div class="subject-bar">
            <div
              class="subject-bar-fill"
              :style="{ width: getSubjectPercent(count) + '%' }"
            ></div>
          </div>
          <span class="subject-count">{{ count }} 题</span>
        </div>
      </div>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <select v-model="filterSubject" class="filter-select" @change="loadMistakes">
          <option value="">全部学科</option>
          <option v-for="s in subjectOptions" :key="s" :value="s">{{ s }}</option>
        </select>
        <select v-model="filterStatus" class="filter-select" @change="loadMistakes">
          <option value="">全部状态</option>
          <option value="unsolved">待解决</option>
          <option value="reviewing">复习中</option>
          <option value="mastered">已掌握</option>
        </select>
        <button
          class="filter-btn"
          :class="{ active: showFavoritesOnly }"
          @click="toggleFavoriteFilter"
          title="只看收藏"
        >
          <component :is="icons.Heart" class="btn-icon" />
          {{ showFavoritesOnly ? '显示全部' : '只看收藏' }}
        </button>
        <div class="search-input-wrapper">
          <component :is="icons.Search" class="search-icon" />
          <input
            v-model="keyword"
            type="text"
            placeholder="搜索错题..."
            class="search-input"
            @input="debounceSearch"
          />
        </div>
      </div>
      <div class="filter-right">
        <button class="btn-primary" @click="showAddModal = true">
          <component :is="icons.Plus" class="btn-icon" />
          添加错题
        </button>
      </div>
    </div>

    <!-- 错题列表 -->
    <div class="mistakes-list">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <div v-else-if="displayedMistakes.length === 0" class="empty-state">
        <component :is="icons.FileText" class="empty-icon" />
        <p class="empty-text">{{ showFavoritesOnly ? '暂无收藏的错题' : '暂无错题记录' }}</p>
        <p v-if="!showFavoritesOnly" class="empty-hint">点击"添加错题"开始记录</p>
      </div>

      <div v-else class="mistakes-grid">
        <div
          v-for="mistake in displayedMistakes"
          :key="mistake.id"
          class="mistake-card card"
          :class="mistake.status"
        >
          <div class="mistake-header">
            <span class="subject-tag" :class="getSubjectClass(mistake.subject)">
              {{ mistake.subject }}
            </span>
            <div class="header-actions">
              <button
                class="favorite-btn"
                :class="{ favorited: mistakeFavorites[mistake.id] }"
                :disabled="favoriteLoading[mistake.id]"
                @click.stop="toggleFavorite(mistake.id)"
                :title="mistakeFavorites[mistake.id] ? '取消收藏' : '收藏'"
              >
                <Heart class="btn-icon" :fill="mistakeFavorites[mistake.id] ? 'currentColor' : 'none'" />
              </button>
              <span class="status-tag" :class="mistake.status">
                {{ getStatusText(mistake.status) }}
              </span>
            </div>
          </div>

          <div class="mistake-question">{{ mistake.question }}</div>

          <div class="mistake-meta">
            <div class="meta-item">
              <span class="meta-label">难度</span>
              <div class="difficulty-stars">
                <span
                  v-for="i in 5"
                  :key="i"
                  class="star"
                  :class="{ active: i <= mistake.difficulty }"
                >★</span>
              </div>
            </div>
            <div class="meta-item" v-if="mistake.knowledge_point">
              <span class="meta-label">知识点</span>
              <span class="meta-value">{{ mistake.knowledge_point }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">复习次数</span>
              <span class="meta-value">{{ mistake.review_count }} 次</span>
            </div>
          </div>

          <div class="mistake-actions">
            <button class="action-btn review" @click="handleReview(mistake.id)">
              <component :is="icons.Eye" class="btn-icon" />
              复习
            </button>
            <button class="action-btn edit" @click="handleEdit(mistake)">
              <component :is="icons.Edit" class="btn-icon" />
              编辑
            </button>
            <button class="action-btn delete" @click="handleDelete(mistake.id)">
              <component :is="icons.Trash2" class="btn-icon" />
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="totalPages > 1">
      <button
        class="page-btn"
        :disabled="currentPage <= 1"
        @click="changePage(currentPage - 1)"
      >
        上一页
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button
        class="page-btn"
        :disabled="currentPage >= totalPages"
        @click="changePage(currentPage + 1)"
      >
        下一页
      </button>
    </div>

    <!-- 添加/编辑错题弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div class="modal-overlay" v-if="showAddModal" @click.self="showAddModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <h3>{{ editingMistake ? '编辑错题' : '添加错题' }}</h3>
              <button class="modal-close" @click="showAddModal = false">
                <component :is="icons.X" class="close-icon" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>章节</label>
                <input v-model="formData.subject" type="text" placeholder="如：机器学习、深度学习" />
              </div>
              <div class="form-group">
                <label>题目内容</label>
                <textarea v-model="formData.question" rows="3" placeholder="输入题目内容"></textarea>
              </div>
              <div class="form-group">
                <label>正确答案</label>
                <textarea v-model="formData.correct_answer" rows="2" placeholder="输入正确答案"></textarea>
              </div>
              <div class="form-group">
                <label>我的答案</label>
                <textarea v-model="formData.user_answer" rows="2" placeholder="输入你当时的答案"></textarea>
              </div>
              <div class="form-group">
                <label>解析/反思</label>
                <textarea v-model="formData.analysis" rows="3" placeholder="输入解析或反思"></textarea>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>知识点</label>
                  <input v-model="formData.knowledge_point" type="text" placeholder="相关知识点" />
                </div>
                <div class="form-group">
                  <label>难度 (1-5)</label>
                  <input v-model.number="formData.difficulty" type="number" min="1" max="5" />
                </div>
              </div>
              <div class="form-group">
                <label>标签（逗号分隔）</label>
                <input v-model="formData.tagsStr" type="text" placeholder="如：易错,重点,高频" />
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="showAddModal = false">取消</button>
              <button class="btn-confirm" @click="handleSubmit" :disabled="submitting">
                {{ submitting ? '提交中...' : '确认' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import {
  FileText, AlertCircle, Eye, CheckCircle, BarChart,
  Search, Plus, Edit, Trash2, X, Heart
} from 'lucide-vue-next'
import {
  getMistakes, getMistakeStats, createMistake, updateMistake,
  deleteMistake, reviewMistake,
  type MistakeItem, type MistakeStatsResponse
} from '@/api/mistakes'
import {
  getFavorites, createFavorite, removeFavoriteByTarget,
  type FavoriteItem
} from '@/api/favorites'

const icons = { FileText, AlertCircle, Eye, CheckCircle, BarChart, Search, Plus, Edit, Trash2, X, Heart }

// 统计数据
const stats = ref<MistakeStatsResponse>({
  total: 0,
  unsolved: 0,
  reviewing: 0,
  mastered: 0,
  by_subject: {}
})

// 列表数据
const mistakes = ref<MistakeItem[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = 20
const total = ref(0)
const totalPages = computed(() => Math.ceil(total.value / pageSize))

// 筛选
const filterSubject = ref('')
const filterStatus = ref('')
const keyword = ref('')
const showFavoritesOnly = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

// 与实际数据保持一致的学科选项
const defaultSubjects = ['数学', '物理', '化学', '英语', '生物']
const subjectOptions = computed(() => {
  const set = new Set(defaultSubjects)
  Object.keys(stats.value.by_subject).forEach(s => set.add(s))
  mistakes.value.forEach(m => set.add(m.subject))
  return Array.from(set)
})

// 收藏筛选后的展示列表
const displayedMistakes = computed(() => {
  if (!showFavoritesOnly.value) return mistakes.value
  return mistakes.value.filter(m => mistakeFavorites.value[m.id])
})

const toggleFavoriteFilter = () => {
  showFavoritesOnly.value = !showFavoritesOnly.value
}

watch(showFavoritesOnly, () => {
  currentPage.value = 1
  loadMistakes()
})

// 收藏状态
const mistakeFavorites = ref<Record<string, FavoriteItem | undefined>>({})
const favoriteLoading = ref<Record<string, boolean>>({})

// 弹窗
const showAddModal = ref(false)
const editingMistake = ref<MistakeItem | null>(null)
const submitting = ref(false)
const formData = ref({
  subject: '',
  question: '',
  correct_answer: '',
  user_answer: '',
  analysis: '',
  knowledge_point: '',
  difficulty: 3,
  tagsStr: ''
})

// 加载统计数据
const loadStats = async () => {
  try {
    stats.value = await getMistakeStats()
  } catch (e) {
    console.error('加载错题统计失败:', e)
  }
}

// 加载错题收藏状态
const loadMistakeFavorites = async () => {
  try {
    const res = await getFavorites({ target_type: 'mistake', page_size: 100 })
    const map: Record<string, FavoriteItem | undefined> = {}
    res.items.forEach(item => {
      map[item.target_id] = item
    })
    mistakeFavorites.value = map
  } catch (e) {
    console.error('加载错题收藏状态失败:', e)
  }
}

// 加载错题列表
const loadMistakes = async () => {
  loading.value = true
  try {
    const res = await getMistakes({
      subject: filterSubject.value || undefined,
      status: filterStatus.value || undefined,
      keyword: keyword.value || undefined,
      page: currentPage.value,
      page_size: showFavoritesOnly.value ? 100 : pageSize
    })
    mistakes.value = res.items
    total.value = res.total
    await loadMistakeFavorites()
  } catch (e) {
    console.error('加载错题列表失败:', e)
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  currentPage.value = page
  loadMistakes()
}

const debounceSearch = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadMistakes()
  }, 300)
}

const getSubjectPercent = (count: number): number => {
  const max = Math.max(...Object.values(stats.value.by_subject))
  return max > 0 ? Math.round((count / max) * 100) : 0
}

const getSubjectClass = (subject: string): string => {
  const classMap: Record<string, string> = {
    '数学': 'math',
    '物理': 'physics',
    '化学': 'chemistry',
    '英语': 'english',
    '生物': 'biology',
    '人工智能概述': 'overview',
    '搜索与推理': 'search',
    '机器学习': 'ml',
    '深度学习': 'dl',
    '自然语言处理': 'nlp',
    '计算机视觉': 'cv',
    '人工智能伦理': 'ethics'
  }
  return classMap[subject] || 'default'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    unsolved: '待解决',
    reviewing: '复习中',
    mastered: '已掌握'
  }
  return map[status] || status
}

// 复习错题
const handleReview = async (mistakeId: string) => {
  try {
    await reviewMistake(mistakeId)
    await Promise.all([loadStats(), loadMistakes()])
  } catch (e) {
    console.error('复习失败:', e)
  }
}

// 编辑错题
const handleEdit = (mistake: MistakeItem) => {
  editingMistake.value = mistake
  formData.value = {
    subject: mistake.subject,
    question: mistake.question,
    correct_answer: mistake.correct_answer,
    user_answer: mistake.user_answer || '',
    analysis: mistake.analysis || '',
    knowledge_point: mistake.knowledge_point || '',
    difficulty: mistake.difficulty,
    tagsStr: mistake.tags || ''
  }
  showAddModal.value = true
}

// 删除错题
const handleDelete = async (mistakeId: string) => {
  if (!confirm('确定要删除这道错题吗？')) return
  try {
    await deleteMistake(mistakeId)
    await Promise.all([loadStats(), loadMistakes()])
  } catch (e) {
    console.error('删除失败:', e)
  }
}

// 切换收藏状态
const toggleFavorite = async (mistakeId: string) => {
  if (favoriteLoading.value[mistakeId]) return
  favoriteLoading.value[mistakeId] = true
  try {
    if (mistakeFavorites.value[mistakeId]) {
      await removeFavoriteByTarget('mistake', mistakeId)
      mistakeFavorites.value[mistakeId] = undefined
    } else {
      const favorite = await createFavorite({ target_type: 'mistake', target_id: mistakeId })
      mistakeFavorites.value[mistakeId] = favorite
    }
  } catch (e) {
    console.error('收藏操作失败:', e)
    alert('收藏操作失败，请重试')
  } finally {
    favoriteLoading.value[mistakeId] = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formData.value.subject || !formData.value.question || !formData.value.correct_answer) {
    alert('请填写学科、题目和正确答案')
    return
  }

  submitting.value = true
  try {
    const tags = formData.value.tagsStr
      ? formData.value.tagsStr.split(',').map(t => t.trim()).filter(Boolean)
      : undefined

    const data = {
      subject: formData.value.subject,
      question: formData.value.question,
      correct_answer: formData.value.correct_answer,
      user_answer: formData.value.user_answer || undefined,
      analysis: formData.value.analysis || undefined,
      knowledge_point: formData.value.knowledge_point || undefined,
      difficulty: formData.value.difficulty,
      tags
    }

    if (editingMistake.value) {
      await updateMistake(editingMistake.value.id, data)
    } else {
      await createMistake(data)
    }

    showAddModal.value = false
    editingMistake.value = null
    resetForm()
    await Promise.all([loadStats(), loadMistakes()])
  } catch (e) {
    console.error('提交失败:', e)
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  formData.value = {
    subject: '',
    question: '',
    correct_answer: '',
    user_answer: '',
    analysis: '',
    knowledge_point: '',
    difficulty: 3,
    tagsStr: ''
  }
}

onMounted(() => {
  loadStats()
  loadMistakes()
})
</script>

<style lang="scss" scoped>
.mistakes-page {
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
  &.red { background: rgba(239, 68, 68, 0.15); .icon { color: #f87171; } }
  &.orange { background: rgba(245, 158, 11, 0.15); .icon { color: #fbbf24; } }
  &.green { background: rgba(16, 185, 129, 0.15); .icon { color: #34d399; } }
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

.subject-distribution {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px;

  .title-icon { width: 18px; height: 18px; color: var(--primary-color); }
}

.subject-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.subject-bar-item {
  display: flex;
  align-items: center;
  gap: 12px;

  .subject-name {
    width: 60px;
    font-size: 13px;
    color: var(--text-secondary);
    text-align: right;
  }

  .subject-bar {
    flex: 1;
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    overflow: hidden;

    .subject-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
      border-radius: 4px;
      transition: width 0.5s ease;
    }
  }

  .subject-count {
    width: 50px;
    font-size: 12px;
    color: var(--text-muted);
  }
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-md);
  color: #e2e8f0;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  .btn-icon { width: 14px; height: 14px; }

  &:hover {
    border-color: #ec4899;
    color: #ec4899;
  }

  &.active {
    background: rgba(236, 72, 153, 0.15);
    border-color: #ec4899;
    color: #ec4899;
  }
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

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-md);
  height: 40px;
  min-width: 180px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;

  &:hover,
  &:focus-within {
    border-color: #60a5fa;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), 0 0 0 1px #60a5fa;
  }

  .search-icon { width: 15px; height: 15px; color: #94a3b8; }

  .search-input {
    background: transparent;
    border: none;
    outline: none;
    color: #e2e8f0;
    font-size: 13px;
    width: 160px;

    &::placeholder { color: #64748b; }
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

.mistakes-list {
  min-height: 200px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: var(--text-muted);
  font-size: 14px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-muted);

  .empty-icon { width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.5; }
  .empty-text { font-size: 16px; margin: 0 0 4px; }
  .empty-hint { font-size: 13px; margin: 0; }
}

.mistakes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.mistake-card {
  display: flex;
  flex-direction: column;
  gap: 12px;

  &.mastered { opacity: 0.7; }
}

.mistake-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;

  .btn-icon { width: 14px; height: 14px; }

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

.subject-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;

  &.math { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
  &.physics { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
  &.chemistry { background: rgba(16, 185, 129, 0.15); color: #34d399; }
  &.english { background: rgba(239, 68, 68, 0.15); color: #f87171; }
  &.biology { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
  &.overview { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
  &.search { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
  &.ml { background: rgba(16, 185, 129, 0.15); color: #34d399; }
  &.dl { background: rgba(239, 68, 68, 0.15); color: #f87171; }
  &.nlp { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
  &.cv { background: rgba(6, 182, 212, 0.15); color: #22d3ee; }
  &.ethics { background: rgba(236, 72, 153, 0.15); color: #f472b6; }
  &.default { background: rgba(99, 102, 241, 0.15); color: var(--primary-color); }
}

.status-tag {
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;

  &.unsolved { background: rgba(239, 68, 68, 0.15); color: #f87171; }
  &.reviewing { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
  &.mastered { background: rgba(16, 185, 129, 0.15); color: #34d399; }
}

.mistake-question {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.mistake-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;

  .meta-label {
    font-size: 11px;
    color: var(--text-muted);
    min-width: 56px;
  }

  .meta-value {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.difficulty-stars {
  display: flex;
  gap: 2px;

  .star {
    font-size: 12px;
    color: var(--border-color);

    &.active { color: #fbbf24; }
  }
}

.mistake-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.action-btn {
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

  &.review {
    background: rgba(59, 130, 246, 0.1);
    color: #60a5fa;
    &:hover { background: rgba(59, 130, 246, 0.2); }
  }

  &.edit {
    background: rgba(245, 158, 11, 0.1);
    color: #fbbf24;
    &:hover { background: rgba(245, 158, 11, 0.2); }
  }

  &.delete {
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
    &:hover { background: rgba(239, 68, 68, 0.2); }
  }
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px 0;
}

.page-btn {
  padding: 8px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: var(--bg-card);
    border-color: var(--primary-color);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.page-info {
  font-size: 13px;
  color: var(--text-muted);
}

/* 弹窗样式 */
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
  max-width: 560px;
  max-height: 80vh;
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

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }
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

  &:hover {
    background: var(--bg-card);
    border-color: var(--primary-color);
  }
}

.modal-body {
  flex: 1;
  overflow-y: auto;
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

  input, textarea {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    color: var(--text-primary);
    font-size: 13px;
    resize: vertical;

    &:focus {
      outline: none;
      border-color: var(--primary-color);
    }

    &::placeholder { color: var(--text-muted); }
  }
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
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

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>

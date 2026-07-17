<template>
  <div class="learning-path-page">
    <!-- 顶部筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <select v-model="activeStatus" class="filter-select" @change="loadPaths">
          <option value="all">全部状态</option>
          <option value="active">进行中</option>
          <option value="completed">已完成</option>
          <option value="paused">已暂停</option>
        </select>
        <div class="search-box">
          <component :is="icons.Search" class="search-icon" />
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索学习路径..."
            class="search-input"
            @input="onSearch"
          />
          <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''; onSearch()">
            <component :is="icons.X" class="clear-icon" />
          </button>
        </div>
      </div>
      <div class="filter-right">
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-num green">{{ progressStats.completed_paths }}</span>
            <span class="stat-label">已完成</span>
          </div>
          <div class="stat-item">
            <span class="stat-num blue">{{ progressStats.total_paths }}</span>
            <span class="stat-label">总路径</span>
          </div>
          <div class="stat-item">
            <span class="stat-num purple">{{ progressStats.overall_progress }}%</span>
            <span class="stat-label">总进度</span>
          </div>
        </div>
        <button class="btn-primary" @click="showCreateModal = true">
          <component :is="icons.Plus" class="btn-icon" />
          新建路径
        </button>
      </div>
    </div>

    <!-- 搜索结果提示 -->
    <div v-if="searchQuery && searchResults.length > 0" class="search-hint">
      找到 {{ searchResults.length }} 个匹配步骤
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>加载学习路径...</span>
    </div>

    <div v-else-if="visiblePaths.length === 0" class="empty-state">
      <component :is="icons.Map" class="empty-icon" />
      <p class="empty-text">暂无学习路径</p>
      <p class="empty-hint">点击"新建路径"开始规划学习路线</p>
    </div>

    <!-- 路径地图区域 -->
    <div v-else class="map-container">
      <div class="map-scroll">
        <div
          v-for="path in visiblePaths"
          :key="path.id"
          class="subject-section active"
        >
          <!-- 路径标题 -->
          <div class="subject-header">
            <div class="subject-icon-wrap" :style="{ background: path.color }">
              <component :is="path.icon" class="subject-icon" />
            </div>
            <div class="subject-info">
              <h3 class="subject-name">{{ path.title }}</h3>
              <span class="subject-desc">{{ path.description || '暂无描述' }}</span>
            </div>
            <div class="subject-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: path.progress + '%', background: path.color }"></div>
              </div>
              <span class="progress-text">{{ path.progress }}%</span>
            </div>
            <button
              class="delete-path-btn"
              @click.stop="handleDeletePath(path.id)"
              title="删除路径"
            >
              <component :is="icons.Trash2" class="btn-icon" />
            </button>
          </div>

          <!-- 路径地图 -->
          <div class="path-map" :style="{ minHeight: path.mapHeight + 'px' }">
            <svg class="path-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
              <defs>
                <linearGradient :id="`pathGrad-${path.id}`" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" :stop-color="path.color" stop-opacity="0.8" />
                  <stop offset="100%" :stop-color="path.color" stop-opacity="0.3" />
                </linearGradient>
              </defs>
              <path
                :d="getPathD(path.nodes)"
                fill="none"
                stroke="var(--border-color)"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                opacity="0.2"
              />
              <path
                :d="getPathD(path.nodes)"
                fill="none"
                :stroke="`url(#pathGrad-${path.id})`"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                :stroke-dasharray="path.pathLength"
                :stroke-dashoffset="path.pathOffset"
                style="transition: stroke-dashoffset 0.8s ease"
              />
            </svg>

            <div
              v-for="(node, index) in path.nodes"
              :key="`${path.id}-${index}`"
              class="map-node"
              :class="[
                node.status,
                { searched: isNodeSearched(node) }
              ]"
              :style="{ left: node.x + '%', top: node.y + '%' }"
              @click="selectNode(path, node, index)"
            >
              <div class="node-ring" :class="node.status"></div>
              <div class="node-icon-wrap" :class="node.status">
                <component v-if="node.status === 'unlocked'" :is="node.icon" class="node-icon" />
                <component v-else :is="icons.Lock" class="node-icon" />
              </div>
              <div class="node-label" :class="node.status">
                {{ node.title }}
              </div>
              <div class="node-index" :class="node.status">{{ index + 1 }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 步骤详情面板 -->
    <Transition name="slide">
      <div class="detail-panel" v-if="selectedNode">
        <div class="panel-header">
          <div class="panel-title-row">
            <div class="title-icon" :class="selectedNode.status" :style="{ background: selectedPathColor }">
              <component v-if="selectedNode.status === 'unlocked'" :is="selectedNode.icon" class="icon" />
              <component v-else :is="icons.Lock" class="icon" />
            </div>
            <div>
              <h3 class="panel-title">{{ selectedNode.title }}</h3>
              <span class="panel-subtitle">{{ selectedPathTitle }}</span>
            </div>
          </div>
          <button class="close-btn" @click="selectedNode = null">
            <component :is="icons.X" class="close-icon" />
          </button>
        </div>
        <div class="panel-content">
          <div class="info-section">
            <h4 class="section-title">步骤概述</h4>
            <p class="section-desc">{{ selectedNode.description || '暂无描述' }}</p>
          </div>
          <div class="info-section">
            <h4 class="section-title">学习状态</h4>
            <div class="status-badge" :class="selectedNode.status">
              <component v-if="selectedNode.status === 'unlocked'" :is="icons.Unlock" class="badge-icon" />
              <component v-else :is="icons.Lock" class="badge-icon" />
              <span>{{ selectedNode.status === 'unlocked' ? '已完成' : '未完成' }}</span>
            </div>
          </div>
          <div class="info-section">
            <h4 class="section-title">学习信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <component :is="icons.BookOpen" class="info-icon" />
                <span>所属路径</span>
                <strong>{{ selectedPathTitle }}</strong>
              </div>
              <div class="info-item">
                <component :is="icons.Clock" class="info-icon" />
                <span>预计时长</span>
                <strong>{{ selectedNode.duration || '未设置' }}</strong>
              </div>
            </div>
          </div>
          <div class="panel-actions">
            <button class="btn-secondary" @click="selectedNode = null">关闭</button>
            <button
              v-if="selectedNode.status === 'locked'"
              class="btn-primary"
              @click="completeSelectedStep"
              :disabled="completingStep"
            >
              {{ completingStep ? '提交中...' : '标记完成' }}
            </button>
            <button v-else class="btn-primary" disabled>已完成</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 新建路径弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
        <div class="modal-overlay" v-if="showCreateModal" @click.self="showCreateModal = false">
          <div class="modal-content">
            <div class="modal-header">
              <h3>新建学习路径</h3>
              <button class="modal-close" @click="showCreateModal = false">
                <component :is="icons.X" class="close-icon" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>路径标题</label>
                <input v-model="createForm.title" type="text" placeholder="如：机器学习入门" />
              </div>
              <div class="form-group">
                <label>路径描述</label>
                <textarea v-model="createForm.description" rows="2" placeholder="描述该学习路径的目标"></textarea>
              </div>
              <div class="form-group">
                <label>学习步骤（每行一个步骤，用 | 分隔标题、描述和预计时长）</label>
                <textarea
                  v-model="createForm.stepsText"
                  rows="6"
                  placeholder="如：&#10;导论 | 了解基本概念 | 30&#10;线性回归 | 掌握线性模型原理 | 60"
                ></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn-cancel" @click="showCreateModal = false">取消</button>
              <button class="btn-confirm" @click="handleCreatePath" :disabled="creatingPath">
                {{ creatingPath ? '创建中...' : '创建' }}
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
  Search, X, BookOpen, Clock, Lock, Unlock,
  Calculator, FlaskConical, Code, Globe, GraduationCap,
  FolderOpen, Target, ChevronLeft,
  Lightbulb, Cpu, Shield, Aperture, Map, Plus, Trash2
} from 'lucide-vue-next'
import {
  getLearningPaths, getLearningPathProgress, createLearningPath,
  deleteLearningPath, completeLearningPathStep,
  type LearningPathItem, type LearningPathProgressStats, type LearningPathStep
} from '@/api/learningPaths'

const icons = {
  Search, X, BookOpen, Clock, Lock, Unlock,
  Calculator, FlaskConical, Code, Globe, GraduationCap,
  FolderOpen, Target, ChevronLeft,
  Lightbulb, Cpu, Shield, Aperture, Map, Plus, Trash2
}

// ===== 状态 =====
const loading = ref(false)
const activeStatus = ref('all')
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const selectedNode = ref<any>(null)
const selectedPathId = ref<string>('')
const selectedStepIndex = ref<number>(-1)
const completingStep = ref(false)

const paths = ref<LearningPathItem[]>([])
const progressStats = ref<LearningPathProgressStats>({
  total_paths: 0,
  active_paths: 0,
  completed_paths: 0,
  total_steps: 0,
  completed_steps: 0,
  overall_progress: 0
})

// 新建路径弹窗
const showCreateModal = ref(false)
const creatingPath = ref(false)
const createForm = ref({
  title: '',
  description: '',
  stepsText: ''
})

// ===== 颜色与图标映射 =====
const colorPalette = [
  '#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'
]

const iconPalette = [
  BookOpen, Search, Code, Cpu, Globe, Aperture, Shield, Lightbulb, Calculator, FlaskConical
]

const getPathColor = (pathId: string): string => {
  let hash = 0
  for (let i = 0; i < pathId.length; i++) {
    hash = pathId.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colorPalette[Math.abs(hash) % colorPalette.length]
}

const getPathIcon = (pathId: string): any => {
  let hash = 0
  for (let i = 0; i < pathId.length; i++) {
    hash = pathId.charCodeAt(i) + ((hash << 5) - hash)
  }
  return iconPalette[Math.abs(hash) % iconPalette.length]
}

const getNodeIcon = (pathId: string, index: number): any => {
  return iconPalette[(Math.abs(index) + pathId.length) % iconPalette.length]
}

// ===== 数据转换 =====
interface PathNode {
  title: string
  description: string
  duration: string
  status: 'unlocked' | 'locked'
  icon: any
  x: number
  y: number
  pathId: string
  stepIndex: number
}

interface PathView {
  id: string
  title: string
  description: string | null
  status: string
  color: string
  icon: any
  progress: number
  pathLength: number
  pathOffset: number
  mapHeight: number
  nodes: PathNode[]
}

function generateSnakePath(count: number): { x: number; y: number }[] {
  const positions: { x: number; y: number }[] = []
  const cols = 5
  const colWidth = 20
  const rowHeight = 16
  const startX = 10
  const startY = 8

  for (let i = 0; i < count; i++) {
    const col = i % cols
    const row = Math.floor(i / cols)
    const actualCol = row % 2 === 0 ? col : (cols - 1 - col)
    positions.push({
      x: startX + actualCol * colWidth,
      y: startY + row * rowHeight
    })
  }
  return positions
}

function parseSteps(path: LearningPathItem): PathNode[] {
  try {
    const steps = JSON.parse(path.steps || '[]')
    const positions = generateSnakePath(steps.length)
    return steps.map((step: any, index: number) => ({
      title: step.title || `步骤 ${index + 1}`,
      description: step.description || '',
      duration: step.duration ? `${step.duration} 分钟` : '未设置',
      status: step.status === 'completed' ? 'unlocked' : 'locked',
      icon: getNodeIcon(path.id, index),
      x: positions[index]?.x ?? 10,
      y: positions[index]?.y ?? 10,
      pathId: path.id,
      stepIndex: index
    }))
  } catch {
    return []
  }
}

const pathViews = computed<PathView[]>(() => {
  return paths.value.map(path => {
    const nodes = parseSteps(path)
    const unlocked = nodes.filter(n => n.status === 'unlocked').length
    const progress = nodes.length > 0 ? Math.round((unlocked / nodes.length) * 100) : 0
    const pathLength = 2000
    const pathOffset = pathLength * (1 - unlocked / nodes.length)
    const mapHeight = Math.max(400, Math.ceil(nodes.length / 5) * 160 + 160)

    return {
      id: path.id,
      title: path.title,
      description: path.description,
      status: path.status,
      color: getPathColor(path.id),
      icon: getPathIcon(path.id),
      progress,
      pathLength,
      pathOffset,
      mapHeight,
      nodes
    }
  })
})

const visiblePaths = computed<PathView[]>(() => {
  let result = pathViews.value

  if (activeStatus.value !== 'all') {
    result = result.filter(p => p.status === activeStatus.value)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      p.title.toLowerCase().includes(q) ||
      (p.description && p.description.toLowerCase().includes(q)) ||
      p.nodes.some(n =>
        n.title.toLowerCase().includes(q) ||
        n.description.toLowerCase().includes(q)
      )
    )
  }

  return result
})

// ===== 方法 =====
const loadPaths = async () => {
  loading.value = true
  try {
    const [pathRes, statsRes] = await Promise.all([
      getLearningPaths({ status: activeStatus.value === 'all' ? undefined : activeStatus.value, page_size: 100 }),
      getLearningPathProgress()
    ])
    paths.value = pathRes.items
    progressStats.value = statsRes
  } catch (e) {
    console.error('加载学习路径失败:', e)
  } finally {
    loading.value = false
  }
}

const onSearch = () => {
  if (!searchQuery.value) {
    searchResults.value = []
    return
  }
  const q = searchQuery.value.toLowerCase()
  searchResults.value = visiblePaths.value.flatMap(p =>
    p.nodes.filter(n =>
      n.title.toLowerCase().includes(q) ||
      n.description.toLowerCase().includes(q)
    )
  )
}

function getPathD(nodes: PathNode[]): string {
  if (nodes.length === 0) return ''
  if (nodes.length === 1) return `M ${nodes[0].x} ${nodes[0].y} L ${nodes[0].x + 0.5} ${nodes[0].y}`
  let d = `M ${nodes[0].x} ${nodes[0].y}`
  for (let i = 1; i < nodes.length; i++) {
    const prev = nodes[i - 1]
    const curr = nodes[i]
    const cx1 = prev.x + (curr.x - prev.x) * 0.5
    const cy1 = prev.y
    const cx2 = curr.x - (curr.x - prev.x) * 0.5
    const cy2 = curr.y
    d += ` C ${cx1} ${cy1}, ${cx2} ${cy2}, ${curr.x} ${curr.y}`
  }
  return d
}

function isNodeSearched(node: PathNode): boolean {
  if (!searchQuery.value) return false
  const q = searchQuery.value.toLowerCase()
  return node.title.toLowerCase().includes(q) || node.description.toLowerCase().includes(q)
}

const selectedPathTitle = computed(() => {
  const path = paths.value.find(p => p.id === selectedPathId.value)
  return path ? path.title : ''
})

const selectedPathColor = computed(() => {
  return selectedPathId.value ? getPathColor(selectedPathId.value) : '#6366f1'
})

function selectNode(path: PathView, node: PathNode, index: number) {
  selectedPathId.value = path.id
  selectedStepIndex.value = index
  selectedNode.value = node
}

const completeSelectedStep = async () => {
  if (!selectedPathId.value || selectedStepIndex.value < 0) return
  completingStep.value = true
  try {
    await completeLearningPathStep(selectedPathId.value, selectedStepIndex.value)
    selectedNode.value.status = 'unlocked'
    await loadPaths()
  } catch (e) {
    console.error('标记步骤完成失败:', e)
    alert('标记步骤完成失败，请重试')
  } finally {
    completingStep.value = false
  }
}

const handleCreatePath = async () => {
  if (!createForm.value.title.trim()) {
    alert('请输入路径标题')
    return
  }

  const steps: LearningPathStep[] = []
  if (createForm.value.stepsText.trim()) {
    createForm.value.stepsText.split('\n').forEach(line => {
      const parts = line.split('|').map(s => s.trim())
      if (parts[0]) {
        steps.push({
          title: parts[0],
          description: parts[1] || '',
          duration: parts[2] ? parseInt(parts[2], 10) || undefined : undefined,
          status: 'pending'
        })
      }
    })
  }

  creatingPath.value = true
  try {
    await createLearningPath({
      title: createForm.value.title.trim(),
      description: createForm.value.description.trim() || undefined,
      steps
    })
    showCreateModal.value = false
    createForm.value = { title: '', description: '', stepsText: '' }
    await loadPaths()
  } catch (e) {
    console.error('创建学习路径失败:', e)
    alert('创建学习路径失败，请重试')
  } finally {
    creatingPath.value = false
  }
}

const handleDeletePath = async (pathId: string) => {
  if (!confirm('确定要删除这条学习路径吗？')) return
  try {
    await deleteLearningPath(pathId)
    if (selectedPathId.value === pathId) {
      selectedNode.value = null
      selectedPathId.value = ''
      selectedStepIndex.value = -1
    }
    await loadPaths()
  } catch (e) {
    console.error('删除学习路径失败:', e)
    alert('删除学习路径失败')
  }
}

onMounted(() => {
  loadPaths()
})
</script>

<style lang="scss" scoped>
.learning-path-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  overflow: hidden;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-shrink: 0;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
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

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  min-width: 220px;
  height: 40px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;

  &:hover,
  &:focus-within {
    border-color: #60a5fa;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), 0 0 0 1px #60a5fa;
  }

  .search-icon { width: 15px; height: 15px; color: #94a3b8; flex-shrink: 0; }

  .search-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #e2e8f0;
    font-size: 13px;
    min-width: 0;
    &::placeholder { color: #64748b; }
  }

  .clear-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 2px;
    display: flex;
    color: #94a3b8;
    &:hover { color: #e2e8f0; }
    .clear-icon { width: 12px; height: 12px; }
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

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }

  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

.stats-row {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;

  .stat-num {
    font-size: 18px;
    font-weight: 700;
    &.green { color: var(--success-color); }
    &.blue { color: var(--primary-color); }
    &.purple { color: #c084fc; }
  }

  .stat-label { font-size: 11px; color: var(--text-muted); }
}

.search-hint {
  padding: 8px 16px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--primary-color);
  flex-shrink: 0;
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

@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: var(--text-muted);

  .empty-icon { width: 56px; height: 56px; margin-bottom: 16px; opacity: 0.5; }
  .empty-text { font-size: 16px; margin: 0 0 4px; }
  .empty-hint { font-size: 13px; margin: 0; }
}

.map-container {
  flex: 1;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: auto;
  position: relative;
}

.map-scroll {
  width: 100%;
  min-height: 100%;
  overflow: visible;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.subject-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: auto;
  transition: all 0.25s ease;

  &.active {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 1px var(--primary-color), 0 4px 16px rgba(99, 102, 241, 0.15);
  }
}

.subject-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.subject-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  .subject-icon { width: 22px; height: 22px; color: white; }
}

.subject-info {
  flex: 1;

  .subject-name {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 2px 0;
  }

  .subject-desc {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.subject-progress {
  display: flex;
  align-items: center;
  gap: 10px;

  .progress-bar {
    width: 100px;
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      border-radius: 4px;
      transition: width 0.5s ease;
    }
  }

  .progress-text {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    min-width: 40px;
    text-align: right;
  }
}

.delete-path-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;

  .btn-icon { width: 14px; height: 14px; }

  &:hover {
    border-color: #ef4444;
    color: #f87171;
    background: rgba(239, 68, 68, 0.1);
  }
}

.path-map {
  position: relative;
  width: 100%;
  min-height: 360px;
  padding: 30px 20px 80px 20px;
  overflow: hidden;
}

.path-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.map-node {
  position: absolute;
  width: 52px;
  height: 52px;
  transform: translateX(-50%);
  z-index: 10;
  cursor: pointer;
  transition: transform 0.25s ease;

  &:hover {
    transform: translateX(-50%) scale(1.12);
  }

  &.searched {
    animation: pulse-glow 1.5s ease-in-out infinite;
  }

  .node-ring {
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    border: 2px solid transparent;
    transition: all 0.3s ease;

    &.unlocked {
      border-color: var(--success-color);
      opacity: 0.3;
    }

    &.locked {
      border-color: var(--text-muted);
      opacity: 0.15;
    }
  }

  .node-icon-wrap {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;

    .node-icon { width: 20px; height: 20px; }

    &.unlocked {
      background: linear-gradient(135deg, #10b981, #059669);
      box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);

      .node-icon { color: white; }

      &:hover {
        box-shadow: 0 3px 12px rgba(16, 185, 129, 0.45);
      }
    }

    &.locked {
      background: var(--bg-tertiary);
      border: 2px solid var(--border-color);
      opacity: 0.5;

      .node-icon { color: var(--text-muted); }
    }
  }

  .node-label {
    position: absolute;
    top: 60px;
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
    font-size: 11px;
    font-weight: 500;
    text-align: center;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;

    &.unlocked { color: var(--success-color); }
    &.locked { color: var(--text-muted); opacity: 0.5; }
  }

  .node-index {
    position: absolute;
    top: -4px;
    right: -4px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
    z-index: 2;

    &.unlocked {
      background: var(--success-color);
      color: white;
      box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
    }

    &.locked {
      background: var(--bg-tertiary);
      border: 2px solid var(--border-color);
      color: var(--text-muted);
    }
  }
}

.detail-panel {
  position: fixed;
  right: 24px;
  top: 100px;
  width: 360px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
  z-index: 100;
  max-height: calc(100vh - 140px);
  overflow-y: auto;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  position: relative;

  .panel-title-row {
    display: flex;
    align-items: center;
    gap: 12px;

    .title-icon {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      .icon { width: 22px; height: 22px; color: white; }

      &.locked {
        background: var(--bg-tertiary) !important;
        border: 2px solid var(--border-color);
        .icon { color: var(--text-muted); }
      }
    }

    .panel-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 2px 0;
    }

    .panel-subtitle { font-size: 12px; color: var(--text-muted); }
  }

  .close-btn {
    position: absolute;
    top: 16px;
    right: 16px;
    width: 28px;
    height: 28px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover { background: var(--bg-card); border-color: var(--primary-color); }

    .close-icon { width: 14px; height: 14px; color: var(--text-secondary); }
  }
}

.panel-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  .section-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    margin: 0 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .section-desc {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin: 0;
  }

  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: var(--radius-md);
    font-size: 13px;
    font-weight: 500;

    .badge-icon { width: 14px; height: 14px; }

    &.unlocked { background: rgba(16, 185, 129, 0.1); color: var(--success-color); }
    &.locked { background: var(--bg-tertiary); color: var(--text-muted); }
  }

  .info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 3px;
      padding: 10px;
      background: var(--bg-tertiary);
      border-radius: var(--radius-md);

      .info-icon { width: 14px; height: 14px; color: var(--primary-color); }
      span { font-size: 11px; color: var(--text-muted); }
      strong { font-size: 13px; color: var(--text-primary); }
    }
  }
}

.panel-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);

  .btn-secondary, .btn-primary {
    flex: 1;
    padding: 10px;
    border-radius: var(--radius-md);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
  }

  .btn-secondary {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    &:hover { background: var(--bg-card); }
  }

  .btn-primary {
    background: var(--primary-color);
    color: white;
    &:hover { background: var(--primary-dark); }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
  }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }
  50% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
}

.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; }
.slide-enter-from { opacity: 0; transform: translateX(20px); }
.slide-leave-to { opacity: 0; transform: translateX(20px); }

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
  max-width: 520px;
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

.modal-enter-active,
.modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
</style>

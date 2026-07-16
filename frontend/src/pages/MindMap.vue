<template>
  <div class="mindmap-page">
    <!-- 左侧课程列表 -->
    <div class="course-sidebar">
      <div class="sidebar-header">
        <h3 class="sidebar-title">我的课程</h3>
        <span class="course-count">{{ filteredCourses.length }} 门课程</span>
      </div>
      <div class="subject-filter">
        <label>选择课程</label>
        <select v-model="selectedSubject">
          <option value="">全部课程</option>
          <option value="ai-intro">人工智能导论</option>
        </select>
      </div>
      <div class="course-list">
        <div
          v-for="course in filteredCourses"
          :key="course.id"
          class="course-item"
          :class="{ active: selectedCourse?.id === course.id }"
          @click="selectCourse(course)"
        >
          <div class="course-icon" :style="{ background: course.color }">
            <component :is="course.icon" class="icon" />
          </div>
          <div class="course-info">
            <div class="course-name">{{ course.name }}</div>
            <div class="course-meta">
              <span>{{ course.chapterCount }} 章节</span>
              <span class="progress-text">{{ course.progress }}%</span>
            </div>
          </div>
          <div class="course-progress-bar">
            <div class="progress-fill" :style="{ width: course.progress + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧主区域 -->
    <div class="mindmap-main">
      <!-- 未选课程 -->
      <div class="empty-state" v-if="!selectedCourse">
        <component :is="icons.BookOpen" class="empty-icon" />
        <h3 class="empty-title">请选择一门课程</h3>
        <p class="empty-desc">从左侧列表选择课程查看知识点思维导图</p>
      </div>

      <!-- 已选课程，未选章节 → 显示章节列表 -->
      <div v-else-if="!selectedChapter" class="chapter-view">
        <div class="toolbar">
          <div class="course-title">
            <div class="title-icon" :style="{ background: selectedCourse.color }">
              <component :is="selectedCourse.icon" class="icon" />
            </div>
            <div>
              <h2 class="title-text">{{ selectedCourse.name }}</h2>
              <span class="title-desc">{{ selectedCourse.description }}</span>
            </div>
          </div>
        </div>
        <div class="chapter-grid">
          <div
            v-for="chapter in selectedCourse.chapters"
            :key="chapter.id"
            class="chapter-card"
            @click="selectChapter(chapter)"
          >
            <div class="chapter-card-header">
              <span class="chapter-badge">第{{ chapter.index }}章</span>
              <h3 class="chapter-card-title">{{ chapter.title }}</h3>
            </div>
            <div class="chapter-card-footer">
              <span class="chapter-topic-count">{{ chapter.topics.length }} 个知识点</span>
              <div class="chapter-progress-mini">
                <div class="progress-fill" :style="{ width: chapter.progress + '%' }"></div>
              </div>
              <span class="chapter-progress-text">{{ chapter.progress }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 已选章节 → 显示散点思维导图 -->
      <div v-else class="scatter-view">
        <!-- 顶部工具栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <button class="back-btn" @click="selectedChapter = null">
              <component :is="icons.ChevronRight" class="back-icon" />
              <span>返回章节</span>
            </button>
            <div class="chapter-title-bar">
              <div class="title-icon" :style="{ background: selectedCourse.color }">
                <component :is="selectedCourse.icon" class="icon" />
              </div>
              <div>
                <h2 class="title-text">{{ selectedChapter.title }}</h2>
                <span class="title-desc">{{ selectedCourse.name }} · 第{{ selectedChapter.index }}章</span>
              </div>
            </div>
          </div>
          <div class="toolbar-right">
            <div class="search-box">
              <component :is="icons.Search" class="search-icon" />
              <input
                type="text"
                v-model="searchQuery"
                placeholder="搜索知识点..."
                class="search-input"
              />
              <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''">
                <component :is="icons.X" class="clear-icon" />
              </button>
            </div>
          </div>
        </div>

        <!-- 搜索结果提示 -->
        <div v-if="searchQuery && matchedNodes.length > 0" class="search-hint">
          找到 {{ matchedNodes.length }} 个匹配知识点
        </div>

        <!-- 散点思维导图画布 -->
        <div class="canvas-container" ref="canvasContainer" @wheel.prevent="onWheel" @mousedown="onCanvasMouseDown">
          <div
            class="canvas-inner"
            :style="{
              transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
              transformOrigin: '0 0'
            }"
          >
            <!-- SVG 连线层 -->
            <svg class="connections-layer">
              <line
                v-for="conn in connections"
                :key="conn.id"
                :x1="conn.x1"
                :y1="conn.y1"
                :x2="conn.x2"
                :y2="conn.y2"
                :stroke="conn.color"
                :stroke-width="conn.width"
                :stroke-dasharray="conn.dashed ? '6,4' : 'none'"
                opacity="0.6"
              />
            </svg>

            <!-- 节点 -->
            <div
              v-for="node in allNodes"
              :key="node.id"
              class="mind-node"
              :class="[
                node.level,
                { highlighted: isNodeMatched(node), dimmed: searchQuery && !isNodeMatched(node) }
              ]"
              :style="{
                left: node.x + 'px',
                top: node.y + 'px',
                borderColor: node.level === 'root' ? selectedCourse.color : getNodeColor(node)
              }"
              @click.stop="onNodeClick(node)"
            >
              <div class="node-dot" :style="{ background: node.level === 'root' ? selectedCourse.color : getNodeColor(node) }"></div>
              <span class="node-label">{{ node.title }}</span>
              <span v-if="node.level !== 'root'" class="node-status-dot" :class="node.status"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识点详情面板 -->
    <Transition name="slide">
      <div class="detail-panel" v-if="selectedTopic">
        <div class="panel-header">
          <div class="panel-title-row">
            <div class="title-icon" :style="{ background: selectedCourse?.color }">
              <component :is="selectedCourse?.icon" class="icon" />
            </div>
            <div>
              <h3 class="panel-title">{{ selectedTopic.title }}</h3>
              <span class="panel-subtitle">{{ selectedCourse?.name }} · 第{{ selectedChapter?.index }}章</span>
            </div>
          </div>
          <button class="close-btn" @click="selectedTopic = null">
            <component :is="icons.X" class="close-icon" />
          </button>
        </div>
        <div class="panel-content">
          <div class="info-section">
            <h4 class="section-title">知识点概述</h4>
            <p class="section-desc">{{ selectedTopic.description || '暂无描述' }}</p>
          </div>
          <div class="info-section">
            <h4 class="section-title">学习状态</h4>
            <div class="status-badge" :class="selectedTopic.status">
              <component :is="getStatusIcon(selectedTopic.status)" class="badge-icon" />
              <span>{{ getStatusText(selectedTopic.status) }}</span>
            </div>
          </div>
          <div class="info-section" v-if="selectedTopic.duration || selectedTopic.difficulty">
            <h4 class="section-title">学习信息</h4>
            <div class="info-grid">
              <div v-if="selectedTopic.duration" class="info-item">
                <component :is="icons.Clock" class="info-icon" />
                <span>预计时长</span>
                <strong>{{ selectedTopic.duration }}</strong>
              </div>
              <div v-if="selectedTopic.difficulty" class="info-item">
                <component :is="icons.Target" class="info-icon" />
                <span>难度等级</span>
                <strong>{{ getDifficultyText(selectedTopic.difficulty) }}</strong>
              </div>
            </div>
          </div>
          <div class="info-section" v-if="selectedTopic.subtopics && selectedTopic.subtopics.length > 0">
            <h4 class="section-title">子知识点 ({{ selectedTopic.subtopics.length }})</h4>
            <div class="subtopic-list">
              <div
                v-for="sub in selectedTopic.subtopics"
                :key="sub.id"
                class="subtopic-row"
              >
                <component :is="getStatusIcon(sub.status)" class="sub-icon" :class="sub.status" />
                <span class="sub-name">{{ sub.title }}</span>
              </div>
            </div>
          </div>
          <div class="panel-actions">
            <button class="btn-secondary" @click="selectedTopic = null">关闭</button>
            <button class="btn-primary">
              {{ selectedTopic.status === 'completed' ? '重新学习' : '开始学习' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  Search, X, ChevronRight, ChevronDown,
  BookOpen, Code, Calculator, FlaskConical, Globe,
  CheckCircle, Clock, AlertCircle, Target,
  Lightbulb, Cpu, Shield, Aperture
} from 'lucide-vue-next'

const icons = {
  Search, X, ChevronRight, ChevronDown,
  BookOpen, Code, Calculator, FlaskConical, Globe,
  CheckCircle, Clock, AlertCircle, Target,
  Lightbulb, Cpu, Shield, Aperture
}

// ===== 状态 =====
const searchQuery = ref('')
const selectedSubject = ref('')
const selectedCourse = ref<any>(null)
const selectedChapter = ref<any>(null)
const selectedTopic = ref<any>(null)
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const canvasContainer = ref<HTMLElement | null>(null)
let isPanning = false
let panStartX = 0
let panStartY = 0

// ===== 数据 =====
interface Topic {
  id: string
  title: string
  status: 'completed' | 'in-progress' | 'not-started'
  description?: string
  duration?: string
  difficulty?: 'easy' | 'medium' | 'hard'
  subtopics?: Topic[]
}

interface Chapter {
  id: string
  index: number
  title: string
  progress: number
  topics: Topic[]
}

interface Course {
  id: string
  name: string
  description: string
  icon: any
  color: string
  chapterCount: number
  progress: number
  chapters: Chapter[]
}

const courses: Course[] = [
  {
    id: 'ai-intro',
    name: '人工智能导论',
    description: '人工智能概述、搜索推理、机器学习、深度学习、NLP、CV与AI伦理',
    icon: Lightbulb,
    color: '#6366f1',
    chapterCount: 7,
    progress: 52,
    chapters: [
      {
        id: 'ai-ch1', index: 1, title: '人工智能概述', progress: 80,
        topics: [
          { id: 'ai-1-1', title: '人工智能定义', status: 'completed', description: '理解人工智能的基本概念与核心目标', duration: '45分钟', difficulty: 'easy',
            subtopics: [{ id: 'ai-1-1-1', title: '强人工智能', status: 'completed' }, { id: 'ai-1-1-2', title: '弱人工智能', status: 'completed' }, { id: 'ai-1-1-3', title: '智能体', status: 'completed' }] },
          { id: 'ai-1-2', title: '发展历程', status: 'completed', description: '从图灵测试到现代AI的发展脉络', duration: '60分钟', difficulty: 'medium',
            subtopics: [{ id: 'ai-1-2-1', title: '图灵测试', status: 'completed' }, { id: 'ai-1-2-2', title: '两次AI寒冬', status: 'completed' }] },
          { id: 'ai-1-3', title: '主要流派', status: 'in-progress', description: '符号主义、连接主义与行为主义', duration: '60分钟', difficulty: 'medium',
            subtopics: [{ id: 'ai-1-3-1', title: '符号主义', status: 'completed' }, { id: 'ai-1-3-2', title: '连接主义', status: 'in-progress' }, { id: 'ai-1-3-3', title: '行为主义', status: 'not-started' }] },
          { id: 'ai-1-4', title: '应用领域', status: 'not-started', description: 'AI在医疗、金融、交通等领域的典型应用', duration: '90分钟', difficulty: 'easy',
            subtopics: [{ id: 'ai-1-4-1', title: '医疗AI', status: 'not-started' }, { id: 'ai-1-4-2', title: '自动驾驶', status: 'not-started' }] }
        ]
      },
      {
        id: 'ai-ch2', index: 2, title: '搜索与推理', progress: 60,
        topics: [
          { id: 'ai-2-1', title: '问题求解', status: 'completed', description: '状态空间、搜索树与问题归约', duration: '60分钟', difficulty: 'medium' },
          { id: 'ai-2-2', title: '盲目搜索', status: 'completed', description: '深度优先、广度优先与一致代价搜索', duration: '90分钟', difficulty: 'medium' },
          { id: 'ai-2-3', title: '启发式搜索', status: 'in-progress', description: 'A*算法与启发函数设计', duration: '120分钟', difficulty: 'hard',
            subtopics: [{ id: 'ai-2-3-1', title: 'A*算法', status: 'in-progress' }, { id: 'ai-2-3-2', title: '可采纳性', status: 'not-started' }] },
          { id: 'ai-2-4', title: '知识表示', status: 'not-started', description: '谓词逻辑、语义网络与知识图谱', duration: '90分钟', difficulty: 'hard' },
          { id: 'ai-2-5', title: '推理方法', status: 'not-started', description: '演绎推理、归纳推理与不确定性推理', duration: '120分钟', difficulty: 'hard' }
        ]
      },
      {
        id: 'ai-ch3', index: 3, title: '机器学习', progress: 60,
        topics: [
          { id: 'ai-3-1', title: '机器学习概述', status: 'completed', description: '学习范式、数据集与模型评估', duration: '60分钟', difficulty: 'easy' },
          { id: 'ai-3-2', title: '监督学习', status: 'completed', description: '分类与回归：KNN、决策树与线性回归', duration: '120分钟', difficulty: 'medium',
            subtopics: [{ id: 'ai-3-2-1', title: 'KNN', status: 'completed' }, { id: 'ai-3-2-2', title: '决策树', status: 'completed' }, { id: 'ai-3-2-3', title: '线性回归', status: 'in-progress' }] },
          { id: 'ai-3-3', title: '无监督学习', status: 'in-progress', description: '聚类与降维：K-Means与PCA', duration: '90分钟', difficulty: 'medium' },
          { id: 'ai-3-4', title: '强化学习', status: 'not-started', description: '智能体、奖励与策略梯度基础', duration: '120分钟', difficulty: 'hard' },
          { id: 'ai-3-5', title: '模型评估', status: 'not-started', description: '交叉验证、过拟合与正则化', duration: '90分钟', difficulty: 'medium' }
        ]
      },
      {
        id: 'ai-ch4', index: 4, title: '深度学习', progress: 50,
        topics: [
          { id: 'ai-4-1', title: '神经网络基础', status: 'completed', description: '感知机、多层网络与反向传播', duration: '120分钟', difficulty: 'medium',
            subtopics: [{ id: 'ai-4-1-1', title: '感知机', status: 'completed' }, { id: 'ai-4-1-2', title: '反向传播', status: 'completed' }] },
          { id: 'ai-4-2', title: '卷积神经网络', status: 'in-progress', description: '卷积、池化与CNN典型结构', duration: '120分钟', difficulty: 'hard' },
          { id: 'ai-4-3', title: '循环神经网络', status: 'not-started', description: 'RNN、LSTM与序列建模', duration: '120分钟', difficulty: 'hard' },
          { id: 'ai-4-4', title: '优化与正则化', status: 'not-started', description: '梯度下降、Dropout与批归一化', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      {
        id: 'ai-ch5', index: 5, title: '自然语言处理', progress: 50,
        topics: [
          { id: 'ai-5-1', title: '文本分析基础', status: 'completed', description: '分词、词性标注与命名实体识别', duration: '60分钟', difficulty: 'medium' },
          { id: 'ai-5-2', title: '语言模型', status: 'in-progress', description: 'n-gram、词向量与Transformer', duration: '120分钟', difficulty: 'hard',
            subtopics: [{ id: 'ai-5-2-1', title: 'Word2Vec', status: 'completed' }, { id: 'ai-5-2-2', title: 'Transformer', status: 'in-progress' }] },
          { id: 'ai-5-3', title: '机器翻译', status: 'not-started', description: '序列到序列模型与注意力机制', duration: '120分钟', difficulty: 'hard' },
          { id: 'ai-5-4', title: '情感分析', status: 'not-started', description: '文本分类与情感倾向识别', duration: '90分钟', difficulty: 'medium' }
        ]
      },
      {
        id: 'ai-ch6', index: 6, title: '计算机视觉', progress: 50,
        topics: [
          { id: 'ai-6-1', title: '图像识别', status: 'completed', description: '图像分类与特征提取', duration: '90分钟', difficulty: 'medium' },
          { id: 'ai-6-2', title: '目标检测', status: 'in-progress', description: '边界框、IoU与经典检测算法', duration: '120分钟', difficulty: 'hard',
            subtopics: [{ id: 'ai-6-2-1', title: 'IoU', status: 'completed' }, { id: 'ai-6-2-2', title: 'YOLO', status: 'in-progress' }] },
          { id: 'ai-6-3', title: '图像生成', status: 'not-started', description: '生成对抗网络与扩散模型基础', duration: '120分钟', difficulty: 'hard' },
          { id: 'ai-6-4', title: '视觉应用', status: 'not-started', description: '人脸识别、OCR与自动驾驶视觉', duration: '90分钟', difficulty: 'medium' }
        ]
      },
      {
        id: 'ai-ch7', index: 7, title: '人工智能伦理', progress: 50,
        topics: [
          { id: 'ai-7-1', title: '伦理挑战', status: 'completed', description: '算法偏见、公平性与透明度', duration: '60分钟', difficulty: 'medium' },
          { id: 'ai-7-2', title: '隐私问题', status: 'in-progress', description: '数据隐私、联邦学习与差分隐私', duration: '90分钟', difficulty: 'medium' },
          { id: 'ai-7-3', title: '安全风险', status: 'not-started', description: '对抗样本、深度伪造与滥用防范', duration: '120分钟', difficulty: 'hard' },
          { id: 'ai-7-4', title: '未来治理', status: 'not-started', description: 'AI治理框架与 Responsible AI', duration: '90分钟', difficulty: 'medium' }
        ]
      }
    ]
  }
]

const filteredCourses = computed(() => {
  if (!selectedSubject.value) return courses
  return courses.filter(course => course.id === selectedSubject.value)
})

// ===== 散点思维导图计算 ====
interface MindNode {
  id: string
  title: string
  level: 'root' | 'topic' | 'subtopic'
  status?: string
  x: number
  y: number
  parentId?: string
  topic?: Topic
}

interface Connection {
  id: string
  x1: number
  y1: number
  x2: number
  y2: number
  color: string
  width: number
  dashed: boolean
}

const nodePositions = ref<MindNode[]>([])
const connections = ref<Connection[]>([])

function computeMindMap() {
  if (!selectedChapter.value) return

  const topics = selectedChapter.value.topics
  const cx = 500
  const cy = 400

  const nodes: MindNode[] = []
  const conns: Connection[] = []

  // 中心节点
  nodes.push({
    id: 'root',
    title: selectedChapter.value.title,
    level: 'root',
    x: cx,
    y: cy
  })

  const topicCount = topics.length
  const topicRadius = 220

  topics.forEach((topic: Topic, i: number) => {
    const angle = (2 * Math.PI * i) / topicCount - Math.PI / 2
    const tx = cx + Math.cos(angle) * topicRadius
    const ty = cy + Math.sin(angle) * topicRadius

    nodes.push({
      id: topic.id,
      title: topic.title,
      level: 'topic',
      status: topic.status,
      x: tx,
      y: ty,
      parentId: 'root',
      topic
    })

    conns.push({
      id: `conn-root-${topic.id}`,
      x1: cx,
      y1: cy,
      x2: tx,
      y2: ty,
      color: getNodeStatusColor(topic.status),
      width: 2.5,
      dashed: topic.status === 'not-started'
    })

    // 子知识点
    if (topic.subtopics && topic.subtopics.length > 0) {
      const subCount = topic.subtopics.length
      const subRadius = 110
      const baseAngle = angle

      topic.subtopics.forEach((sub: Topic, j: number) => {
        const spreadAngle = Math.PI / 3
        const subAngle = baseAngle + (j - (subCount - 1) / 2) * (spreadAngle / Math.max(subCount - 1, 1))
        const sx = tx + Math.cos(subAngle) * subRadius
        const sy = ty + Math.sin(subAngle) * subRadius

        nodes.push({
          id: sub.id,
          title: sub.title,
          level: 'subtopic',
          status: sub.status,
          x: sx,
          y: sy,
          parentId: topic.id,
          topic: sub
        })

        conns.push({
          id: `conn-${topic.id}-${sub.id}`,
          x1: tx,
          y1: ty,
          x2: sx,
          y2: sy,
          color: getNodeStatusColor(sub.status),
          width: 1.5,
          dashed: sub.status === 'not-started'
        })
      })
    }
  })

  nodePositions.value = nodes
  connections.value = conns

  // 重置视图
  zoom.value = 1
  panX.value = 0
  panY.value = 0
}

function getNodeStatusColor(status?: string): string {
  const map: Record<string, string> = {
    completed: '#10b981',
    'in-progress': '#f59e0b',
    'not-started': '#64748b'
  }
  return map[status || ''] || '#64748b'
}

function getNodeColor(node: MindNode): string {
  if (node.level === 'root') return selectedCourse.value.color
  return getNodeStatusColor(node.status)
}

const allNodes = computed(() => nodePositions.value)

// ===== 搜索 =====
const matchedNodes = computed(() => {
  if (!searchQuery.value) return []
  const q = searchQuery.value.toLowerCase()
  return nodePositions.value.filter(n =>
    n.level !== 'root' && n.title.toLowerCase().includes(q)
  )
})

function isNodeMatched(node: MindNode): boolean {
  if (!searchQuery.value) return false
  const q = searchQuery.value.toLowerCase()
  return node.title.toLowerCase().includes(q)
}

// ===== 画布交互 =====
function onWheel(e: WheelEvent) {
  const delta = e.deltaY > 0 ? -0.05 : 0.05
  zoom.value = Math.max(0.3, Math.min(3, zoom.value + delta))
}

function onCanvasMouseDown(e: MouseEvent) {
  isPanning = true
  panStartX = e.clientX - panX.value
  panStartY = e.clientY - panY.value
  document.addEventListener('mousemove', onCanvasMouseMove)
  document.addEventListener('mouseup', onCanvasMouseUp)
}

function onCanvasMouseMove(e: MouseEvent) {
  if (!isPanning) return
  panX.value = e.clientX - panStartX
  panY.value = e.clientY - panStartY
}

function onCanvasMouseUp() {
  isPanning = false
  document.removeEventListener('mousemove', onCanvasMouseMove)
  document.removeEventListener('mouseup', onCanvasMouseUp)
}

// ===== 方法 =====
function selectCourse(course: Course) {
  selectedCourse.value = course
  selectedChapter.value = null
  selectedTopic.value = null
  searchQuery.value = ''
}

watch(selectedSubject, () => {
  selectedCourse.value = null
  selectedChapter.value = null
  selectedTopic.value = null
})

function selectChapter(chapter: Chapter) {
  selectedChapter.value = chapter
  selectedTopic.value = null
  searchQuery.value = ''
  nextTick(() => {
    computeMindMap()
  })
}

function onNodeClick(node: MindNode) {
  if (node.level === 'root') return
  if (node.topic) {
    selectedTopic.value = node.topic
  }
}

function getStatusIcon(status?: string) {
  const map: Record<string, any> = {
    completed: CheckCircle,
    'in-progress': Clock,
    'not-started': AlertCircle
  }
  return map[status || ''] || AlertCircle
}

function getStatusText(status?: string): string {
  const map: Record<string, string> = {
    completed: '已完成',
    'in-progress': '学习中',
    'not-started': '未开始'
  }
  return map[status || ''] || '未开始'
}

function getDifficultyText(difficulty?: string): string {
  const map: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[difficulty || ''] || '中等'
}
</script>

<style lang="scss" scoped>
.mindmap-page {
  display: flex;
  gap: 16px;
  height: 100%;
  overflow: hidden;
}

// 左侧课程列表
.course-sidebar {
  width: 380px;
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;

  .sidebar-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .course-count {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.subject-filter {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.5), rgba(26, 37, 52, 0.5));

  label {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 500;
    display: block;
    margin-bottom: 8px;
  }

  select {
    width: 100%;
    padding: 10px 14px;
    background: linear-gradient(145deg, #273548, #1e293b);
    border: 2px solid rgba(71, 85, 105, 0.8);
    border-radius: var(--radius-md);
    color: #e2e8f0;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    height: 44px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;

    &:focus {
      outline: none;
      border-color: #6366f1;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), 0 0 0 1px #6366f1;
    }

    &:hover {
      border-color: #60a5fa;
    }

    option {
      background: #1e293b;
      color: #e2e8f0;
      padding: 10px 14px;
    }
  }
}

.course-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.course-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;

  &:hover {
    background: var(--bg-card);
  }

  &.active {
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid var(--primary-color);

    .course-name {
      color: var(--primary-color);
    }
  }

  .course-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .icon {
      width: 20px;
      height: 20px;
      color: white;
    }
  }

  .course-info {
    flex: 1;
    min-width: 0;

    .course-name {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 4px;
    }

    .course-meta {
      display: flex;
      gap: 8px;
      font-size: 11px;
      color: var(--text-muted);

      .progress-text {
        color: var(--primary-color);
        font-weight: 600;
      }
    }
  }

  .course-progress-bar {
    position: absolute;
    bottom: 2px;
    left: 8px;
    right: 8px;
    height: 2px;
    background: var(--bg-tertiary);

    .progress-fill {
      height: 100%;
      background: var(--primary-color);
      transition: width 0.3s ease;
    }
  }
}

// 右侧主区域
.mindmap-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
  overflow: hidden;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  flex-shrink: 0;

  &:hover {
    background: var(--bg-card);
    color: var(--text-primary);
    border-color: var(--primary-color);
  }

  .back-icon {
    width: 14px;
    height: 14px;
    transform: rotate(180deg);
  }
}

.chapter-title-bar {
  display: flex;
  align-items: center;
  gap: 12px;

  .title-icon {
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

  .title-text {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 2px 0;
  }

  .title-desc {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.course-title {
  display: flex;
  align-items: center;
  gap: 12px;

  .title-icon {
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

  .title-text {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 2px 0;
  }

  .title-desc {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  min-width: 200px;

  .search-icon {
    width: 16px;
    height: 16px;
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .search-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--text-primary);
    font-size: 13px;
    min-width: 0;

    &::placeholder {
      color: var(--text-muted);
    }
  }

  .clear-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 2px;
    display: flex;
    align-items: center;
    color: var(--text-muted);

    &:hover {
      color: var(--text-primary);
    }

    .clear-icon {
      width: 14px;
      height: 14px;
    }
  }
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

// 章节列表视图
.chapter-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
  overflow: hidden;
}

.chapter-grid {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  padding: 4px;
  align-content: start;
}

.chapter-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;

  &:hover {
    border-color: var(--primary-color);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  }

  .chapter-card-header {
    display: flex;
    align-items: center;
    gap: 12px;

    .chapter-badge {
      font-size: 12px;
      font-weight: 600;
      color: var(--primary-color);
      background: rgba(99, 102, 241, 0.1);
      padding: 4px 10px;
      border-radius: var(--radius-sm);
      flex-shrink: 0;
    }

    .chapter-card-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
  }

  .chapter-card-footer {
    display: flex;
    align-items: center;
    gap: 12px;

    .chapter-topic-count {
      font-size: 12px;
      color: var(--text-muted);
      flex-shrink: 0;
    }

    .chapter-progress-mini {
      flex: 1;
      height: 6px;
      background: var(--bg-tertiary);
      border-radius: 3px;
      overflow: hidden;

      .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
        border-radius: 3px;
        transition: width 0.3s ease;
      }
    }

    .chapter-progress-text {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      min-width: 36px;
      text-align: right;
    }
  }
}

// 散点思维导图视图
.scatter-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
  overflow: hidden;
}

.canvas-container {
  flex: 1;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: grab;
  position: relative;

  &:active {
    cursor: grabbing;
  }
}

.canvas-inner {
  position: relative;
  width: 1000px;
  height: 800px;
  transition: transform 0.1s ease;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.mind-node {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.25s ease;
  white-space: nowrap;
  transform: translate(-50%, -50%);
  z-index: 1;

  &:hover {
    transform: translate(-50%, -50%) scale(1.08);
    z-index: 10;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  }

  .node-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .node-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .node-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;

    &.completed { background: #10b981; }
    &.in-progress { background: #f59e0b; }
    &.not-started { background: #64748b; }
  }

  &.root {
    padding: 14px 28px;
    border-width: 3px;
    font-size: 16px;
    font-weight: 700;
    background: rgba(99, 102, 241, 0.1);
    animation: rootPulse 2s ease-in-out infinite;

    .node-dot {
      width: 14px;
      height: 14px;
    }

    .node-label {
      font-size: 16px;
      font-weight: 700;
    }
  }

  &.topic {
    .node-label {
      font-size: 13px;
    }
  }

  &.subtopic {
    padding: 6px 12px;
    border-width: 1.5px;

    .node-dot {
      width: 7px;
      height: 7px;
    }

    .node-label {
      font-size: 11px;
      color: var(--text-secondary);
    }
  }

  &.highlighted {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.5);
    animation: nodeGlow 1.5s ease-in-out infinite;
    z-index: 5;
  }

  &.dimmed {
    opacity: 0.3;
  }
}

@keyframes rootPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.3); }
  50% { box-shadow: 0 0 0 8px rgba(99, 102, 241, 0); }
}

@keyframes nodeGlow {
  0%, 100% { box-shadow: 0 0 8px rgba(99, 102, 241, 0.4); }
  50% { box-shadow: 0 0 16px rgba(99, 102, 241, 0.7); }
}

// 空状态
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);

  .empty-icon {
    width: 48px;
    height: 48px;
    color: var(--text-muted);
    opacity: 0.5;
  }

  .empty-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .empty-desc {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0;
  }
}

// 详情面板
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
      width: 40px;
      height: 40px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      .icon {
        width: 20px;
        height: 20px;
        color: white;
      }
    }

    .panel-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 2px 0;
    }

    .panel-subtitle {
      font-size: 12px;
      color: var(--text-muted);
    }
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

    &:hover {
      background: var(--bg-card);
      border-color: var(--primary-color);
    }

    .close-icon {
      width: 14px;
      height: 14px;
      color: var(--text-secondary);
    }
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

    .badge-icon {
      width: 14px;
      height: 14px;
    }

    &.completed {
      background: rgba(16, 185, 129, 0.1);
      color: var(--success-color);
    }

    &.in-progress {
      background: rgba(245, 158, 11, 0.1);
      color: var(--warning-color);
    }

    &.not-started {
      background: var(--bg-tertiary);
      color: var(--text-muted);
    }
  }

  .info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
      padding: 12px;
      background: var(--bg-tertiary);
      border-radius: var(--radius-md);

      .info-icon {
        width: 16px;
        height: 16px;
        color: var(--primary-color);
      }

      span {
        font-size: 11px;
        color: var(--text-muted);
      }

      strong {
        font-size: 14px;
        color: var(--text-primary);
      }
    }
  }

  .subtopic-list {
    display: flex;
    flex-direction: column;
    gap: 6px;

    .subtopic-row {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      background: var(--bg-tertiary);
      border-radius: var(--radius-md);

      .sub-icon {
        width: 14px;
        height: 14px;
        flex-shrink: 0;

        &.completed { color: var(--success-color); }
        &.in-progress { color: var(--warning-color); }
        &.not-started { color: var(--text-muted); }
      }

      .sub-name {
        font-size: 13px;
        color: var(--text-primary);
      }
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

    &:hover {
      background: var(--bg-card);
    }
  }

  .btn-primary {
    background: var(--primary-color);
    color: white;

    &:hover {
      background: var(--primary-dark);
    }
  }
}

// Transitions
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>

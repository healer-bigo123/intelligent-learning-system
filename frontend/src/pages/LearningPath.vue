<template>
  <div class="learning-path-page">
    <!-- 顶部筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <select v-model="activeSubject" class="filter-select">
          <option value="all">全部学科</option>
          <option v-for="s in availableSubjects" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
        <div class="grade-select-wrapper">
          <component :is="icons.GraduationCap" class="select-icon" />
          <select v-model="activeGrade" class="grade-select">
            <option value="all">全部年级</option>
            <option value="grade10">高一</option>
            <option value="grade11">高二</option>
            <option value="grade12">高三</option>
          </select>
        </div>
      </div>
      <div class="filter-right">
        <div class="search-box">
          <component :is="icons.Search" class="search-icon" />
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索知识点..."
            class="search-input"
            @input="onSearch"
          />
          <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''; onSearch()">
            <component :is="icons.X" class="clear-icon" />
          </button>
        </div>
        <div class="stats-row">
          <div class="stat-item">
            <span class="stat-num green">{{ stats.unlocked }}</span>
            <span class="stat-label">已解锁</span>
          </div>
          <div class="stat-item">
            <span class="stat-num gray">{{ stats.locked }}</span>
            <span class="stat-label">未解锁</span>
          </div>
          <div class="stat-item">
            <span class="stat-num blue">{{ stats.total }}</span>
            <span class="stat-label">总知识点</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索结果提示 -->
    <div v-if="searchQuery && searchResults.length > 0" class="search-hint">
      找到 {{ searchResults.length }} 个匹配知识点
    </div>

    <!-- 地图区域 -->
    <div class="map-container">
      <div class="map-scroll">
        <!-- 返回全部学科按钮 -->
        <button v-if="activeSubject !== 'all'" class="back-to-all-btn" @click="onSubjectChange('all')">
          <component :is="icons.ChevronLeft" class="back-icon" />
          <span>返回全部学科</span>
        </button>

        <!-- 按学科分组渲染 -->
        <div
          v-for="subject in visibleSubjects"
          :key="subject.id"
          class="subject-section"
          :class="{ clickable: activeSubject === 'all', active: activeSubject === subject.id }"
          @click="activeSubject === 'all' && onSubjectChange(subject.id)"
        >
          <!-- 学科标题 -->
          <div class="subject-header">
            <div class="subject-icon-wrap" :style="{ background: subject.color }">
              <component :is="subject.icon" class="subject-icon" />
            </div>
            <div class="subject-info">
              <h3 class="subject-name">{{ subject.name }}</h3>
              <span class="subject-desc">{{ subject.courseName }}</span>
            </div>
            <div class="subject-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: subject.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ subject.progress }}%</span>
            </div>
          </div>

          <!-- 路径地图 -->
          <div class="path-map" :style="{ minHeight: subject.mapHeight + 'px' }">
            <svg class="path-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
              <defs>
                <linearGradient :id="`pathGrad-${subject.id}`" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" :stop-color="subject.color" stop-opacity="0.8" />
                  <stop offset="100%" :stop-color="subject.color" stop-opacity="0.3" />
                </linearGradient>
                <filter :id="`glow-${subject.id}`">
                  <feGaussianBlur stdDeviation="4" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>
              <!-- 背景路径 -->
              <path
                :d="getPathD(subject.nodes)"
                fill="none"
                stroke="var(--border-color)"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                opacity="0.2"
              />
              <!-- 已解锁路径 -->
              <path
                :d="getPathD(subject.nodes)"
                fill="none"
                :stroke="`url(#pathGrad-${subject.id})`"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                :stroke-dasharray="subject.pathLength"
                :stroke-dashoffset="subject.pathOffset"
                style="transition: stroke-dashoffset 0.8s ease"
              />
              <!-- 虚线装饰 -->
              <path
                :d="getPathD(subject.nodes)"
                fill="none"
                stroke="white"
                stroke-width="0.1"
                stroke-dasharray="0.5 0.4"
                stroke-linecap="round"
                opacity="0.5"
              />
            </svg>

            <!-- 知识点节点 -->
            <div
              v-for="(node, index) in subject.nodes"
              :key="node.id"
              class="map-node"
              :class="[
                node.status,
                { searched: isNodeSearched(node) }
              ]"
              :style="{ left: node.x + '%', top: node.y + '%' }"
              @click="selectNode(node)"
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

    <!-- 知识点详情面板 -->
    <Transition name="slide">
      <div class="detail-panel" v-if="selectedNode">
        <div class="panel-header">
          <div class="panel-title-row">
            <div class="title-icon" :class="selectedNode.status" :style="{ background: getSubjectColor(selectedNode.subject) }">
              <component v-if="selectedNode.status === 'unlocked'" :is="selectedNode.icon" class="icon" />
              <component v-else :is="icons.Lock" class="icon" />
            </div>
            <div>
              <h3 class="panel-title">{{ selectedNode.title }}</h3>
              <span class="panel-subtitle">{{ selectedNode.courseName }} · {{ selectedNode.chapter }}</span>
            </div>
          </div>
          <button class="close-btn" @click="selectedNode = null">
            <component :is="icons.X" class="close-icon" />
          </button>
        </div>
        <div class="panel-content">
          <div class="info-section">
            <h4 class="section-title">知识点概述</h4>
            <p class="section-desc">{{ selectedNode.description || '暂无描述' }}</p>
          </div>
          <div class="info-section">
            <h4 class="section-title">学习状态</h4>
            <div class="status-badge" :class="selectedNode.status">
              <component v-if="selectedNode.status === 'unlocked'" :is="icons.Unlock" class="badge-icon" />
              <component v-else :is="icons.Lock" class="badge-icon" />
              <span>{{ selectedNode.status === 'unlocked' ? '已解锁' : '未解锁' }}</span>
            </div>
          </div>
          <div class="info-section">
            <h4 class="section-title">学习信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <component :is="icons.BookOpen" class="info-icon" />
                <span>所属课程</span>
                <strong>{{ selectedNode.courseName }}</strong>
              </div>
              <div class="info-item">
                <component :is="icons.FolderOpen" class="info-icon" />
                <span>所属章节</span>
                <strong>{{ selectedNode.chapter }}</strong>
              </div>
              <div class="info-item">
                <component :is="icons.Clock" class="info-icon" />
                <span>预计时长</span>
                <strong>{{ selectedNode.duration }}</strong>
              </div>
              <div class="info-item">
                <component :is="icons.Target" class="info-icon" />
                <span>难度</span>
                <strong>{{ getDifficultyText(selectedNode.difficulty) }}</strong>
              </div>
            </div>
          </div>
          <div class="panel-actions">
            <button class="btn-secondary" @click="selectedNode = null">关闭</button>
            <button
              v-if="selectedNode.status === 'locked'"
              class="btn-primary"
              disabled
            >
              未解锁
            </button>
            <button
              v-else
              class="btn-primary"
            >
              开始学习
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Search, X, BookOpen, Clock, Lock, Unlock,
  Calculator, FlaskConical, Code, Globe, GraduationCap,
  FolderOpen, Target, ChevronLeft,
  Lightbulb, Cpu, Shield, Aperture
} from 'lucide-vue-next'

const icons = {
  Search, X, BookOpen, Clock, Lock, Unlock,
  Calculator, FlaskConical, Code, Globe, GraduationCap,
  FolderOpen, Target, ChevronLeft,
  Lightbulb, Cpu, Shield, Aperture
}

// ===== 状态 =====
const activeSubject = ref('all')
const activeGrade = ref('all')
const activeCourse = ref('all')
const searchQuery = ref('')
const selectedNode = ref<any>(null)
const searchResults = ref<any[]>([])

// 全部章节列表（人工智能导论）
const allSubjectList = [
  { id: 'overview', name: '人工智能概述' },
  { id: 'search', name: '搜索与推理' },
  { id: 'ml', name: '机器学习' },
  { id: 'dl', name: '深度学习' },
  { id: 'nlp', name: '自然语言处理' },
  { id: 'cv', name: '计算机视觉' },
  { id: 'ethics', name: '人工智能伦理' }
]

function onSubjectChange(val: string) {
  activeSubject.value = val
}

// ===== 数据 =====
interface PathNode {
  id: string
  title: string
  description: string
  icon: any
  status: 'unlocked' | 'locked'
  subject: string
  grade: string
  courseId: string
  courseName: string
  chapter: string
  duration: string
  difficulty: 'easy' | 'medium' | 'hard'
  x: number
  y: number
}

interface SubjectInfo {
  id: string
  name: string
  icon: any
  color: string
  courseName: string
  nodes: PathNode[]
  progress: number
  pathLength: number
  pathOffset: number
  mapHeight: number
}

// 生成蜿蜒路径坐标（百分比）
function generateSnakePath(count: number): { x: number; y: number }[] {
  const positions: { x: number; y: number }[] = []
  const cols = 5
  // 列宽：5列均分100%，每列20%
  const colWidth = 20
  // 行高：固定16%
  const rowHeight = 16
  // 起始X：第一列中心在10%处
  const startX = 10
  // 起始Y：从8%开始
  const startY = 8

  for (let i = 0; i < count; i++) {
    const col = i % cols
    const row = Math.floor(i / cols)
    // 蛇形：偶数行从左到右，奇数行从右到左
    const actualCol = row % 2 === 0 ? col : (cols - 1 - col)
    positions.push({
      x: startX + actualCol * colWidth,
      y: startY + row * rowHeight
    })
  }
  return positions
}

const allNodes: Omit<PathNode, 'x' | 'y'>[] = [
  // 人工智能概述
  { id: 'ai-o1', title: '人工智能定义', description: '理解人工智能的基本概念与核心目标', icon: BookOpen, status: 'unlocked', subject: 'overview', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第一章 人工智能概述', duration: '45分钟', difficulty: 'easy' },
  { id: 'ai-o2', title: '发展历程', description: '从图灵测试到现代AI的发展脉络', icon: BookOpen, status: 'unlocked', subject: 'overview', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第一章 人工智能概述', duration: '60分钟', difficulty: 'medium' },
  { id: 'ai-o3', title: '主要流派', description: '符号主义、连接主义与行为主义', icon: BookOpen, status: 'unlocked', subject: 'overview', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第一章 人工智能概述', duration: '60分钟', difficulty: 'medium' },
  { id: 'ai-o4', title: '应用领域', description: 'AI在医疗、金融、交通等领域的典型应用', icon: BookOpen, status: 'unlocked', subject: 'overview', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第一章 人工智能概述', duration: '90分钟', difficulty: 'easy' },
  { id: 'ai-o5', title: '智能体模型', description: '感知、决策与行动的智能体框架', icon: Lightbulb, status: 'locked', subject: 'overview', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第一章 人工智能概述', duration: '90分钟', difficulty: 'medium' },
  // 搜索与推理
  { id: 'ai-s1', title: '问题求解', description: '状态空间、搜索树与问题归约', icon: Search, status: 'unlocked', subject: 'search', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第二章 搜索与推理', duration: '60分钟', difficulty: 'medium' },
  { id: 'ai-s2', title: '盲目搜索', description: '深度优先、广度优先与一致代价搜索', icon: Search, status: 'unlocked', subject: 'search', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第二章 搜索与推理', duration: '90分钟', difficulty: 'medium' },
  { id: 'ai-s3', title: '启发式搜索', description: 'A*算法与启发函数设计', icon: Search, status: 'unlocked', subject: 'search', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第二章 搜索与推理', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-s4', title: '知识表示', description: '谓词逻辑、语义网络与知识图谱', icon: Search, status: 'locked', subject: 'search', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第二章 搜索与推理', duration: '90分钟', difficulty: 'hard' },
  { id: 'ai-s5', title: '推理方法', description: '演绎推理、归纳推理与不确定性推理', icon: Search, status: 'locked', subject: 'search', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第二章 搜索与推理', duration: '120分钟', difficulty: 'hard' },
  // 机器学习
  { id: 'ai-ml1', title: '机器学习概述', description: '学习范式、数据集与模型评估', icon: Code, status: 'unlocked', subject: 'ml', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第三章 机器学习', duration: '60分钟', difficulty: 'easy' },
  { id: 'ai-ml2', title: '监督学习', description: '分类与回归：KNN、决策树与线性回归', icon: Code, status: 'unlocked', subject: 'ml', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第三章 机器学习', duration: '120分钟', difficulty: 'medium' },
  { id: 'ai-ml3', title: '无监督学习', description: '聚类与降维：K-Means与PCA', icon: Code, status: 'unlocked', subject: 'ml', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第三章 机器学习', duration: '90分钟', difficulty: 'medium' },
  { id: 'ai-ml4', title: '强化学习', description: '智能体、奖励与策略梯度基础', icon: Code, status: 'locked', subject: 'ml', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第三章 机器学习', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-ml5', title: '模型评估', description: '交叉验证、过拟合与正则化', icon: Code, status: 'locked', subject: 'ml', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第三章 机器学习', duration: '90分钟', difficulty: 'medium' },
  // 深度学习
  { id: 'ai-dl1', title: '神经网络基础', description: '感知机、多层网络与反向传播', icon: Cpu, status: 'unlocked', subject: 'dl', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第四章 深度学习', duration: '120分钟', difficulty: 'medium' },
  { id: 'ai-dl2', title: '卷积神经网络', description: '卷积、池化与CNN典型结构', icon: Cpu, status: 'unlocked', subject: 'dl', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第四章 深度学习', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-dl3', title: '循环神经网络', description: 'RNN、LSTM与序列建模', icon: Cpu, status: 'locked', subject: 'dl', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第四章 深度学习', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-dl4', title: '优化与正则化', description: '梯度下降、Dropout与批归一化', icon: Cpu, status: 'locked', subject: 'dl', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第四章 深度学习', duration: '90分钟', difficulty: 'hard' },
  // 自然语言处理
  { id: 'ai-nlp1', title: '文本分析基础', description: '分词、词性标注与命名实体识别', icon: Globe, status: 'unlocked', subject: 'nlp', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第五章 自然语言处理', duration: '60分钟', difficulty: 'medium' },
  { id: 'ai-nlp2', title: '语言模型', description: 'n-gram、词向量与Transformer', icon: Globe, status: 'unlocked', subject: 'nlp', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第五章 自然语言处理', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-nlp3', title: '机器翻译', description: '序列到序列模型与注意力机制', icon: Globe, status: 'locked', subject: 'nlp', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第五章 自然语言处理', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-nlp4', title: '情感分析', description: '文本分类与情感倾向识别', icon: Globe, status: 'locked', subject: 'nlp', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第五章 自然语言处理', duration: '90分钟', difficulty: 'medium' },
  // 计算机视觉
  { id: 'ai-cv1', title: '图像识别', description: '图像分类与特征提取', icon: Aperture, status: 'unlocked', subject: 'cv', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第六章 计算机视觉', duration: '90分钟', difficulty: 'medium' },
  { id: 'ai-cv2', title: '目标检测', description: '边界框、IoU与经典检测算法', icon: Aperture, status: 'unlocked', subject: 'cv', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第六章 计算机视觉', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-cv3', title: '图像生成', description: '生成对抗网络与扩散模型基础', icon: Aperture, status: 'locked', subject: 'cv', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第六章 计算机视觉', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-cv4', title: '视觉应用', description: '人脸识别、OCR与自动驾驶视觉', icon: Aperture, status: 'locked', subject: 'cv', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第六章 计算机视觉', duration: '90分钟', difficulty: 'medium' },
  // 人工智能伦理
  { id: 'ai-e1', title: '伦理挑战', description: '算法偏见、公平性与透明度', icon: Shield, status: 'unlocked', subject: 'ethics', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第七章 人工智能伦理', duration: '60分钟', difficulty: 'medium' },
  { id: 'ai-e2', title: '隐私问题', description: '数据隐私、联邦学习与差分隐私', icon: Shield, status: 'unlocked', subject: 'ethics', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第七章 人工智能伦理', duration: '90分钟', difficulty: 'medium' },
  { id: 'ai-e3', title: '安全风险', description: '对抗样本、深度伪造与滥用防范', icon: Shield, status: 'locked', subject: 'ethics', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第七章 人工智能伦理', duration: '120分钟', difficulty: 'hard' },
  { id: 'ai-e4', title: '未来治理', description: 'AI治理框架与 Responsible AI', icon: Shield, status: 'locked', subject: 'ethics', grade: 'grade10', courseId: 'ai-intro', courseName: '人工智能导论', chapter: '第七章 人工智能伦理', duration: '90分钟', difficulty: 'medium' }
]



// 构建学科分组
const subjectGroups = computed(() => {
  const groups: Record<string, Omit<PathNode, 'x' | 'y'>[]> = {}
  allNodes.forEach(n => {
    if (!groups[n.subject]) groups[n.subject] = []
    groups[n.subject].push(n)
  })
  return groups
})

const subjectMeta: Record<string, { name: string; icon: any; color: string; courseName: string }> = {
  overview: { name: '人工智能概述', icon: BookOpen, color: '#3b82f6', courseName: '人工智能导论' },
  search: { name: '搜索与推理', icon: Search, color: '#f59e0b', courseName: '人工智能导论' },
  ml: { name: '机器学习', icon: Code, color: '#10b981', courseName: '人工智能导论' },
  dl: { name: '深度学习', icon: Cpu, color: '#ef4444', courseName: '人工智能导论' },
  nlp: { name: '自然语言处理', icon: Globe, color: '#8b5cf6', courseName: '人工智能导论' },
  cv: { name: '计算机视觉', icon: Aperture, color: '#06b6d4', courseName: '人工智能导论' },
  ethics: { name: '人工智能伦理', icon: Shield, color: '#ec4899', courseName: '人工智能导论' }
}

// 有数据的学科列表（用于下拉框）
const availableSubjects = computed(() => {
  return allSubjectList.filter(s => subjectGroups.value[s.id])
})

const visibleSubjects = computed<SubjectInfo[]>(() => {
  const result: SubjectInfo[] = []

  for (const [subjectId, nodes] of Object.entries(subjectGroups.value)) {
    // 学科筛选
    if (activeSubject.value !== 'all' && subjectId !== activeSubject.value) continue

    // 筛选
    let filtered = nodes
    if (activeGrade.value !== 'all') {
      filtered = filtered.filter(n => n.grade === activeGrade.value)
    }
    if (activeCourse.value !== 'all') {
      filtered = filtered.filter(n => n.courseId === activeCourse.value)
    }
    if (filtered.length === 0) continue

    // 生成坐标（百分比）
    const positions = generateSnakePath(filtered.length)
    const nodesWithPos: PathNode[] = filtered.map((n, i) => ({ ...n, x: positions[i].x, y: positions[i].y }))

    const unlocked = nodesWithPos.filter(n => n.status === 'unlocked').length
    const progress = Math.round((unlocked / nodesWithPos.length) * 100)
    const pathLength = 2000
    const pathOffset = pathLength * (1 - unlocked / nodesWithPos.length)
    const mapHeight = Math.max(500, Math.ceil(nodesWithPos.length / 5) * 200 + 200)

    const meta = subjectMeta[subjectId]
    result.push({
      id: subjectId,
      name: meta.name,
      icon: meta.icon,
      color: meta.color,
      courseName: meta.courseName,
      nodes: nodesWithPos,
      progress,
      pathLength,
      pathOffset,
      mapHeight
    })
  }

  return result
})

const stats = computed(() => {
  let total = 0, unlocked = 0, locked = 0
  visibleSubjects.value.forEach(s => {
    total += s.nodes.length
    unlocked += s.nodes.filter(n => n.status === 'unlocked').length
    locked += s.nodes.filter(n => n.status === 'locked').length
  })
  return { total, unlocked, locked }
})

// 生成 SVG 路径（使用百分比坐标）
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

// 搜索
function onSearch() {
  if (!searchQuery.value) {
    searchResults.value = []
    return
  }
  const q = searchQuery.value.toLowerCase()
  searchResults.value = visibleSubjects.value.flatMap(s =>
    s.nodes.filter(n =>
      n.title.toLowerCase().includes(q) ||
      n.description.toLowerCase().includes(q) ||
      n.chapter.toLowerCase().includes(q)
    )
  )
}

function isNodeSearched(node: PathNode): boolean {
  if (!searchQuery.value) return false
  const q = searchQuery.value.toLowerCase()
  return node.title.toLowerCase().includes(q) || node.description.toLowerCase().includes(q)
}

function selectNode(node: PathNode) {
  if (node.status === 'locked') return
  selectedNode.value = node
}

function getSubjectColor(subject: string): string {
  return subjectMeta[subject]?.color || '#6366f1'
}

function getDifficultyText(difficulty: string): string {
  const map: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
  return map[difficulty] || '中等'
}
</script>

<style lang="scss" scoped>
.learning-path-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
  overflow: hidden;
}

// 筛选栏
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-shrink: 0;
  margin-bottom: 20px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
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

.grade-select-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-md);
  padding: 0 12px;
  height: 40px;
  min-width: 120px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;

  &:hover,
  &:focus-within {
    border-color: #60a5fa;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15), 0 0 0 1px #60a5fa;
  }

  .select-icon { width: 15px; height: 15px; color: #94a3b8; }

  .grade-select {
    background: transparent;
    border: none;
    color: #e2e8f0;
    font-size: 13px;
    font-weight: 500;
    outline: none;
    cursor: pointer;
    min-width: 80px;

    option { background: #1e293b; color: #e2e8f0; }
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
  min-width: 200px;
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
    &.gray { color: var(--text-muted); }
    &.blue { color: var(--primary-color); }
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

// 地图区域
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

// 返回全部学科按钮
.back-to-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 8px;

  &:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
  }

  .back-icon { width: 12px; height: 12px; }
}

// 学科分组
.subject-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: auto;
  transition: all 0.25s ease;

  &.clickable {
    cursor: pointer;

    &:hover {
      border-color: var(--primary-color);
      box-shadow: 0 0 0 1px var(--primary-color);
    }
  }

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

// 路径地图
.path-map {
  position: relative;
  width: 100%;
  min-height: 400px;
  padding: 30px 20px 100px 20px;
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

// 知识点节点
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
</style>

<template>
  <div class="mindmap-page">
    <!-- 左侧课程列表 -->
    <div class="course-sidebar">
      <div class="sidebar-header">
        <h3 class="sidebar-title">我的课程</h3>
        <span class="course-count">{{ filteredCourses.length }} 门课程</span>
      </div>
      <div class="subject-filter">
        <label>选择科目</label>
        <select v-model="selectedSubject">
          <option value="">全部科目</option>
          <option value="math">数学</option>
          <option value="physics">物理</option>
          <option value="chemistry">化学</option>
          <option value="biology">生物</option>
          <option value="english">英语</option>
          <option value="chinese">语文</option>
          <option value="history">历史</option>
          <option value="geography">地理</option>
          <option value="politics">政治</option>
          <option value="programming">编程</option>
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
  FlaskRound, Heart, Bookmark, MapPin, Users,
  CheckCircle, Clock, AlertCircle, Target
} from 'lucide-vue-next'

const icons = {
  Search, X, ChevronRight, ChevronDown,
  BookOpen, Code, Calculator, FlaskConical, Globe,
  FlaskRound, Heart, Bookmark, MapPin, Users,
  CheckCircle, Clock, AlertCircle, Target
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
    id: 'math',
    name: '高中数学',
    description: '函数、几何、概率统计',
    icon: Calculator,
    color: '#6366f1',
    chapterCount: 5,
    progress: 65,
    chapters: [
      {
        id: 'math-ch1', index: 1, title: '函数与导数', progress: 80,
        topics: [
          { id: 'math-1-1', title: '函数的概念与表示', status: 'completed', description: '理解函数的定义、定义域、值域及表示方法', duration: '45分钟', difficulty: 'easy',
            subtopics: [{ id: 'math-1-1-1', title: '函数的定义', status: 'completed' }, { id: 'math-1-1-2', title: '定义域与值域', status: 'completed' }, { id: 'math-1-1-3', title: '函数的表示法', status: 'completed' }] },
          { id: 'math-1-2', title: '函数的单调性与最值', status: 'completed', description: '掌握函数单调性的判断方法及最值求解', duration: '60分钟', difficulty: 'medium',
            subtopics: [{ id: 'math-1-2-1', title: '单调性的定义', status: 'completed' }, { id: 'math-1-2-2', title: '单调性的证明', status: 'completed' }, { id: 'math-1-2-3', title: '最值问题', status: 'completed' }] },
          { id: 'math-1-3', title: '导数的概念与计算', status: 'in-progress', description: '理解导数的几何意义，掌握基本求导公式', duration: '90分钟', difficulty: 'hard',
            subtopics: [{ id: 'math-1-3-1', title: '导数的定义', status: 'completed' }, { id: 'math-1-3-2', title: '基本求导公式', status: 'in-progress' }, { id: 'math-1-3-3', title: '复合函数求导', status: 'not-started' }] },
          { id: 'math-1-4', title: '导数的应用', status: 'not-started', description: '利用导数研究函数的单调性、极值与最值', duration: '120分钟', difficulty: 'hard',
            subtopics: [{ id: 'math-1-4-1', title: '单调性应用', status: 'not-started' }, { id: 'math-1-4-2', title: '极值与最值', status: 'not-started' }] }
        ]
      },
      {
        id: 'math-ch2', index: 2, title: '三角函数', progress: 45,
        topics: [
          { id: 'math-2-1', title: '任意角和弧度制', status: 'completed', duration: '30分钟', difficulty: 'easy' },
          { id: 'math-2-2', title: '三角函数的定义', status: 'completed', duration: '45分钟', difficulty: 'medium' },
          { id: 'math-2-3', title: '三角函数的图像与性质', status: 'in-progress', duration: '90分钟', difficulty: 'hard' },
          { id: 'math-2-4', title: '三角恒等变换', status: 'not-started', duration: '60分钟', difficulty: 'hard' }
        ]
      },
      {
        id: 'math-ch3', index: 3, title: '数列', progress: 100,
        topics: [
          { id: 'math-3-1', title: '数列的概念', status: 'completed', duration: '30分钟', difficulty: 'easy' },
          { id: 'math-3-2', title: '等差数列', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'math-3-3', title: '等比数列', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'math-3-4', title: '数列求和', status: 'completed', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      {
        id: 'math-ch4', index: 4, title: '立体几何', progress: 30,
        topics: [
          { id: 'math-4-1', title: '空间几何体', status: 'completed', duration: '45分钟', difficulty: 'medium' },
          { id: 'math-4-2', title: '点、线、面的位置关系', status: 'in-progress', duration: '90分钟', difficulty: 'hard' },
          { id: 'math-4-3', title: '空间向量与立体几何', status: 'not-started', duration: '120分钟', difficulty: 'hard' }
        ]
      },
      {
        id: 'math-ch5', index: 5, title: '概率与统计', progress: 60,
        topics: [
          { id: 'math-5-1', title: '随机事件的概率', status: 'completed', duration: '45分钟', difficulty: 'medium' },
          { id: 'math-5-2', title: '古典概型', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'math-5-3', title: '统计案例', status: 'in-progress', duration: '90分钟', difficulty: 'hard' }
        ]
      }
    ]
  },
  {
    id: 'physics',
    name: '高中物理',
    description: '力学、电磁学、光学',
    icon: FlaskConical,
    color: '#f59e0b',
    chapterCount: 4,
    progress: 40,
    chapters: [
      {
        id: 'phy-ch1', index: 1, title: '运动的描述', progress: 80,
        topics: [
          { id: 'phy-1-1', title: '质点参考系', status: 'completed', duration: '30分钟', difficulty: 'easy' },
          { id: 'phy-1-2', title: '时间和位移', status: 'completed', duration: '45分钟', difficulty: 'easy' },
          { id: 'phy-1-3', title: '速度', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'phy-1-4', title: '加速度', status: 'in-progress', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      {
        id: 'phy-ch2', index: 2, title: '匀变速直线运动', progress: 60,
        topics: [
          { id: 'phy-2-1', title: '实验：探究小车速度', status: 'completed', duration: '90分钟', difficulty: 'medium' },
          { id: 'phy-2-2', title: '匀变速直线运动规律', status: 'in-progress', duration: '120分钟', difficulty: 'hard' },
          { id: 'phy-2-3', title: '自由落体运动', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      {
        id: 'phy-ch3', index: 3, title: '相互作用', progress: 20,
        topics: [
          { id: 'phy-3-1', title: '重力基本相互作用', status: 'completed', duration: '45分钟', difficulty: 'easy' },
          { id: 'phy-3-2', title: '弹力', status: 'in-progress', duration: '60分钟', difficulty: 'medium' },
          { id: 'phy-3-3', title: '摩擦力', status: 'not-started', duration: '90分钟', difficulty: 'hard' },
          { id: 'phy-3-4', title: '力的合成与分解', status: 'not-started', duration: '120分钟', difficulty: 'hard' }
        ]
      },
      {
        id: 'phy-ch4', index: 4, title: '牛顿运动定律', progress: 0,
        topics: [
          { id: 'phy-4-1', title: '牛顿第一定律', status: 'not-started', duration: '60分钟', difficulty: 'medium' },
          { id: 'phy-4-2', title: '牛顿第二定律', status: 'not-started', duration: '90分钟', difficulty: 'hard' },
          { id: 'phy-4-3', title: '牛顿第三定律', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      }
    ]
  },
  {
    id: 'programming',
    name: 'Python编程',
    description: '基础语法、数据结构、算法',
    icon: Code,
    color: '#10b981',
    chapterCount: 4,
    progress: 75,
    chapters: [
      {
        id: 'prog-ch1', index: 1, title: 'Python基础', progress: 100,
        topics: [
          { id: 'prog-1-1', title: '变量与数据类型', status: 'completed', duration: '45分钟', difficulty: 'easy' },
          { id: 'prog-1-2', title: '运算符与表达式', status: 'completed', duration: '30分钟', difficulty: 'easy' },
          { id: 'prog-1-3', title: '条件语句', status: 'completed', duration: '60分钟', difficulty: 'easy' },
          { id: 'prog-1-4', title: '循环语句', status: 'completed', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      {
        id: 'prog-ch2', index: 2, title: '函数与模块', progress: 80,
        topics: [
          { id: 'prog-2-1', title: '函数定义与调用', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'prog-2-2', title: '参数与返回值', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'prog-2-3', title: '模块与包', status: 'in-progress', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      {
        id: 'prog-ch3', index: 3, title: '数据结构', progress: 60,
        topics: [
          { id: 'prog-3-1', title: '列表与元组', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'prog-3-2', title: '字典与集合', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'prog-3-3', title: '字符串操作', status: 'in-progress', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      {
        id: 'prog-ch4', index: 4, title: '面向对象编程', progress: 30,
        topics: [
          { id: 'prog-4-1', title: '类与对象', status: 'completed', duration: '90分钟', difficulty: 'hard' },
          { id: 'prog-4-2', title: '继承与多态', status: 'in-progress', duration: '120分钟', difficulty: 'hard' },
          { id: 'prog-4-3', title: '异常处理', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      }
    ]
  },
  {
    id: 'english',
    name: '高中英语',
    description: '语法、词汇、阅读、写作',
    icon: Globe,
    color: '#06b6d4',
    chapterCount: 4,
    progress: 55,
    chapters: [
      {
        id: 'eng-ch1', index: 1, title: '语法基础', progress: 70,
        topics: [
          { id: 'eng-1-1', title: '时态与语态', status: 'completed', duration: '90分钟', difficulty: 'medium',
            subtopics: [{ id: 'eng-1-1-1', title: '一般现在时', status: 'completed' }, { id: 'eng-1-1-2', title: '现在进行时', status: 'completed' }, { id: 'eng-1-1-3', title: '被动语态', status: 'in-progress' }] },
          { id: 'eng-1-2', title: '从句', status: 'in-progress', duration: '120分钟', difficulty: 'hard',
            subtopics: [{ id: 'eng-1-2-1', title: '定语从句', status: 'completed' }, { id: 'eng-1-2-2', title: '状语从句', status: 'in-progress' }, { id: 'eng-1-2-3', title: '名词性从句', status: 'not-started' }] },
          { id: 'eng-1-3', title: '非谓语动词', status: 'in-progress', duration: '90分钟', difficulty: 'hard',
            subtopics: [{ id: 'eng-1-3-1', title: '不定式', status: 'in-progress' }, { id: 'eng-1-3-2', title: '动名词', status: 'not-started' }, { id: 'eng-1-3-3', title: '分词', status: 'not-started' }] }
        ]
      },
      {
        id: 'eng-ch2', index: 2, title: '词汇拓展', progress: 60,
        topics: [
          { id: 'eng-2-1', title: '词根词缀', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'eng-2-2', title: '高频词汇', status: 'in-progress', duration: '120分钟', difficulty: 'medium' },
          { id: 'eng-2-3', title: '短语搭配', status: 'in-progress', duration: '90分钟', difficulty: 'medium' }
        ]
      },
      {
        id: 'eng-ch3', index: 3, title: '阅读理解', progress: 40,
        topics: [
          { id: 'eng-3-1', title: '阅读技巧', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'eng-3-2', title: '主旨大意题', status: 'in-progress', duration: '90分钟', difficulty: 'hard' },
          { id: 'eng-3-3', title: '推理判断题', status: 'not-started', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      {
        id: 'eng-ch4', index: 4, title: '写作技巧', progress: 20,
        topics: [
          { id: 'eng-4-1', title: '应用文写作', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'eng-4-2', title: '议论文写作', status: 'not-started', duration: '120分钟', difficulty: 'hard' }
        ]
      }
    ]
  },
  {
    id: 'chemistry',
    name: '高中化学',
    description: '无机化学、有机化学、化学反应',
    icon: FlaskRound,
    color: '#ef4444',
    chapterCount: 4,
    progress: 35,
    chapters: [
      { id: 'chem-ch1', index: 1, title: '物质结构', progress: 80,
        topics: [
          { id: 'chem-1-1', title: '原子结构', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'chem-1-2', title: '化学键', status: 'completed', duration: '90分钟', difficulty: 'hard' },
          { id: 'chem-1-3', title: '晶体结构', status: 'in-progress', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'chem-ch2', index: 2, title: '化学反应原理', progress: 50,
        topics: [
          { id: 'chem-2-1', title: '化学反应速率', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'chem-2-2', title: '化学平衡', status: 'in-progress', duration: '120分钟', difficulty: 'hard' },
          { id: 'chem-2-3', title: '电化学', status: 'not-started', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      { id: 'chem-ch3', index: 3, title: '有机化学', progress: 20,
        topics: [
          { id: 'chem-3-1', title: '烃类化合物', status: 'completed', duration: '90分钟', difficulty: 'medium' },
          { id: 'chem-3-2', title: '烃的衍生物', status: 'in-progress', duration: '120分钟', difficulty: 'hard' },
          { id: 'chem-3-3', title: '有机合成', status: 'not-started', duration: '120分钟', difficulty: 'hard' }
        ]
      },
      { id: 'chem-ch4', index: 4, title: '元素及其化合物', progress: 10,
        topics: [
          { id: 'chem-4-1', title: '金属元素', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'chem-4-2', title: '非金属元素', status: 'not-started', duration: '90分钟', difficulty: 'medium' },
          { id: 'chem-4-3', title: '化合物性质', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      }
    ]
  },
  {
    id: 'biology',
    name: '高中生物',
    description: '细胞、遗传、生态系统',
    icon: Heart,
    color: '#14b8a6',
    chapterCount: 4,
    progress: 45,
    chapters: [
      { id: 'bio-ch1', index: 1, title: '细胞结构与功能', progress: 90,
        topics: [
          { id: 'bio-1-1', title: '细胞膜与细胞器', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'bio-1-2', title: '细胞代谢', status: 'completed', duration: '90分钟', difficulty: 'hard' },
          { id: 'bio-1-3', title: '细胞分裂', status: 'in-progress', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'bio-ch2', index: 2, title: '遗传与进化', progress: 60,
        topics: [
          { id: 'bio-2-1', title: '孟德尔遗传定律', status: 'completed', duration: '90分钟', difficulty: 'hard' },
          { id: 'bio-2-2', title: 'DNA与基因', status: 'in-progress', duration: '120分钟', difficulty: 'hard' },
          { id: 'bio-2-3', title: '生物进化', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'bio-ch3', index: 3, title: '生命活动调节', progress: 30,
        topics: [
          { id: 'bio-3-1', title: '神经调节', status: 'completed', duration: '90分钟', difficulty: 'medium' },
          { id: 'bio-3-2', title: '体液调节', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'bio-3-3', title: '免疫调节', status: 'not-started', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      { id: 'bio-ch4', index: 4, title: '生态系统', progress: 20,
        topics: [
          { id: 'bio-4-1', title: '生态系统结构', status: 'in-progress', duration: '60分钟', difficulty: 'medium' },
          { id: 'bio-4-2', title: '能量流动', status: 'not-started', duration: '60分钟', difficulty: 'medium' },
          { id: 'bio-4-3', title: '生态平衡', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      }
    ]
  },
  {
    id: 'chinese',
    name: '高中语文',
    description: '文言文、现代文、写作',
    icon: Bookmark,
    color: '#ec4899',
    chapterCount: 4,
    progress: 50,
    chapters: [
      { id: 'chin-ch1', index: 1, title: '文言文阅读', progress: 70,
        topics: [
          { id: 'chin-1-1', title: '实词虚词', status: 'completed', duration: '90分钟', difficulty: 'medium' },
          { id: 'chin-1-2', title: '句式语法', status: 'completed', duration: '90分钟', difficulty: 'medium' },
          { id: 'chin-1-3', title: '文言文翻译', status: 'in-progress', duration: '120分钟', difficulty: 'hard' }
        ]
      },
      { id: 'chin-ch2', index: 2, title: '现代文阅读', progress: 60,
        topics: [
          { id: 'chin-2-1', title: '论述类文本', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'chin-2-2', title: '文学类文本', status: 'in-progress', duration: '90分钟', difficulty: 'hard' },
          { id: 'chin-2-3', title: '实用类文本', status: 'in-progress', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'chin-ch3', index: 3, title: '古代诗歌', progress: 40,
        topics: [
          { id: 'chin-3-1', title: '诗歌鉴赏', status: 'completed', duration: '90分钟', difficulty: 'hard' },
          { id: 'chin-3-2', title: '诗歌默写', status: 'in-progress', duration: '60分钟', difficulty: 'easy' },
          { id: 'chin-3-3', title: '诗歌表达', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'chin-ch4', index: 4, title: '写作', progress: 30,
        topics: [
          { id: 'chin-4-1', title: '审题立意', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'chin-4-2', title: '文章结构', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'chin-4-3', title: '语言表达', status: 'not-started', duration: '90分钟', difficulty: 'hard' }
        ]
      }
    ]
  },
  {
    id: 'history',
    name: '高中历史',
    description: '中国史、世界史、近代史',
    icon: BookOpen,
    color: '#8b5cf6',
    chapterCount: 4,
    progress: 30,
    chapters: [
      { id: 'hist-ch1', index: 1, title: '中国古代史', progress: 60,
        topics: [
          { id: 'hist-1-1', title: '先秦时期', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'hist-1-2', title: '秦汉至隋唐', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'hist-1-3', title: '宋元明清', status: 'in-progress', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      { id: 'hist-ch2', index: 2, title: '中国近代史', progress: 40,
        topics: [
          { id: 'hist-2-1', title: '晚清时期', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'hist-2-2', title: '民国时期', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'hist-2-3', title: '新中国史', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'hist-ch3', index: 3, title: '世界古代史', progress: 20,
        topics: [
          { id: 'hist-3-1', title: '古代文明', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'hist-3-2', title: '中世纪', status: 'in-progress', duration: '60分钟', difficulty: 'medium' },
          { id: 'hist-3-3', title: '文艺复兴', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'hist-ch4', index: 4, title: '世界近现代史', progress: 10,
        topics: [
          { id: 'hist-4-1', title: '工业革命', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'hist-4-2', title: '两次世界大战', status: 'not-started', duration: '90分钟', difficulty: 'hard' },
          { id: 'hist-4-3', title: '冷战与全球化', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      }
    ]
  },
  {
    id: 'geography',
    name: '高中地理',
    description: '自然地理、人文地理、区域地理',
    icon: MapPin,
    color: '#10b981',
    chapterCount: 4,
    progress: 25,
    chapters: [
      { id: 'geo-ch1', index: 1, title: '地球与地图', progress: 70,
        topics: [
          { id: 'geo-1-1', title: '地球运动', status: 'completed', duration: '90分钟', difficulty: 'hard' },
          { id: 'geo-1-2', title: '地图知识', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'geo-1-3', title: '等高线', status: 'in-progress', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'geo-ch2', index: 2, title: '自然地理', progress: 40,
        topics: [
          { id: 'geo-2-1', title: '大气运动', status: 'completed', duration: '90分钟', difficulty: 'hard' },
          { id: 'geo-2-2', title: '水循环', status: 'in-progress', duration: '60分钟', difficulty: 'medium' },
          { id: 'geo-2-3', title: '地质地貌', status: 'not-started', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      { id: 'geo-ch3', index: 3, title: '人文地理', progress: 20,
        topics: [
          { id: 'geo-3-1', title: '人口与城市', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'geo-3-2', title: '农业区位', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'geo-3-3', title: '工业区位', status: 'not-started', duration: '90分钟', difficulty: 'medium' }
        ]
      },
      { id: 'geo-ch4', index: 4, title: '区域地理', progress: 10,
        topics: [
          { id: 'geo-4-1', title: '中国区域', status: 'in-progress', duration: '90分钟', difficulty: 'medium' },
          { id: 'geo-4-2', title: '世界区域', status: 'not-started', duration: '90分钟', difficulty: 'medium' },
          { id: 'geo-4-3', title: '区域可持续发展', status: 'not-started', duration: '90分钟', difficulty: 'hard' }
        ]
      }
    ]
  },
  {
    id: 'politics',
    name: '高中政治',
    description: '经济、政治、哲学、法治',
    icon: Users,
    color: '#f97316',
    chapterCount: 4,
    progress: 40,
    chapters: [
      { id: 'pol-ch1', index: 1, title: '经济生活', progress: 70,
        topics: [
          { id: 'pol-1-1', title: '商品与货币', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'pol-1-2', title: '消费与生产', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'pol-1-3', title: '市场经济', status: 'in-progress', duration: '90分钟', difficulty: 'hard' }
        ]
      },
      { id: 'pol-ch2', index: 2, title: '政治生活', progress: 50,
        topics: [
          { id: 'pol-2-1', title: '公民与政府', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'pol-2-2', title: '政党制度', status: 'in-progress', duration: '60分钟', difficulty: 'medium' },
          { id: 'pol-2-3', title: '国际社会', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'pol-ch3', index: 3, title: '文化生活', progress: 30,
        topics: [
          { id: 'pol-3-1', title: '文化传承', status: 'completed', duration: '60分钟', difficulty: 'medium' },
          { id: 'pol-3-2', title: '文化创新', status: 'in-progress', duration: '60分钟', difficulty: 'medium' },
          { id: 'pol-3-3', title: '中华文化', status: 'not-started', duration: '60分钟', difficulty: 'medium' }
        ]
      },
      { id: 'pol-ch4', index: 4, title: '生活与哲学', progress: 20,
        topics: [
          { id: 'pol-4-1', title: '唯物论', status: 'in-progress', duration: '90分钟', difficulty: 'hard' },
          { id: 'pol-4-2', title: '辩证法', status: 'not-started', duration: '120分钟', difficulty: 'hard' },
          { id: 'pol-4-3', title: '认识论', status: 'not-started', duration: '90分钟', difficulty: 'hard' }
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
  const color = selectedCourse.value.color

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

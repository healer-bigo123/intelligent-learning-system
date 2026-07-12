<template>
  <div class="resources">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="search-section">
        <div class="search-box">
          <component :is="icons.Search" class="search-icon" />
          <input type="text" v-model="searchQuery" placeholder="搜索课程、讲师..." class="search-input" />
          <button class="search-btn">
            <component :is="icons.Search" class="btn-icon" />
          </button>
        </div>
      </div>

      <select v-model="activeCategory" class="filter-select">
        <option value="all">全部学科</option>
        <option v-for="tab in categoryTabs.filter(t => t.id !== 'all')" :key="tab.id" :value="tab.id">{{ tab.label }}</option>
      </select>

      <div class="sort-section">
        <div class="sort-select-wrapper">
          <component :is="icons.ArrowDown" class="sort-icon" />
          <select v-model="sortBy" class="sort-select">
            <option value="recommend">推荐排序</option>
            <option value="latest">最新发布</option>
            <option value="popular">最受欢迎</option>
            <option value="duration">时长最短</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 课程网格 -->
    <div class="courses-grid">
      <div v-for="course in filteredCourses" :key="course.id" class="course-card">
        <div class="course-cover" :style="{ background: course.coverColor }">
          <div class="cover-overlay">
            <button class="play-btn">
              <component :is="icons.Play" class="play-icon" />
            </button>
          </div>
          <div class="course-badge" v-if="course.isNew">
            <component :is="icons.Star" class="badge-icon" />
            新课
          </div>
          <div class="course-badge popular" v-else-if="course.isPopular">
            <component :is="icons.Flame" class="badge-icon" />
            热门
          </div>
        </div>

        <div class="course-content">
          <div class="course-header">
            <span class="course-category">{{ course.category }}</span>
            <span class="course-rating">
              <component :is="icons.Star" class="star-icon" />
              {{ course.rating }}
            </span>
          </div>

          <h3 class="course-title">{{ course.title }}</h3>
          <p class="course-desc">{{ course.description }}</p>

          <div class="course-meta">
            <div class="instructor-info">
              <div class="instructor-avatar" :style="{ background: course.instructorColor }">
                <component :is="icons.User" class="avatar-icon" />
              </div>
              <span class="instructor-name">{{ course.instructor }}</span>
            </div>
            <div class="course-stats">
              <span class="stat-item">
                <component :is="icons.Users" class="stat-icon" />
                {{ course.students }}
              </span>
              <span class="stat-item">
                <component :is="icons.Clock" class="stat-icon" />
                {{ course.duration }}
              </span>
            </div>
          </div>

          <div class="course-tags">
            <span v-for="tag in course.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>

          <button class="enroll-btn" :class="{ enrolled: course.enrolled }">
            {{ course.enrolled ? '继续学习' : '开始学习' }}
            <component :is="course.enrolled ? icons.ArrowRight : icons.Plus" class="btn-icon" />
          </button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <button class="page-btn" :disabled="currentPage === 1">
        <component :is="icons.ChevronLeft" class="page-icon" />
      </button>
      <button
        v-for="page in visiblePages"
        :key="page"
        class="page-btn"
        :class="{ active: currentPage === page, dots: page === '...' }"
        @click="currentPage = typeof page === 'number' ? page : currentPage"
      >
        {{ page }}
      </button>
      <button class="page-btn" :disabled="currentPage === totalPages">
        <component :is="icons.ChevronRight" class="page-icon" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Search, Play, Star, Flame, Users, Clock,
  User, ArrowRight, Plus, ChevronLeft, ChevronRight,
  BookOpen, Calculator, FlaskConical, Globe, Code, Music,
  ArrowDown
} from 'lucide-vue-next'
import { api } from '@/api/client'

const icons = {
  Search, Play, Star, Flame, Users, Clock,
  User, ArrowRight, Plus, ChevronLeft, ChevronRight,
  BookOpen, Calculator, FlaskConical, Globe, Code, Music,
  ArrowDown
}

const categoryTabs = [
  { id: 'all', label: '全部学科', icon: BookOpen, color: '#6366f1' },
  { id: 'math', label: '数学', icon: Calculator, color: '#3b82f6' },
  { id: 'physics', label: '物理', icon: FlaskConical, color: '#10b981' },
  { id: 'chemistry', label: '化学', icon: FlaskConical, color: '#ef4444' },
  { id: 'biology', label: '生物', icon: FlaskConical, color: '#06b6d4' },
  { id: 'english', label: '英语', icon: Globe, color: '#f59e0b' },
  { id: 'chinese', label: '语文', icon: BookOpen, color: '#ec4899' },
  { id: 'history', label: '历史', icon: BookOpen, color: '#8b5cf6' },
  { id: 'geography', label: '地理', icon: Globe, color: '#14b8a6' },
  { id: 'politics', label: '政治', icon: BookOpen, color: '#f97316' },
  { id: 'programming', label: '编程', icon: Code, color: '#8b5cf6' }
]

const searchQuery = ref('')
const activeCategory = ref('all')
const sortBy = ref('recommend')
const currentPage = ref(1)
const pageSize = 6

const courses = ref<any[]>([])
const loading = ref(false)

// 从后端加载学习资料
const loadResources = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize
    }
    
    // 映射分类
    const categoryMap: Record<string, string> = {
      math: '数学',
      physics: '物理',
      chemistry: '化学',
      biology: '生物',
      english: '英语',
      chinese: '语文',
      history: '历史',
      geography: '地理',
      politics: '政治',
      programming: '编程'
    }
    
    if (activeCategory.value !== 'all') {
      params.subject = categoryMap[activeCategory.value] || activeCategory.value
    }
    
    if (searchQuery.value) {
      params.keyword = searchQuery.value
    }
    
    const response = await api.get('/study-materials', { params })
    const data = response.data
    
    // 转换数据格式
    const colorMap: Record<string, string> = {
      '数学': '#3b82f6',
      '物理': '#10b981',
      '化学': '#ef4444',
      '英语': '#f59e0b',
      '编程': '#8b5cf6'
    }
    
    courses.value = (data.items || []).map((item: any, index: number) => ({
      id: item.id,
      title: item.title,
      description: item.content?.substring(0, 50) + '...' || '暂无描述',
      category: item.subject,
      categoryId: Object.entries(categoryMap).find(([k, v]) => v === item.subject)?.[0] || 'math',
      coverColor: `linear-gradient(135deg, ${colorMap[item.subject] || '#6366f1'}, ${colorMap[item.subject] || '#6366f1'}dd)`,
      instructor: item.source || '系统',
      instructorColor: colorMap[item.subject] || '#6366f1',
      rating: 4.5,
      students: '0',
      duration: `${item.difficulty || 1}级难度`,
      tags: [item.material_type, item.knowledge_point].filter(Boolean),
      isNew: false,
      isPopular: false,
      enrolled: false
    }))
  } catch (error) {
    console.error('加载学习资料失败:', error)
  } finally {
    loading.value = false
  }
}

const filteredCourses = computed(() => {
  return courses.value
})

const totalPages = computed(() => Math.ceil(courses.value.length / pageSize))

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 5) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      pages.push(1, 2, 3, 4, '...', total)
    } else if (current >= total - 2) {
      pages.push(1, '...', total - 3, total - 2, total - 1, total)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }

  return pages
})

// 监听筛选条件变化
import { watch } from 'vue'
watch([activeCategory, searchQuery], () => {
  currentPage.value = 1
  loadResources()
})

onMounted(() => {
  loadResources()
})
</script>

<style lang="scss" scoped>
.resources {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0;
  background: transparent;
  border: none;
  box-shadow: none;
}

.search-section {
  flex: 0 0 auto;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid #475569;
  border-radius: var(--radius-md);
  padding: 7px 10px;
  min-width: 110px;
  height: 40px;
  transition: all 0.3s ease;
  box-shadow: 
    0 2px 6px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);

  &:hover,
  &:focus-within {
    border-color: #60a5fa;
    box-shadow: 
      0 2px 6px rgba(0, 0, 0, 0.15),
      0 0 0 1px #60a5fa;
  }

  .search-icon {
    width: 15px;
    height: 15px;
    color: #94a3b8;
    flex-shrink: 0;
  }

  .search-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #e2e8f0;
    font-size: 13px;
    min-width: 0;

    &::placeholder {
      color: #64748b;
    }
  }
}

.filter-select {
  padding: 8px 12px;
  background: linear-gradient(145deg, #273548, #1e293b);
  border: 2px solid #475569;
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

.sort-section {
  .sort-select-wrapper {
    display: flex;
    align-items: center;
    gap: 7px;
    background: linear-gradient(145deg, #273548, #1e293b);
    border: 2px solid #475569;
    border-radius: var(--radius-md);
    padding: 0 12px;
    min-width: 100px;
    height: 40px;
    transition: all 0.3s ease;
    box-shadow: 
      0 2px 6px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.05);

    &:hover {
      border-color: #60a5fa;
      box-shadow: 
        0 2px 6px rgba(0, 0, 0, 0.15),
        0 0 0 1px #60a5fa;
    }

    .sort-icon {
      width: 15px;
      height: 15px;
      color: #94a3b8;
    }

    .sort-select {
      background: transparent;
      border: none;
      color: #e2e8f0;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      outline: none;
      min-width: 0;
      width: 70px;

      option {
        background: #1e293b;
        color: #f1f5f9;
        padding: 8px 12px;
      }
    }
  }
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.course-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
    border-color: var(--primary-color);
  }
}

.course-cover {
  position: relative;
  height: 160px;
  background-size: cover;
  background-position: center;
}

.cover-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;

  .course-card:hover & {
    opacity: 1;
  }
}

.play-btn {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.1);
    background: white;
  }

  .play-icon {
    width: 20px;
    height: 20px;
    color: var(--primary-color);
    margin-left: 3px;
  }
}

.course-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(239, 68, 68, 0.9);
  border-radius: 12px;
  font-size: 11px;
  color: white;
  font-weight: 500;

  &.popular {
    background: rgba(245, 158, 11, 0.9);
  }

  .badge-icon {
    width: 12px;
    height: 12px;
  }
}

.course-content {
  padding: 20px;
}

.course-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.course-category {
  font-size: 11px;
  padding: 4px 10px;
  background: rgba(99, 102, 241, 0.1);
  border-radius: 4px;
  color: var(--primary-color);
  font-weight: 500;
}

.course-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--warning-color);
  font-weight: 500;

  .star-icon {
    width: 14px;
    height: 14px;
    fill: var(--warning-color);
  }
}

.course-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 16px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.instructor-info {
  display: flex;
  align-items: center;
  gap: 8px;

  .instructor-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;

    .avatar-icon {
      width: 14px;
      height: 14px;
      color: white;
    }
  }

  .instructor-name {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.course-stats {
  display: flex;
  gap: 16px;

  .stat-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--text-muted);

    .stat-icon {
      width: 14px;
      height: 14px;
    }
  }
}

.course-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 20px;

  .tag {
    font-size: 10px;
    padding: 4px 10px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    color: var(--text-secondary);
  }
}

.enroll-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: var(--primary-color);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: var(--primary-dark);
    transform: translateY(-2px);
  }

  &.enrolled {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);

    &:hover {
      background: var(--bg-card);
      border-color: var(--primary-color);
    }
  }

  .btn-icon {
    width: 16px;
    height: 16px;
  }
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
}

.page-btn {
  width: 36px;
  height: 36px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.2s ease;

  &:hover:not(.disabled):not(.dots) {
    background: var(--bg-tertiary);
    border-color: var(--primary-color);
    color: var(--text-primary);
  }

  &.active {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
  }

  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.dots {
    background: transparent;
    border: none;
    cursor: default;
  }

  .page-icon {
    width: 14px;
    height: 14px;
  }
}
</style>
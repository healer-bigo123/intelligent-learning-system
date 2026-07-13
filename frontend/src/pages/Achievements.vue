<template>
  <div class="achievements-page">
    <!-- 顶部统计区域 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon trophy">
          <Award class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value gold">{{ stats.total }}</div>
          <div class="stat-label">总成就数</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon star">
          <Star class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value green">{{ stats.unlocked }}</div>
          <div class="stat-label">已解锁</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon zap">
          <Zap class="icon" />
        </div>
        <div class="stat-info">
          <div class="stat-value purple">{{ stats.points }}</div>
          <div class="stat-label">成就点数</div>
        </div>
      </div>
    </div>

    <!-- 总进度条 -->
    <div class="progress-section">
      <div class="progress-header">
        <span class="progress-label">成就完成进度</span>
        <span class="progress-percent">{{ completionPercent }}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: completionPercent + '%' }"></div>
      </div>
    </div>

    <!-- 分类筛选标签 -->
    <div class="category-tabs">
      <button
        v-for="cat in categories"
        :key="cat.key"
        class="tab-btn"
        :class="{ active: activeCategory === cat.key }"
        @click="activeCategory = cat.key"
      >
        <component :is="cat.icon" class="tab-icon" />
        {{ cat.label }}
      </button>
    </div>

    <!-- 成就卡片网格 -->
    <div class="achievements-grid">
      <div
        v-for="item in filteredAchievements"
        :key="item.id"
        class="achievement-card"
        :class="{ unlocked: item.unlocked, locked: !item.unlocked }"
      >
        <div class="card-icon-wrapper" :class="item.iconClass">
          <component :is="item.icon" class="card-icon" />
        </div>

        <div class="card-body">
          <div class="card-name">{{ item.name }}</div>
          <div class="card-desc">{{ item.description }}</div>
        </div>

        <div class="card-footer">
          <span class="card-points">+{{ item.points }} 点</span>
          <span class="card-badge" :class="{ unlocked: item.unlocked }">
            <component :is="item.unlocked ? Award : Lock" class="badge-icon" />
            {{ item.unlocked ? '已解锁' : '未解锁' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Star, Flame, BookOpen, Target, Clock,
  Award, Lock, Zap, Heart, Share2, Users
} from 'lucide-vue-next'
import type { Component } from 'vue'

const categories = [
  { key: 'all', label: '全部', icon: Star },
  { key: 'learning', label: '学习达人', icon: BookOpen },
  { key: 'streak', label: '坚持之星', icon: Flame },
  { key: 'explore', label: '知识探索', icon: Target },
  { key: 'social', label: '社交互动', icon: Heart }
]

const activeCategory = ref('all')

interface Achievement {
  id: number
  name: string
  description: string
  points: number
  icon: Component
  iconClass: string
  unlocked: boolean
  category: string
}

const achievements = ref<Achievement[]>([
  {
    id: 1,
    name: '首次登录',
    description: '第一次成功登录学习平台，开启学习之旅',
    points: 10,
    icon: Award,
    iconClass: 'icon-trophy',
    unlocked: true,
    category: 'learning'
  },
  {
    id: 2,
    name: '连续学习7天',
    description: '连续7天保持学习打卡，养成良好习惯',
    points: 50,
    icon: Flame,
    iconClass: 'icon-flame',
    unlocked: true,
    category: 'streak'
  },
  {
    id: 3,
    name: '完成100道题',
    description: '累计完成100道练习题，知识量稳步提升',
    points: 80,
    icon: BookOpen,
    iconClass: 'icon-book',
    unlocked: true,
    category: 'explore'
  },
  {
    id: 4,
    name: '专注学习10小时',
    description: '累计专注学习达到10小时，深度学习达人',
    points: 100,
    icon: Clock,
    iconClass: 'icon-clock',
    unlocked: false,
    category: 'streak'
  },
  {
    id: 5,
    name: '掌握50个知识点',
    description: '成功掌握50个核心知识点，知识体系初步建立',
    points: 120,
    icon: Target,
    iconClass: 'icon-target',
    unlocked: false,
    category: 'explore'
  },
  {
    id: 6,
    name: '获得第一个满分',
    description: '在某次练习中获得满分，表现优异',
    points: 60,
    icon: Award,
    iconClass: 'icon-award',
    unlocked: true,
    category: 'learning'
  },
  {
    id: 7,
    name: '分享学习笔记',
    description: '首次分享学习笔记给其他同学，知识传递',
    points: 30,
    icon: Share2,
    iconClass: 'icon-share',
    unlocked: false,
    category: 'social'
  },
  {
    id: 8,
    name: '帮助3位同学',
    description: '在学习社区中成功帮助3位同学解答问题',
    points: 70,
    icon: Users,
    iconClass: 'icon-users',
    unlocked: false,
    category: 'social'
  },
  {
    id: 9,
    name: '完成所有课程',
    description: '完成平台上所有课程的学习，全面掌握知识',
    points: 200,
    icon: Star,
    iconClass: 'icon-star',
    unlocked: false,
    category: 'learning'
  }
])

const stats = computed(() => {
  const total = achievements.value.length
  const unlocked = achievements.value.filter(a => a.unlocked).length
  const points = achievements.value
    .filter(a => a.unlocked)
    .reduce((sum, a) => sum + a.points, 0)
  return { total, unlocked, points }
})

const completionPercent = computed(() => {
  if (stats.value.total === 0) return 0
  return Math.round((stats.value.unlocked / stats.value.total) * 100)
})

const filteredAchievements = computed(() => {
  if (activeCategory.value === 'all') return achievements.value
  return achievements.value.filter(a => a.category === activeCategory.value)
})
</script>

<style lang="scss" scoped>
.achievements-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: var(--radius-md);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-color: rgba(99, 102, 241, 0.4);
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;

  .icon {
    width: 24px;
    height: 24px;
  }

  &.trophy {
    background: rgba(245, 158, 11, 0.12);
    .icon { color: rgba(245, 158, 11, 0.9); }
  }

  &.star {
    background: rgba(16, 185, 129, 0.12);
    .icon { color: rgba(16, 185, 129, 0.9); }
  }

  &.zap {
    background: rgba(139, 92, 246, 0.12);
    .icon { color: rgba(139, 92, 246, 0.9); }
  }
}

.stat-info {
  .stat-value {
    font-size: 30px;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;

    &.gold { color: rgba(245, 158, 11, 0.95); }
    &.green { color: rgba(16, 185, 129, 0.95); }
    &.purple { color: rgba(139, 92, 246, 0.95); }
  }

  .stat-label {
    font-size: 12px;
    color: rgba(148, 163, 184, 0.7);
    margin-top: 4px;
  }
}

.progress-section {
  padding: 18px 20px;
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(71, 85, 105, 0.4);
  border-radius: var(--radius-md);

  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }

  .progress-label {
    font-size: 13px;
    color: rgba(241, 245, 249, 0.85);
    font-weight: 500;
  }

  .progress-percent {
    font-size: 13px;
    color: rgba(99, 102, 241, 0.9);
    font-weight: 600;
  }

  .progress-bar {
    height: 8px;
    background: rgba(51, 65, 85, 0.5);
    border-radius: 4px;
    overflow: hidden;

    .progress-fill {
      height: 100%;
      border-radius: 4px;
      background: linear-gradient(90deg, rgba(99, 102, 241, 0.7), rgba(139, 92, 246, 0.7));
      transition: width 0.6s ease;
    }
  }
}

.category-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(51, 65, 85, 0.4);
  border: 1px solid rgba(71, 85, 105, 0.5);
  border-radius: var(--radius-md);
  color: rgba(148, 163, 184, 0.8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;

  .tab-icon {
    width: 15px;
    height: 15px;
  }

  &:hover {
    background: rgba(51, 65, 85, 0.6);
    color: rgba(241, 245, 249, 0.9);
  }

  &.active {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
    border-color: rgba(99, 102, 241, 0.5);
    color: rgba(241, 245, 249, 0.95);
  }
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.achievement-card {
  display: flex;
  flex-direction: column;
  padding: 22px 20px;
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(71, 85, 105, 0.4);
  border-radius: var(--radius-md);
  transition: all 0.3s ease;

  &.unlocked {
    border-color: rgba(245, 158, 11, 0.3);
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.06);

    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 0 30px rgba(245, 158, 11, 0.12), 0 8px 20px rgba(0, 0, 0, 0.2);
      border-color: rgba(245, 158, 11, 0.5);
    }
  }

  &.locked {
    opacity: 0.5;

    &:hover {
      opacity: 0.7;
      transform: translateY(-2px);
    }

    .card-icon-wrapper {
      background: rgba(51, 65, 85, 0.3);

      .card-icon {
        color: rgba(148, 163, 184, 0.4);
      }
    }
  }
}

.card-icon-wrapper {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  transition: all 0.3s ease;

  .card-icon {
    width: 30px;
    height: 30px;
    transition: color 0.3s ease;
  }

  &.icon-trophy {
    background: rgba(245, 158, 11, 0.12);
    .card-icon { color: rgba(245, 158, 11, 0.85); }
  }

  &.icon-flame {
    background: rgba(239, 68, 68, 0.12);
    .card-icon { color: rgba(239, 68, 68, 0.85); }
  }

  &.icon-book {
    background: rgba(59, 130, 246, 0.12);
    .card-icon { color: rgba(59, 130, 246, 0.85); }
  }

  &.icon-clock {
    background: rgba(139, 92, 246, 0.12);
    .card-icon { color: rgba(139, 92, 246, 0.85); }
  }

  &.icon-target {
    background: rgba(16, 185, 129, 0.12);
    .card-icon { color: rgba(16, 185, 129, 0.85); }
  }

  &.icon-award {
    background: rgba(245, 158, 11, 0.12);
    .card-icon { color: rgba(245, 158, 11, 0.85); }
  }

  &.icon-share {
    background: rgba(99, 102, 241, 0.12);
    .card-icon { color: rgba(99, 102, 241, 0.85); }
  }

  &.icon-users {
    background: rgba(244, 114, 182, 0.12);
    .card-icon { color: rgba(244, 114, 182, 0.85); }
  }

  &.icon-star {
    background: rgba(251, 191, 36, 0.12);
    .card-icon { color: rgba(251, 191, 36, 0.85); }
  }
}

.unlocked .card-icon-wrapper {
  &.icon-trophy { background: rgba(245, 158, 11, 0.18); }
  &.icon-flame { background: rgba(239, 68, 68, 0.18); }
  &.icon-book { background: rgba(59, 130, 246, 0.18); }
  &.icon-clock { background: rgba(139, 92, 246, 0.18); }
  &.icon-target { background: rgba(16, 185, 129, 0.18); }
  &.icon-award { background: rgba(245, 158, 11, 0.18); }
  &.icon-share { background: rgba(99, 102, 241, 0.18); }
  &.icon-users { background: rgba(244, 114, 182, 0.18); }
  &.icon-star { background: rgba(251, 191, 36, 0.18); }
}

.card-body {
  flex: 1;
  margin-bottom: 16px;

  .card-name {
    font-size: 15px;
    font-weight: 600;
    color: rgba(241, 245, 249, 0.92);
    margin-bottom: 6px;
  }

  .card-desc {
    font-size: 12px;
    color: rgba(148, 163, 184, 0.65);
    line-height: 1.6;
  }
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid rgba(71, 85, 105, 0.3);

  .card-points {
    font-size: 13px;
    font-weight: 600;
    color: rgba(245, 158, 11, 0.9);
  }

  .card-badge {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 10px;
    background: rgba(71, 85, 105, 0.4);
    color: rgba(148, 163, 184, 0.6);

    .badge-icon {
      width: 12px;
      height: 12px;
    }

    &.unlocked {
      background: rgba(16, 185, 129, 0.15);
      color: rgba(16, 185, 129, 0.9);
    }
  }
}
</style>

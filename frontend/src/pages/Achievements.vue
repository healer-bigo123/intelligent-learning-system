<template>
  <div class="achievements-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载成就数据...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="achievements.length === 0" class="empty-state">
      <Award class="empty-icon" />
      <p>暂无成就数据</p>
      <p class="empty-hint">完成学习任务来解锁成就吧！</p>
    </div>

    <!-- 正常内容 -->
    <template v-else>
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
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Star, Flame, BookOpen, Target, Clock,
  Award, Lock, Zap, Heart, Share2, Users,
  Lightbulb, Cpu, Shield, Aperture, Search, Code, Globe
} from 'lucide-vue-next'
import type { Component } from 'vue'
import { getAchievements, getMyAchievements, checkAchievements, type AchievementItem } from '@/api/achievements'

const categories = [
  { key: 'all', label: '全部', icon: Star },
  { key: 'learning', label: '学习达人', icon: BookOpen },
  { key: 'streak', label: '坚持之星', icon: Flame },
  { key: 'explore', label: '知识探索', icon: Target },
  { key: 'social', label: '社交互动', icon: Heart }
]

const activeCategory = ref('all')

// 条件类型 → 分类映射
const conditionTypeToCategory: Record<string, string> = {
  exercise_count: 'explore',
  streak_days: 'streak',
  accuracy: 'learning',
  material_count: 'learning',
  login_count: 'learning',
  study_hours: 'streak',
  knowledge_mastered: 'explore',
  full_score: 'learning',
  share_count: 'social',
  help_count: 'social',
  course_completed: 'learning'
}

// 条件类型 → 图标映射
const conditionTypeToIcon: Record<string, Component> = {
  exercise_count: BookOpen,
  streak_days: Flame,
  accuracy: Award,
  material_count: Star,
  login_count: Award,
  study_hours: Clock,
  knowledge_mastered: Target,
  full_score: Award,
  share_count: Share2,
  help_count: Users,
  course_completed: Star
}

// 条件类型 → 图标样式类名
const conditionTypeToIconClass: Record<string, string> = {
  exercise_count: 'icon-book',
  streak_days: 'icon-flame',
  accuracy: 'icon-award',
  material_count: 'icon-star',
  login_count: 'icon-trophy',
  study_hours: 'icon-clock',
  knowledge_mastered: 'icon-target',
  full_score: 'icon-award',
  share_count: 'icon-share',
  help_count: 'icon-users',
  course_completed: 'icon-star'
}

// 条件类型 → 成就点数
const conditionTypeToPoints: Record<string, number> = {
  exercise_count: 80,
  streak_days: 50,
  accuracy: 60,
  material_count: 30,
  login_count: 10,
  study_hours: 100,
  knowledge_mastered: 120,
  full_score: 60,
  share_count: 30,
  help_count: 70,
  course_completed: 200
}

interface Achievement {
  id: string
  name: string
  description: string
  points: number
  icon: Component
  iconClass: string
  unlocked: boolean
  unlocked_at?: string
  category: string
  condition_type: string
  condition_value: number
}

const achievements = ref<Achievement[]>([])
const loading = ref(true)

// 条件类型 → 描述后缀
function getConditionDesc(condition_type: string, condition_value: number): string {
  const descMap: Record<string, string> = {
    exercise_count: `累计完成${condition_value}道练习题`,
    streak_days: `连续学习${condition_value}天`,
    accuracy: `练习正确率达到${condition_value}%`,
    material_count: `收藏${condition_value}份学习资料`,
    login_count: `累计登录${condition_value}次`,
    study_hours: `累计专注学习${condition_value}小时`,
    knowledge_mastered: `掌握${condition_value}个知识点`,
    full_score: `获得${condition_value}次满分`,
    share_count: `分享${condition_value}次学习笔记`,
    help_count: `帮助${condition_value}位同学`,
    course_completed: `完成${condition_value}门课程`
  }
  return descMap[condition_type] || `达成条件：${condition_value}`
}

async function loadAchievements() {
  loading.value = true
  try {
    // 并行获取成就列表和已解锁成就
    const [allRes, myRes] = await Promise.all([
      getAchievements(),
      getMyAchievements()
    ])

    // 尝试检查是否有新解锁的成就
    try {
      await checkAchievements()
      // 重新获取已解锁成就
      const updatedMyRes = await getMyAchievements()
      const unlockedIds = new Set(updatedMyRes.items.map(item => item.achievement.id))
      const unlockedMap = new Map(updatedMyRes.items.map(item => [item.achievement.id, item.unlocked_at]))

      achievements.value = allRes.map(item => {
        const isUnlocked = unlockedIds.has(item.id)
        const category = conditionTypeToCategory[item.condition_type] || 'learning'
        return {
          id: item.id,
          name: item.name,
          description: item.description || getConditionDesc(item.condition_type, item.condition_value),
          points: conditionTypeToPoints[item.condition_type] || 50,
          icon: conditionTypeToIcon[item.condition_type] || Star,
          iconClass: conditionTypeToIconClass[item.condition_type] || 'icon-trophy',
          unlocked: isUnlocked,
          unlocked_at: unlockedMap.get(item.id),
          category,
          condition_type: item.condition_type,
          condition_value: item.condition_value
        }
      })
    } catch {
      // check 失败时使用原始数据
      const unlockedIds = new Set(myRes.items.map(item => item.achievement.id))
      const unlockedMap = new Map(myRes.items.map(item => [item.achievement.id, item.unlocked_at]))

      achievements.value = allRes.map(item => {
        const isUnlocked = unlockedIds.has(item.id)
        const category = conditionTypeToCategory[item.condition_type] || 'learning'
        return {
          id: item.id,
          name: item.name,
          description: item.description || getConditionDesc(item.condition_type, item.condition_value),
          points: conditionTypeToPoints[item.condition_type] || 50,
          icon: conditionTypeToIcon[item.condition_type] || Star,
          iconClass: conditionTypeToIconClass[item.condition_type] || 'icon-trophy',
          unlocked: isUnlocked,
          unlocked_at: unlockedMap.get(item.id),
          category,
          condition_type: item.condition_type,
          condition_value: item.condition_value
        }
      })
    }
  } catch (e) {
    console.error('加载成就数据失败:', e)
  } finally {
    loading.value = false
  }
}

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

onMounted(() => {
  loadAchievements()
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
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  &.unlocked {
    border-color: rgba(245, 158, 11, 0.4);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), 0 0 20px rgba(245, 158, 11, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.05);

    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3), 0 0 30px rgba(245, 158, 11, 0.12);
      border-color: rgba(245, 158, 11, 0.6);
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

  &.icon-lightbulb {
    background: rgba(99, 102, 241, 0.12);
    .card-icon { color: rgba(99, 102, 241, 0.85); }
  }

  &.icon-search {
    background: rgba(245, 158, 11, 0.12);
    .card-icon { color: rgba(245, 158, 11, 0.85); }
  }

  &.icon-code {
    background: rgba(16, 185, 129, 0.12);
    .card-icon { color: rgba(16, 185, 129, 0.85); }
  }

  &.icon-cpu {
    background: rgba(239, 68, 68, 0.12);
    .card-icon { color: rgba(239, 68, 68, 0.85); }
  }

  &.icon-globe {
    background: rgba(139, 92, 246, 0.12);
    .card-icon { color: rgba(139, 92, 246, 0.85); }
  }

  &.icon-aperture {
    background: rgba(6, 182, 212, 0.12);
    .card-icon { color: rgba(6, 182, 212, 0.85); }
  }

  &.icon-shield {
    background: rgba(236, 72, 153, 0.12);
    .card-icon { color: rgba(236, 72, 153, 0.85); }
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
  &.icon-lightbulb { background: rgba(99, 102, 241, 0.18); }
  &.icon-search { background: rgba(245, 158, 11, 0.18); }
  &.icon-code { background: rgba(16, 185, 129, 0.18); }
  &.icon-cpu { background: rgba(239, 68, 68, 0.18); }
  &.icon-globe { background: rgba(139, 92, 246, 0.18); }
  &.icon-aperture { background: rgba(6, 182, 212, 0.18); }
  &.icon-shield { background: rgba(236, 72, 153, 0.18); }
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

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(71, 85, 105, 0.3);
    border-top-color: rgba(99, 102, 241, 0.8);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  p {
    font-size: 14px;
    color: rgba(148, 163, 184, 0.7);
  }
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
    color: rgba(148, 163, 184, 0.3);
  }

  p {
    font-size: 14px;
    color: rgba(148, 163, 184, 0.6);
    margin: 0;
  }

  .empty-hint {
    font-size: 13px;
    color: rgba(148, 163, 184, 0.4);
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

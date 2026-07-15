<template>
  <div class="classroom">
    <!-- 正在直播 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">
          <component :is="icons.Video" class="title-icon" />
          正在直播
        </h2>
        <span class="live-count">{{ liveClasses.length }} 个课堂正在进行</span>
      </div>

      <div class="live-grid">
        <div v-for="liveClass in liveClasses" :key="liveClass.id" class="live-card">
          <div class="live-header">
            <div class="live-indicator">
              <span class="pulse-dot"></span>
              <span class="live-text">直播中</span>
            </div>
            <div class="student-count">
              <component :is="icons.Users" class="count-icon" />
              <span>{{ liveClass.students }}</span>
            </div>
          </div>

          <div class="live-body">
            <div class="subject-badge" :style="{ background: liveClass.color }">
              {{ liveClass.subject }}
            </div>
            <h3 class="class-title">{{ liveClass.title }}</h3>
            <div class="teacher-info">
              <div class="teacher-avatar" :style="{ background: liveClass.color }">
                <component :is="icons.User" class="avatar-icon" />
              </div>
              <span class="teacher-name">{{ liveClass.teacher }}</span>
            </div>
          </div>

          <button class="enter-btn" @click="enterClass(liveClass.id)">
            <component :is="icons.Play" class="btn-icon" />
            进入课堂
          </button>
        </div>
      </div>
    </div>

    <!-- 即将开始 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">
          <component :is="icons.Calendar" class="title-icon" />
          即将开始
        </h2>
        <span class="upcoming-count">{{ upcomingClasses.length }} 节课程待开始</span>
      </div>

      <div class="upcoming-list">
        <div v-for="upcoming in upcomingClasses" :key="upcoming.id" class="upcoming-card">
          <div class="upcoming-left">
            <div class="date-badge" :style="{ background: upcoming.color }">
              <div class="date-day">{{ upcoming.day }}</div>
              <div class="date-month">{{ upcoming.month }}</div>
            </div>
          </div>

          <div class="upcoming-center">
            <div class="upcoming-header">
              <h3 class="upcoming-title">{{ upcoming.title }}</h3>
              <span class="subject-tag" :style="{ background: upcoming.color }">
                {{ upcoming.subject }}
              </span>
            </div>

            <div class="upcoming-meta">
              <div class="meta-item">
                <component :is="icons.Clock" class="meta-icon" />
                <span>{{ upcoming.time }}</span>
              </div>
              <div class="meta-item">
                <component :is="icons.User" class="meta-icon" />
                <span>{{ upcoming.teacher }}</span>
              </div>
            </div>
          </div>

          <div class="upcoming-right">
            <button class="reserve-btn" @click="reserveClass(upcoming.id)">
              预约
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的课程 -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">
          <component :is="icons.BookOpen" class="title-icon" />
          我的课程
        </h2>
        <span class="course-count">共 {{ myCourses.length }} 门课程</span>
      </div>

      <div class="courses-grid">
        <div v-for="course in myCourses" :key="course.id" class="course-card">
          <div class="course-header">
            <div class="course-icon" :style="{ background: course.color }">
              <component :is="icons.BookOpen" class="icon" />
            </div>
            <div class="course-info">
              <h3 class="course-title">{{ course.title }}</h3>
              <p class="course-teacher">{{ course.teacher }}</p>
            </div>
          </div>

          <div class="course-progress">
            <div class="progress-header">
              <span class="progress-label">学习进度</span>
              <span class="progress-value">{{ course.progress }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: course.progress + '%', background: course.color }"
              ></div>
            </div>
          </div>

          <div class="course-footer">
            <div class="stat-item">
              <span class="stat-label">已完成</span>
              <span class="stat-value">{{ course.completedLessons }}</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-label">总课时</span>
              <span class="stat-value">{{ course.totalLessons }}</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-label">学习时长</span>
              <span class="stat-value">{{ course.hours }}h</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Video, Calendar, Users, Clock, Play, BookOpen, User } from 'lucide-vue-next'

const icons = {
  Video,
  Calendar,
  Users,
  Clock,
  Play,
  BookOpen,
  User
}

// 正在直播的课程
const liveClasses = ref([
  {
    id: 1,
    title: '高三数学冲刺班 - 函数与导数',
    subject: '数学',
    teacher: '王老师',
    students: 156,
    color: 'linear-gradient(135deg, #3b82f6, #2563eb)'
  },
  {
    id: 2,
    title: '英语口语强化训练 - 日常对话',
    subject: '英语',
    teacher: '李老师',
    students: 89,
    color: 'linear-gradient(135deg, #10b981, #059669)'
  },
  {
    id: 3,
    title: '物理实验专题 - 力学综合',
    subject: '物理',
    teacher: '张老师',
    students: 124,
    color: 'linear-gradient(135deg, #f59e0b, #d97706)'
  }
])

// 即将开始的课程
const upcomingClasses = ref([
  {
    id: 1,
    title: '化学有机合成专题',
    subject: '化学',
    teacher: '刘老师',
    day: '12',
    month: '7月',
    time: '14:00 - 16:00',
    color: 'linear-gradient(135deg, #ef4444, #dc2626)'
  },
  {
    id: 2,
    title: '数学概率统计精讲',
    subject: '数学',
    teacher: '陈老师',
    day: '13',
    month: '7月',
    time: '09:00 - 11:00',
    color: 'linear-gradient(135deg, #8b5cf6, #7c3aed)'
  },
  {
    id: 3,
    title: '英语阅读理解技巧',
    subject: '英语',
    teacher: '赵老师',
    day: '14',
    month: '7月',
    time: '15:30 - 17:30',
    color: 'linear-gradient(135deg, #06b6d4, #0891b2)'
  },
  {
    id: 4,
    title: '物理电磁学进阶',
    subject: '物理',
    teacher: '孙老师',
    day: '15',
    month: '7月',
    time: '10:00 - 12:00',
    color: 'linear-gradient(135deg, #f97316, #ea580c)'
  }
])

// 我的课程
const myCourses = ref([
  {
    id: 1,
    title: '高中数学系统复习',
    teacher: '王老师',
    progress: 75,
    completedLessons: 30,
    totalLessons: 40,
    hours: 24,
    color: 'linear-gradient(135deg, #3b82f6, #2563eb)'
  },
  {
    id: 2,
    title: '英语能力提升计划',
    teacher: '李老师',
    progress: 60,
    completedLessons: 18,
    totalLessons: 30,
    hours: 16,
    color: 'linear-gradient(135deg, #10b981, #059669)'
  },
  {
    id: 3,
    title: '物理核心概念精讲',
    teacher: '张老师',
    progress: 45,
    completedLessons: 9,
    totalLessons: 20,
    hours: 12,
    color: 'linear-gradient(135deg, #f59e0b, #d97706)'
  },
  {
    id: 4,
    title: '化学基础与实验',
    teacher: '刘老师',
    progress: 30,
    completedLessons: 6,
    totalLessons: 20,
    hours: 8,
    color: 'linear-gradient(135deg, #ef4444, #dc2626)'
  }
])

const enterClass = (classId: number) => {
  console.log('进入课堂:', classId)
  // TODO: 实现进入课堂逻辑
}

const reserveClass = (classId: number) => {
  console.log('预约课程:', classId)
  // TODO: 实现预约逻辑
}
</script>

<style lang="scss" scoped>
.classroom {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-normal);

  &:hover {
    border-color: rgba(99, 102, 241, 0.3);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  }
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

.live-count,
.upcoming-count,
.course-count {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 4px 12px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

// 正在直播
.live-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 24px;
}

.live-card {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  padding: 20px;
  transition: all var(--transition-normal);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  &:hover {
    background: linear-gradient(145deg, rgba(40, 54, 71, 0.98), rgba(26, 37, 52, 0.99));
    border-color: rgba(99, 102, 241, 0.5);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  }
}

.live-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.live-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: var(--error-color);
  border-radius: 50%;
  position: relative;
  animation: pulse 2s infinite;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: var(--error-color);
    border-radius: 50%;
    animation: pulse-ring 2s infinite;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

@keyframes pulse-ring {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

.live-text {
  font-size: 12px;
  color: var(--error-color);
  font-weight: 600;
}

.student-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);

  .count-icon {
    width: 16px;
    height: 16px;
  }
}

.live-body {
  margin-bottom: 20px;
}

.subject-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.class-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.teacher-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.teacher-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

  .avatar-icon {
    width: 20px;
    height: 20px;
    color: var(--text-primary);
  }
}

.teacher-name {
  font-size: 14px;
  color: var(--text-secondary);
}

.enter-btn {
  width: 100%;
  height: 44px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border: none;
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all var(--transition-normal);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  .btn-icon {
    width: 18px;
    height: 18px;
  }
}

// 即将开始
.upcoming-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
}

.upcoming-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all var(--transition-normal);

  &:hover {
    background: var(--bg-tertiary);
    border-color: var(--primary-color);
    transform: translateX(4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  }
}

.upcoming-left {
  flex-shrink: 0;
}

.date-badge {
  width: 70px;
  height: 70px;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.date-day {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

.date-month {
  font-size: 12px;
  font-weight: 500;
  margin-top: 4px;
}

.upcoming-center {
  flex: 1;
  min-width: 0;
}

.upcoming-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.upcoming-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.subject-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.upcoming-meta {
  display: flex;
  align-items: center;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);

  .meta-icon {
    width: 16px;
    height: 16px;
  }
}

.upcoming-right {
  flex-shrink: 0;
}

.reserve-btn {
  padding: 10px 24px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: var(--radius-md);
  color: var(--primary-color);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);

  &:hover {
    background: rgba(99, 102, 241, 0.2);
    border-color: var(--primary-light);
    color: var(--primary-light);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
}

// 我的课程
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 24px;
}

.course-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  transition: all var(--transition-normal);

  &:hover {
    background: var(--bg-tertiary);
    border-color: var(--primary-color);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  }
}

.course-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.course-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

  .icon {
    width: 24px;
    height: 24px;
    color: var(--text-primary);
  }
}

.course-info {
  flex: 1;
  min-width: 0;

  .course-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 4px 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .course-teacher {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 0;
  }
}

.course-progress {
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.progress-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.course-footer {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-divider {
  width: 1px;
  height: 30px;
  background: var(--border-color);
}

// 响应式设计
@media (max-width: 1024px) {
  .live-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }

  .courses-grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  }
}

@media (max-width: 768px) {
  .classroom {
    gap: 24px;
  }

  .section-header {
    padding: 16px 20px;
  }

  .section-title {
    font-size: 16px;

    .title-icon {
      width: 20px;
      height: 20px;
    }
  }

  .live-grid,
  .courses-grid {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .upcoming-list {
    padding: 16px;
  }

  .upcoming-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;

    .upcoming-right {
      width: 100%;

      .reserve-btn {
        width: 100%;
      }
    }
  }

  .date-badge {
    width: 60px;
    height: 60px;

    .date-day {
      font-size: 20px;
    }
  }
}
</style>

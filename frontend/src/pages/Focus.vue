<template>
  <div class="focus-container">
    <div v-if="isFullscreen && isRunning" class="focus-overlay">
      <div class="overlay-content">
        <component :is="icons.Shield" class="overlay-icon" />
        <div class="overlay-text">专注模式中</div>
        <div class="overlay-timer">{{ formattedTime }}</div>
        <div class="overlay-subject" v-if="focusSubject">{{ focusSubject }}</div>
        <div class="overlay-hint">按 Ctrl+Shift+E 退出专注</div>
      </div>
    </div>

    <div class="focus-content" :class="{ 'fullscreen-active': isFullscreen }">
      <div class="focus-header">
        <div class="header-left">
          <h2>专注学习</h2>
          <p class="header-desc">番茄钟专注计时与每日打卡</p>
        </div>
      </div>

      <div class="focus-main">
        <div class="timer-section">
          <div class="timer-card">
            <div class="timer-card-header">
              <button class="fullscreen-btn" @click="toggleFullscreen">
                <component :is="isFullscreen ? icons.Shrink : icons.Maximize" />
              </button>
            </div>
            <div class="mode-tabs">
              <button
                v-for="m in modes"
                :key="m.id"
                class="mode-tab"
                :class="{ active: currentMode === m.id }"
                @click="switchMode(m.id)"
              >
                {{ m.label }}
              </button>
            </div>

            <div v-if="currentMode === 'custom'" class="custom-input">
              <label>自定义时长（分钟）</label>
              <input type="number" v-model="customMinutes" min="1" max="120" @change="applyCustomTime" />
            </div>

            <div class="timer-circle-wrapper">
              <svg class="timer-svg" viewBox="0 0 200 200">
                <circle class="timer-bg" cx="100" cy="100" r="90" />
                <circle
                  class="timer-progress"
                  cx="100"
                  cy="100"
                  r="90"
                  :stroke-dasharray="circumference"
                  :stroke-dashoffset="dashOffset"
                  :class="{ running: isRunning }"
                />
              </svg>
              <div class="timer-display">
                <div class="timer-time">{{ formattedTime }}</div>
                <div class="timer-label">{{ isRunning ? '专注中...' : isPaused ? '已暂停' : '准备开始' }}</div>
              </div>
            </div>

            <div class="timer-controls">
              <button v-if="!isRunning && !isPaused" class="ctrl-btn start" @click="startTimer">
                <component :is="icons.Play" />
                <span>开始专注</span>
              </button>
              <button v-if="isRunning" class="ctrl-btn pause" @click="pauseTimer">
                <component :is="icons.Pause" />
                <span>暂停</span>
              </button>
              <button v-if="isPaused" class="ctrl-btn resume" @click="resumeTimer">
                <component :is="icons.Play" />
                <span>继续</span>
              </button>
              <button v-if="isRunning || isPaused" class="ctrl-btn stop" @click="handleStop">
                <component :is="icons.Square" />
                <span>结束</span>
              </button>
            </div>

            <div class="subject-select-wrapper">
              <label>学习章节</label>
              <select v-model="focusSubject">
                <option value="">选择章节</option>
                <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
          </div>

          <div class="checkin-card">
            <div class="checkin-header">
              <h3>今日打卡</h3>
              <span class="checkin-date">{{ todayStr }}</span>
            </div>
            <div class="checkin-body">
              <div class="checkin-status" :class="{ checked: todayChecked }">
                <component :is="todayChecked ? icons.CheckCircle : icons.Circle" />
                <span>{{ todayChecked ? '今日已打卡' : '今日未打卡' }}</span>
              </div>
              <button class="checkin-btn" :class="{ disabled: todayChecked }" :disabled="todayChecked" @click="doCheckin">
                {{ todayChecked ? '已完成' : '打卡' }}
              </button>
            </div>
            <div class="checkin-streak">
              <div class="streak-item">
                <span class="streak-value">{{ streakDays }}</span>
                <span class="streak-label">连续打卡</span>
              </div>
              <div class="streak-item">
                <span class="streak-value">{{ totalCheckins }}</span>
                <span class="streak-label">累计打卡</span>
              </div>
            </div>
          </div>
        </div>

        <div class="stats-section">
          <div class="stats-row">
            <div class="stat-card">
              <div class="stat-icon blue"><component :is="icons.Clock" /></div>
              <div>
                <div class="stat-value">{{ todayMinutes }}<span class="unit">分钟</span></div>
                <div class="stat-label">今日专注</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon green"><component :is="icons.Target" /></div>
              <div>
                <div class="stat-value">{{ todaySessions }}</div>
                <div class="stat-label">专注次数</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon orange"><component :is="icons.Flame" /></div>
              <div>
                <div class="stat-value">{{ streakDays }}</div>
                <div class="stat-label">连续天数</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon purple"><component :is="icons.Award" /></div>
              <div>
                <div class="stat-value">{{ totalMinutes }}<span class="unit">分钟</span></div>
                <div class="stat-label">累计专注</div>
              </div>
            </div>
          </div>

          <div class="chart-card">
            <h3>本周专注时长</h3>
            <div class="bar-chart">
              <div v-for="day in weekDays" :key="day.label" class="bar-item">
                <div class="bar-wrapper">
                  <div class="bar-fill" :style="{ height: getBarHeight(day.minutes) + '%' }" :class="{ today: day.isToday }"></div>
                </div>
                <span class="bar-label" :class="{ today: day.isToday }">{{ day.label }}</span>
                <span class="bar-value">{{ day.minutes }}m</span>
              </div>
            </div>
          </div>

          <div class="history-card">
            <h3>最近专注记录</h3>
            <div class="history-list">
              <div v-if="history.length === 0" class="history-empty">
                <component :is="icons.Clock" />
                <span>暂无专注记录</span>
              </div>
              <div v-for="(item, idx) in history" :key="idx" class="history-item">
                <div class="history-dot" :style="{ background: getSubjectColor(item.subject) }"></div>
                <div class="history-info">
                  <div class="history-subject">{{ item.subject || '未选择科目' }}</div>
                  <div class="history-time">{{ item.date }}</div>
                </div>
                <div class="history-duration">{{ item.minutes }} 分钟</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showExitModal" class="modal-overlay" @click.self="showExitModal = false">
      <div class="exit-modal">
        <component :is="icons.AlertTriangle" class="modal-icon" />
        <h3>确定要结束专注吗？</h3>
        <p>当前专注时长为 {{ Math.round((totalSeconds - remainingSeconds) / 60) }} 分钟，结束后将记录本次专注。</p>
        <div class="modal-actions">
          <button class="modal-btn cancel" @click="showExitModal = false">继续专注</button>
          <button class="modal-btn confirm" @click="confirmStop">确定结束</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Play, Pause, Square, Clock, Target, Flame, Award,
  CheckCircle, Circle, Maximize, Shrink, Shield, AlertTriangle
} from 'lucide-vue-next'

const icons = { Play, Pause, Square, Clock, Target, Flame, Award, CheckCircle, Circle, Maximize, Shrink, Shield, AlertTriangle }

const modes = [
  { id: 'pomodoro', label: '番茄钟', minutes: 25 },
  { id: 'short', label: '短专注', minutes: 15 },
  { id: 'long', label: '长专注', minutes: 45 },
  { id: 'custom', label: '自定义', minutes: 30 }
]

const currentMode = ref('pomodoro')
const totalSeconds = ref(25 * 60)
const remainingSeconds = ref(25 * 60)
const isRunning = ref(false)
const isPaused = ref(false)
const focusSubject = ref('')
const isFullscreen = ref(false)
const showExitModal = ref(false)
let timerInterval: ReturnType<typeof setInterval> | null = null

const customMinutes = ref(30)

function applyCustomTime() {
  const val = parseInt(customMinutes.value.toString()) || 30
  customMinutes.value = Math.min(Math.max(val, 1), 120)
  totalSeconds.value = customMinutes.value * 60
  remainingSeconds.value = customMinutes.value * 60
}

const subjects = ['人工智能概述', '搜索与推理', '机器学习', '深度学习', '自然语言处理', '计算机视觉', '人工智能伦理']
const circumference = 2 * Math.PI * 90

const dashOffset = computed(() => {
  const progress = remainingSeconds.value / totalSeconds.value
  return circumference * (1 - progress)
})

const formattedTime = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60)
  const s = remainingSeconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

function switchMode(modeId: string) {
  if (isRunning.value) return
  currentMode.value = modeId
  const mode = modes.find(m => m.id === modeId)
  if (mode) {
    totalSeconds.value = mode.minutes * 60
    remainingSeconds.value = mode.minutes * 60
  }
}

function startTimer() {
  isRunning.value = true
  isPaused.value = false
  timerInterval = setInterval(() => {
    remainingSeconds.value--
    if (remainingSeconds.value <= 0) {
      completeTimer()
    }
  }, 1000)
}

function pauseTimer() {
  isRunning.value = false
  isPaused.value = true
  if (timerInterval) clearInterval(timerInterval)
}

function resumeTimer() {
  isRunning.value = true
  isPaused.value = false
  timerInterval = setInterval(() => {
    remainingSeconds.value--
    if (remainingSeconds.value <= 0) {
      completeTimer()
    }
  }, 1000)
}

function handleStop() {
  showExitModal.value = true
}

function confirmStop() {
  showExitModal.value = false
  stopTimer()
}

function stopTimer() {
  isRunning.value = false
  isPaused.value = false
  if (timerInterval) clearInterval(timerInterval)
  const elapsed = totalSeconds.value - remainingSeconds.value
  if (elapsed > 30) {
    recordSession(Math.round(elapsed / 60))
  }
  remainingSeconds.value = totalSeconds.value
  if (isFullscreen.value) {
    exitFullscreen()
  }
}

function completeTimer() {
  isRunning.value = false
  isPaused.value = false
  if (timerInterval) clearInterval(timerInterval)
  recordSession(Math.round(totalSeconds.value / 60))
  remainingSeconds.value = totalSeconds.value
}

function toggleFullscreen() {
  if (isFullscreen.value) {
    exitFullscreen()
  } else {
    enterFullscreen()
  }
}

function enterFullscreen() {
  const elem = document.documentElement
  if (elem.requestFullscreen) {
    elem.requestFullscreen()
  } else if ((elem as any).webkitRequestFullscreen) {
    (elem as any).webkitRequestFullscreen()
  } else if ((elem as any).msRequestFullscreen) {
    (elem as any).msRequestFullscreen()
  }
}

function exitFullscreen() {
  if (document.exitFullscreen) {
    document.exitFullscreen()
  } else if ((document as any).webkitExitFullscreen) {
    (document as any).webkitExitFullscreen()
  } else if ((document as any).msExitFullscreen) {
    (document as any).msExitFullscreen()
  }
}

function handleFullscreenChange() {
  isFullscreen.value = !!(document.fullscreenElement || (document as any).webkitFullscreenElement || (document as any).msFullscreenElement)
}

function handleKeydown(e: KeyboardEvent) {
  if (isRunning.value && isFullscreen.value && e.ctrlKey && e.shiftKey && e.key === 'E') {
    e.preventDefault()
    handleStop()
  }
  if ((e.key === 'Escape') && isFullscreen.value && isRunning.value) {
    e.preventDefault()
    handleStop()
  }
}

const todayStr = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
})

const todayChecked = ref(false)
const streakDays = ref(3)
const totalCheckins = ref(12)

function doCheckin() {
  todayChecked.value = true
  totalCheckins.value++
  streakDays.value++
}

const todayMinutes = ref(45)
const todaySessions = ref(2)
const totalMinutes = ref(380)

const weekDays = computed(() => {
  const days = ['一', '二', '三', '四', '五', '六', '日']
  const data = [30, 45, 0, 60, 25, todayMinutes.value, 0]
  const today = new Date().getDay()
  const todayIdx = today === 0 ? 6 : today - 1
  return days.map((label, i) => ({
    label,
    minutes: data[i],
    isToday: i === todayIdx
  }))
})

const maxWeekMinutes = computed(() => Math.max(...weekDays.value.map(d => d.minutes), 60))

function getBarHeight(minutes: number): number {
  return (minutes / maxWeekMinutes.value) * 100
}

interface HistoryItem {
  subject: string
  date: string
  minutes: number
}

const history = ref<HistoryItem[]>([
  { subject: '机器学习', date: '今天 14:30', minutes: 25 },
  { subject: '人工智能概述', date: '今天 10:15', minutes: 20 },
  { subject: '搜索与推理', date: '昨天 16:00', minutes: 45 },
  { subject: '深度学习', date: '昨天 09:30', minutes: 30 },
  { subject: '自然语言处理', date: '2天前 15:00', minutes: 25 }
])

function recordSession(minutes: number) {
  const now = new Date()
  const timeStr = `今天 ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  history.value.unshift({
    subject: focusSubject.value,
    date: timeStr,
    minutes
  })
  todayMinutes.value += minutes
  todaySessions.value++
  totalMinutes.value += minutes
}

function getSubjectColor(subject: string): string {
  const map: Record<string, string> = {
    '人工智能概述': '#3b82f6',
    '搜索与推理': '#f59e0b',
    '机器学习': '#10b981',
    '深度学习': '#ef4444',
    '自然语言处理': '#8b5cf6',
    '计算机视觉': '#06b6d4',
    '人工智能伦理': '#ec4899'
  }
  return map[subject] || '#64748b'
}

onMounted(() => {
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
  document.removeEventListener('keydown', handleKeydown)
  if (isFullscreen.value) {
    exitFullscreen()
  }
})
</script>

<style lang="scss" scoped>
.focus-container {
  position: relative;
  min-height: 100%;
}

.focus-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.95);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;

  .overlay-content {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  .overlay-icon {
    width: 64px;
    height: 64px;
    color: var(--primary-color);
    animation: pulse 2s ease-in-out infinite;
  }

  .overlay-text {
    font-size: 24px;
    font-weight: 700;
    color: white;
  }

  .overlay-timer {
    font-size: 72px;
    font-weight: 700;
    color: var(--primary-color);
    font-variant-numeric: tabular-nums;
    line-height: 1;
    letter-spacing: -2px;
    margin: 10px 0;
  }

  .overlay-subject {
    font-size: 18px;
    color: var(--text-secondary);
    padding: 6px 20px;
    background: rgba(99, 102, 241, 0.15);
    border-radius: 20px;
    border: 1px solid rgba(99, 102, 241, 0.3);
  }

  .overlay-hint {
    font-size: 14px;
    color: var(--text-muted);
    margin-top: 8px;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.05); }
}

.focus-content {
  padding-bottom: 20px;

  &.fullscreen-active {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow-y: auto;
    z-index: 1000;
    background: var(--bg-primary);
    padding: 24px;
  }
}

.focus-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;

  .header-left {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .header-left h2 {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
    text-shadow: 
      0 0 20px rgba(99, 102, 241, 0.4),
      0 2px 4px rgba(0, 0, 0, 0.3);
    position: relative;
    padding-bottom: 8px;

    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 60px;
      height: 3px;
      background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
      border-radius: 2px;
    }
  }

  .header-desc {
    font-size: 14px;
    color: #94a3b8;
    margin: 0;
    font-weight: 400;
  }

}

.focus-main {
  display: flex;
  gap: 20px;

  @media (max-width: 1200px) {
    flex-direction: column;
  }
}

.timer-section {
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex-shrink: 0;

  @media (max-width: 1200px) {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;

    .timer-card, .checkin-card {
      flex: 1;
      min-width: 300px;
      max-width: 400px;
    }
  }
}

.timer-card {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.timer-card-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;

  .fullscreen-btn {
    width: 36px;
    height: 36px;
    background: linear-gradient(145deg, #273548, #1e293b);
    border: 2px solid rgba(71, 85, 105, 0.8);
    border-radius: var(--radius-sm);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);

    &:hover {
      background: linear-gradient(145deg, #334155, #273548);
      border-color: var(--primary-color);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2), 0 0 0 1px var(--primary-color);
    }

    svg {
      width: 18px;
      height: 18px;
      color: #cbd5e1;
    }
  }
}

.mode-tabs {
  display: flex;
  gap: 8px;

  .mode-tab {
    flex: 1;
    padding: 10px 0;
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 2px solid rgba(71, 85, 105, 0.6);
    border-radius: var(--radius-md);
    color: #94a3b8;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);

    &:hover { 
      border-color: #60a5fa; 
      color: #e2e8f0; 
      background: linear-gradient(145deg, #273548, #1e293b);
    }
    &.active {
      background: linear-gradient(145deg, rgba(99, 102, 241, 0.2), rgba(79, 70, 229, 0.15));
      border-color: #6366f1;
      color: #a5b4fc;
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
  }
}

.custom-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  background: linear-gradient(145deg, rgba(99, 102, 241, 0.12), rgba(79, 70, 229, 0.08));
  border: 2px solid rgba(99, 102, 241, 0.3);
  border-radius: var(--radius-md);

  label {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 600;
  }

  input {
    padding: 10px 14px;
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 2px solid rgba(71, 85, 105, 0.7);
    border-radius: var(--radius-md);
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 700;
    text-align: center;
    height: 42px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);

    &:focus {
      outline: none;
      border-color: #6366f1;
      box-shadow: 0 0 0 1px #6366f1, inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
  }
}

.timer-circle-wrapper {
  position: relative;
  width: 220px;
  height: 220px;
  margin: 0 auto;
}

.timer-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.timer-bg { fill: none; stroke: var(--bg-tertiary); stroke-width: 6; }

.timer-progress {
  fill: none;
  stroke: var(--primary-color);
  stroke-width: 6;
  stroke-linecap: round;
  transition: stroke-dashoffset 1s linear;

  &.running {
    animation: pulse-ring 2s ease-in-out infinite;
  }
}

@keyframes pulse-ring {
  0%, 100% { filter: drop-shadow(0 0 4px rgba(99, 102, 241, 0.3)); }
  50% { filter: drop-shadow(0 0 12px rgba(99, 102, 241, 0.6)); }
}

.timer-display {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;

  .timer-time {
    font-size: 52px;
    font-weight: 800;
    color: #ffffff;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    text-shadow: 
      0 0 30px rgba(99, 102, 241, 0.5),
      0 2px 4px rgba(0, 0, 0, 0.3);
  }

  .timer-label {
    font-size: 14px;
    color: #94a3b8;
    margin-top: 10px;
    font-weight: 500;
  }
}

.timer-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.ctrl-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

  svg { width: 18px; height: 18px; }

  &.start { 
    background: linear-gradient(145deg, #6366f1, #4f46e5); 
    color: white; 
    &:hover { 
      background: linear-gradient(145deg, #4f46e5, #4338ca); 
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
      transform: translateY(-1px);
    }
  }
  
  &.pause { 
    background: linear-gradient(145deg, #f59e0b, #d97706); 
    color: white; 
    &:hover { 
      background: linear-gradient(145deg, #d97706, #b45309);
      box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    }
  }
  
  &.resume { 
    background: linear-gradient(145deg, #6366f1, #4f46e5); 
    color: white; 
    &:hover { 
      background: linear-gradient(145deg, #4f46e5, #4338ca); 
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
  }
  
  &.stop {
    background: linear-gradient(145deg, #273548, #1e293b);
    color: #cbd5e1;
    border: 2px solid rgba(71, 85, 105, 0.8);
    &:hover { 
      background: linear-gradient(145deg, #334155, #273548); 
      color: #e2e8f0;
      border-color: #60a5fa;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2), 0 0 0 1px #60a5fa;
    }
  }
}

.subject-select-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 600;
  }

  select {
    padding: 10px 14px;
    background: linear-gradient(145deg, #273548, #1e293b);
    border: 2px solid rgba(71, 85, 105, 0.8);
    border-radius: var(--radius-md);
    color: #e2e8f0;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    height: 42px;
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

.checkin-card {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.checkin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;

  h3 {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .checkin-date { font-size: 12px; color: var(--text-muted); }
}

.checkin-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;

  .checkin-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--text-muted);

    svg { width: 20px; height: 20px; }

    &.checked { color: var(--success-color); }
  }

  .checkin-btn {
    padding: 8px 24px;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;

    &:hover { background: var(--primary-dark); }
    &.disabled {
      background: var(--bg-tertiary);
      color: var(--text-muted);
      cursor: default;
      &:hover { background: var(--bg-tertiary); }
    }
  }
}

.checkin-streak {
  display: flex;
  gap: 16px;

  .streak-item {
    flex: 1;
    text-align: center;
    padding: 14px;
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid rgba(71, 85, 105, 0.4);
    border-radius: var(--radius-md);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);

    .streak-value {
      display: block;
      font-size: 28px;
      font-weight: 800;
      color: #6366f1;
      text-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
    }

    .streak-label { font-size: 12px; color: #94a3b8; }
  }
}

.stats-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;

  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  }

  .stat-icon {
    width: 52px;
    height: 52px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);

    &.blue { background: linear-gradient(145deg, rgba(99, 102, 241, 0.2), rgba(79, 70, 229, 0.1)); svg { color: #818cf8; }}
    &.green { background: linear-gradient(145deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1)); svg { color: #34d399; }}
    &.orange { background: linear-gradient(145deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.1)); svg { color: #fbbf24; }}
    &.purple { background: linear-gradient(145deg, rgba(139, 92, 246, 0.2), rgba(126, 34, 206, 0.1)); svg { color: #c084fc; }}

    svg { width: 26px; height: 26px; }
  }

  .stat-value {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.2;
    text-align: center;

    .unit {
      font-size: 12px;
      font-weight: 600;
      color: #94a3b8;
      margin-left: 3px;
    }
  }

  .stat-label { font-size: 12px; color: #94a3b8; font-weight: 500; text-align: center; line-height: 1.4; }
}

.chart-card {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  h3 {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 16px 0;
  }
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 160px;
  gap: 8px;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  height: 100%;
  justify-content: flex-end;
}

.bar-wrapper {
  width: 100%;
  max-width: 36px;
  height: 120px;
  background: var(--bg-tertiary);
  border-radius: 6px 6px 0 0;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(180deg, var(--primary-color), var(--primary-light));
  border-radius: 6px 6px 0 0;
  transition: height 0.5s;
  min-height: 0;

  &.today { background: linear-gradient(180deg, #10b981, #34d399); }
}

.bar-label { font-size: 12px; color: var(--text-muted); &.today { color: var(--success-color); font-weight: 600; }}
.bar-value { font-size: 11px; color: var(--text-muted); }

.history-card {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.95), rgba(26, 37, 52, 0.98));
  border: 2px solid rgba(71, 85, 105, 0.7);
  border-radius: var(--radius-lg);
  padding: 20px;
  flex: 1;
  min-height: 200px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);

  h3 {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 16px 0;
  }
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-empty {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px;
  color: var(--text-muted);
  font-size: 13px;

  svg { width: 20px; height: 20px; opacity: 0.5; }
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border: 1px solid rgba(71, 85, 105, 0.4);
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);

  &:hover { 
    background: linear-gradient(145deg, #273548, #1e293b);
    border-color: rgba(99, 102, 241, 0.4);
    transform: translateX(4px);
  }

  .history-dot { 
    width: 12px; 
    height: 12px; 
    border-radius: 50%; 
    flex-shrink: 0;
    box-shadow: 0 0 8px currentColor;
  }

  .history-info {
    flex: 1;
    min-width: 0;

    .history-subject { font-size: 14px; font-weight: 600; color: #e2e8f0; }
    .history-time { font-size: 12px; color: #94a3b8; }
  }

  .history-duration { font-size: 14px; font-weight: 700; color: #6366f1; flex-shrink: 0; }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  z-index: 20000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s;
  backdrop-filter: blur(8px);
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; }}

.exit-modal {
  background: linear-gradient(145deg, rgba(40, 54, 71, 0.98), rgba(26, 37, 52, 0.99));
  border: 2px solid rgba(71, 85, 105, 0.8);
  border-radius: var(--radius-lg);
  padding: 32px;
  width: 420px;
  text-align: center;
  animation: slideUp 0.3s;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); }}

.modal-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: rgba(245, 158, 11, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f59e0b;
}

.exit-modal h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.exit-modal p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.modal-btn {
  padding: 10px 28px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;

  &.cancel {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
    &:hover { background: var(--bg-card); color: var(--text-primary); }
  }

  &.confirm {
    background: var(--primary-color);
    color: white;
    &:hover { background: var(--primary-dark); }
  }
}
</style>
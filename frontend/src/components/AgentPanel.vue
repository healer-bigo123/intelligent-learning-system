<template>
  <div class="agent-panel">
    <div class="panel-header">
      <h2 class="panel-title">
        <component :is="icons.Bot" class="icon" />
        智能体列表
      </h2>
    </div>
    <div class="agent-list">
      <div
        v-for="agent in agents"
        :key="agent.id"
        class="agent-item"
        :class="{ active: selectedAgent?.id === agent.id, disabled: agent.status === 'inactive' }"
        @click="selectAgent(agent)"
      >
        <div class="agent-icon" :style="{ background: agent.color }">
          <component :is="getIcon(agent.icon)" class="icon" />
        </div>
        <div class="agent-info">
          <div class="agent-name">{{ agent.name }}</div>
          <div class="agent-status" :class="agent.status">
            <span class="status-dot"></span>
            {{ getStatusText(agent.status) }}
          </div>
        </div>
        <div class="agent-model-tag" v-if="agent.selectedModel">
          {{ getModelName(agent.selectedModel) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type Component } from 'vue'
import { Bot, HelpCircle, Calendar, CheckSquare, Heart, Star, BarChart } from 'lucide-vue-next'
import type { AgentInfo, ModelInfo } from '@/types'

const props = defineProps<{
  agents: AgentInfo[]
  selectedAgent: AgentInfo | null
  models: ModelInfo[]
}>()

const emit = defineEmits<{
  (e: 'select', agent: AgentInfo): void
}>()

const icons = { Bot, HelpCircle, Calendar, CheckSquare, Heart, Star, BarChart }

const iconMap: Record<string, Component> = {
  HelpCircle,
  Calendar,
  CheckSquare,
  Heart,
  Star,
  BarChart
}

const getIcon = (iconName: string): Component => {
  return iconMap[iconName] || HelpCircle
}

const selectAgent = (agent: AgentInfo) => {
  if (agent.status !== 'inactive') {
    emit('select', agent)
  }
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    active: '在线',
    inactive: '离线',
    loading: '加载中'
  }
  return statusMap[status] || status
}

const getModelName = (modelId: string): string => {
  const model = props.models.find(m => m.id === modelId)
  return model?.name.split(' ')[0] || modelId
}
</script>

<style lang="scss" scoped>
@import '@/style/index.scss';

.agent-panel {
  background: $bg-card;
  border-radius: $radius-lg;
  border: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid $border-color;
  
  .panel-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
    color: $text-primary;
    
    .icon {
      width: 24px;
      height: 24px;
      color: $primary-color;
    }
  }
}

.agent-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.agent-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all $transition-fast;
  margin-bottom: 8px;
  border: 1px solid transparent;
  
  &:hover:not(.disabled) {
    background: $bg-hover;
    transform: translateX(4px);
  }
  
  &.active {
    background: rgba(99, 102, 241, 0.15);
    border-color: $primary-color;
  }
  
  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.agent-icon {
  width: 44px;
  height: 44px;
  border-radius: $radius-md;
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

.agent-info {
  flex: 1;
  min-width: 0;
  
  .agent-name {
    font-size: 15px;
    font-weight: 500;
    color: $text-primary;
    margin-bottom: 4px;
  }
  
  .agent-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }
    
    &.active .status-dot {
      background: $success-color;
      box-shadow: 0 0 8px $success-color;
    }
    
    &.inactive .status-dot {
      background: $text-muted;
    }
    
    &.loading .status-dot {
      background: $warning-color;
      animation: pulse 1s infinite;
    }
  }
}

.agent-model-tag {
  background: $bg-tertiary;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  color: $text-secondary;
  flex-shrink: 0;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
<template>
  <div class="model-selector">
    <div class="selector-header">
      <component :is="icons.Cpu" class="icon" />
      <span class="title">大模型配置</span>
    </div>
    
    <div class="model-filter">
      <el-tabs v-model="activeFilter" class="filter-tabs">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="可用" name="available" />
        <el-tab-pane label="按提供商" name="provider" />
      </el-tabs>
    </div>
    
    <div class="model-grid">
      <div
        v-for="model in filteredModels"
        :key="model.id"
        class="model-card"
        :class="{ selected: localSelectedModel === model.id, disabled: !model.available }"
        @click="selectModel(model)"
      >
        <div class="model-header">
          <div class="model-radio">
            <input
              type="radio"
              :value="model.id"
              :checked="localSelectedModel === model.id"
              :disabled="!model.available"
              @change="selectModel(model)"
              class="radio-input"
            />
          </div>
          <div class="model-badge" :class="{ premium: model.cost !== '免费' }">
            {{ model.cost }}
          </div>
        </div>
        
        <div class="model-info">
          <h3 class="model-name">{{ model.name }}</h3>
          <p class="model-provider">{{ model.provider }}</p>
          <p class="model-desc">{{ model.description }}</p>
        </div>
        
        <div class="model-specs">
          <div class="spec-item">
            <span class="spec-label">最大Token</span>
            <span class="spec-value">{{ formatTokens(model.maxTokens) }}</span>
          </div>
        </div>
        
        <div class="model-actions">
          <el-button 
            size="small" 
            type="primary"
            :disabled="!model.available"
            @click.stop="selectModel(model)"
          >
            {{ localSelectedModel === model.id ? '已选择' : '选择' }}
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="config-summary" v-if="selectedModel">
      <div class="summary-title">当前配置</div>
      <div class="summary-content">
        <div class="summary-item">
          <span class="label">智能体</span>
          <span class="value">{{ agentName }}</span>
        </div>
        <div class="summary-item">
          <span class="label">模型</span>
          <span class="value">{{ selectedModel.name }}</span>
        </div>
        <div class="summary-item">
          <span class="label">提供商</span>
          <span class="value">{{ selectedModel.provider }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Cpu } from 'lucide-vue-next'
import type { ModelInfo } from '@/types'

const props = defineProps<{
  models: ModelInfo[]
  selectedModelId: string
  agentName: string
}>()

const emit = defineEmits<{
  (e: 'select', modelId: string): void
}>()

const icons = { Cpu }
const activeFilter = ref('all')
const localSelectedModel = ref(props.selectedModelId)

// Sync local value with prop changes
watch(() => props.selectedModelId, (newVal) => {
  localSelectedModel.value = newVal
})

const filteredModels = computed(() => {
  let result = props.models
  if (activeFilter.value === 'available') {
    result = result.filter(m => m.available)
  }
  return result
})

const selectedModel = computed(() => {
  return props.models.find(m => m.id === localSelectedModel.value)
})

const selectModel = (model: ModelInfo) => {
  if (model.available) {
    localSelectedModel.value = model.id
    emit('select', model.id)
  }
}

const formatTokens = (tokens: number): string => {
  if (tokens >= 1000000) {
    return (tokens / 1000000).toFixed(1) + 'M'
  } else if (tokens >= 1000) {
    return (tokens / 1000).toFixed(0) + 'K'
  }
  return tokens.toString()
}
</script>

<style lang="scss" scoped>
@import '@/style/index.scss';

.model-selector {
  background: $bg-card;
  border-radius: $radius-lg;
  border: 1px solid $border-color;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.selector-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  
  .icon {
    width: 22px;
    height: 22px;
    color: $primary-color;
  }
  
  .title {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
  }
}

.model-filter {
  margin-bottom: 20px;
}

.filter-tabs {
  .el-tabs__header {
    margin: 0;
  }
  .el-tabs__nav {
    background: transparent;
  }
  .el-tabs__item {
    color: $text-secondary;
    &.is-active {
      color: $primary-color;
    }
  }
}

.model-grid {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.model-card {
  background: $bg-tertiary;
  border-radius: $radius-md;
  padding: 16px;
  border: 2px solid transparent;
  transition: all $transition-fast;
  
  &:hover:not(.disabled) {
    border-color: $border-color;
    transform: translateY(-2px);
  }
  
  &.selected {
    border-color: $primary-color;
    background: rgba(99, 102, 241, 0.1);
  }
  
  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.model-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.model-radio {
  .radio-input {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
}

.model-badge {
  background: $success-color;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  
  &.premium {
    background: $warning-color;
  }
}

.model-info {
  margin-bottom: 12px;
  
  .model-name {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 4px;
  }
  
  .model-provider {
    font-size: 12px;
    color: $primary-color;
    margin-bottom: 6px;
  }
  
  .model-desc {
    font-size: 13px;
    color: $text-secondary;
  }
}

.model-specs {
  background: $bg-card;
  padding: 10px 12px;
  border-radius: $radius-sm;
  margin-bottom: 12px;
  
  .spec-item {
    display: flex;
    justify-content: space-between;
    
    .spec-label {
      font-size: 12px;
      color: $text-muted;
    }
    
    .spec-value {
      font-size: 13px;
      font-weight: 600;
      color: $text-primary;
    }
  }
}

.config-summary {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid $border-color;
  
  .summary-title {
    font-size: 13px;
    color: $text-muted;
    margin-bottom: 12px;
  }
  
  .summary-content {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
  }
  
  .summary-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .label {
      font-size: 12px;
      color: $text-muted;
    }
    
    .value {
      font-size: 13px;
      font-weight: 500;
      color: $text-primary;
    }
  }
}
</style>
<template>
  <div class="emotion-result">
    <div class="emotion-result__container">
      <!-- 标题区域 -->
      <div class="emotion-result__header">
        <h2 class="emotion-result__title">情绪识别结果分析</h2>
        <p class="emotion-result__subtitle">
          共识别 {{ emotionData.length }} 次，分析时长 {{ analysisTime }}
        </p>
      </div>

      <!-- 统计概览 -->
      <div class="emotion-result__overview">
        <div class="emotion-result__stat-card">
          <div class="emotion-result__stat-label">主要情绪</div>
          <div class="emotion-result__stat-value emotion-result__stat-value--primary">
            {{ dominantEmotion }}
          </div>
        </div>
        
        <div class="emotion-result__stat-card">
          <div class="emotion-result__stat-label">平均置信度</div>
          <div class="emotion-result__stat-value">{{ averageConfidence }}%</div>
        </div>
        
        <div class="emotion-result__stat-card">
          <div class="emotion-result__stat-label">情绪变化</div>
          <div class="emotion-result__stat-value">{{ emotionVariety }} 种</div>
        </div>
      </div>

      <!-- 详细记录列表 -->
      <div class="emotion-result__details">
        <h3 class="emotion-result__details-title">详细记录</h3>
        
        <div class="emotion-result__list">
          <div 
            v-for="(record, index) in emotionData" 
            :key="index"
            class="emotion-result__record"
          >
            <div class="emotion-result__record-index">
              {{ index + 1 }}
            </div>
            
            <div class="emotion-result__record-content">
              <div class="emotion-result__record-emotion">
                {{ record.emotion }}
              </div>
              <div class="emotion-result__record-confidence">
                置信度: {{ record.confidence }}%
              </div>
            </div>
            
            <div class="emotion-result__record-time">
              {{ formatTime(record.timestamp) }}
            </div>
            
            <div class="emotion-result__record-bar">
              <div 
                class="emotion-result__record-progress"
                :style="{ width: record.confidence + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 情绪分布统计 -->
      <div class="emotion-result__distribution">
        <h3 class="emotion-result__distribution-title">情绪分布</h3>
        
        <div class="emotion-result__chart">
          <div 
            v-for="(emotion, emotionName) in emotionStats" 
            :key="emotionName"
            class="emotion-result__chart-item"
          >
            <div class="emotion-result__chart-label">
              {{ emotionName }}
            </div>
            <div class="emotion-result__chart-bar">
              <div 
                class="emotion-result__chart-progress"
                :style="{ width: (emotion.count / emotionData.length * 100) + '%' }"
              ></div>
            </div>
            <div class="emotion-result__chart-value">
              {{ emotion.count }} 次 ({{ Math.round(emotion.count / emotionData.length * 100) }}%)
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="emotion-result__actions">
        <button 
          @click="exportResults"
          class="emotion-result__button emotion-result__button--export"
        >
          导出结果
        </button>
        
        <button 
          @click="backToCamera"
          class="emotion-result__button emotion-result__button--back"
        >
          重新识别
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  emotionData: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['back-to-camera'])

// 计算属性
const analysisTime = computed(() => {
  if (props.emotionData.length === 0) return '0秒'
  return `${props.emotionData.length}秒`
})

const dominantEmotion = computed(() => {
  if (props.emotionData.length === 0) return '无数据'
  
  const emotionCounts = {}
  props.emotionData.forEach(record => {
    emotionCounts[record.emotion] = (emotionCounts[record.emotion] || 0) + 1
  })
  
  let maxCount = 0
  let dominant = '无'
  
  Object.entries(emotionCounts).forEach(([emotion, count]) => {
    if (count > maxCount) {
      maxCount = count
      dominant = emotion
    }
  })
  
  return dominant
})

const averageConfidence = computed(() => {
  if (props.emotionData.length === 0) return 0
  
  const total = props.emotionData.reduce((sum, record) => sum + record.confidence, 0)
  return Math.round(total / props.emotionData.length)
})

const emotionVariety = computed(() => {
  const uniqueEmotions = new Set(props.emotionData.map(record => record.emotion))
  return uniqueEmotions.size
})

const emotionStats = computed(() => {
  const stats = {}
  
  props.emotionData.forEach(record => {
    if (!stats[record.emotion]) {
      stats[record.emotion] = {
        count: 0,
        totalConfidence: 0
      }
    }
    stats[record.emotion].count++
    stats[record.emotion].totalConfidence += record.confidence
  })
  
  // 计算平均置信度
  Object.keys(stats).forEach(emotion => {
    stats[emotion].avgConfidence = Math.round(
      stats[emotion].totalConfidence / stats[emotion].count
    )
  })
  
  return stats
})

// 方法
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const exportResults = () => {
  const data = {
    summary: {
      totalRecords: props.emotionData.length,
      analysisTime: analysisTime.value,
      dominantEmotion: dominantEmotion.value,
      averageConfidence: averageConfidence.value,
      emotionVariety: emotionVariety.value
    },
    details: props.emotionData,
    distribution: emotionStats.value,
    exportTime: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { 
    type: 'application/json' 
  })
  
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `emotion-analysis-${new Date().toISOString().slice(0, 10)}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const backToCamera = () => {
  emit('back-to-camera')
}
</script>

<style scoped>
.emotion-result {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
  padding: 1rem;
  overflow-y: auto;
}

.emotion-result__container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  max-width: 1000px;
  width: 100%;
}

.emotion-result__header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(226, 232, 240, 0.8);
}

.emotion-result__title {
  color: #1f2937;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.emotion-result__subtitle {
  color: #6b7280;
  font-size: 1.1rem;
  margin: 0;
}

.emotion-result__overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.emotion-result__stat-card {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.emotion-result__stat-label {
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.emotion-result__stat-value {
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 700;
}

.emotion-result__stat-value--primary {
  color: #3b82f6;
  font-size: 1.8rem;
}

.emotion-result__details {
  margin-bottom: 2rem;
}

.emotion-result__details-title {
  color: #1f2937;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.emotion-result__list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.emotion-result__record {
  display: grid;
  grid-template-columns: 40px 1fr 120px;
  grid-template-rows: auto auto;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 8px;
  border: 1px solid rgba(226, 232, 240, 0.6);
  transition: all 0.2s ease;
}

.emotion-result__record:hover {
  background: rgba(243, 244, 246, 0.9);
  transform: translateX(4px);
}

.emotion-result__record-index {
  grid-row: 1 / 3;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 0.9rem;
}

.emotion-result__record-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.emotion-result__record-emotion {
  font-weight: 600;
  color: #1f2937;
  font-size: 1.1rem;
}

.emotion-result__record-confidence {
  color: #6b7280;
  font-size: 0.9rem;
}

.emotion-result__record-time {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  color: #9ca3af;
  font-size: 0.8rem;
}

.emotion-result__record-bar {
  grid-column: 2 / 4;
  height: 4px;
  background: rgba(226, 232, 240, 0.8);
  border-radius: 2px;
  overflow: hidden;
}

.emotion-result__record-progress {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.emotion-result__distribution {
  margin-bottom: 2rem;
}

.emotion-result__distribution-title {
  color: #1f2937;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.emotion-result__chart {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.emotion-result__chart-item {
  display: grid;
  grid-template-columns: 100px 1fr 120px;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: rgba(248, 250, 252, 0.6);
  border-radius: 8px;
}

.emotion-result__chart-label {
  font-weight: 600;
  color: #374151;
}

.emotion-result__chart-bar {
  height: 20px;
  background: rgba(226, 232, 240, 0.8);
  border-radius: 10px;
  overflow: hidden;
}

.emotion-result__chart-progress {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  border-radius: 10px;
  transition: width 0.5s ease;
}

.emotion-result__chart-value {
  text-align: right;
  font-size: 0.9rem;
  color: #6b7280;
}

.emotion-result__actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.emotion-result__button {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.emotion-result__button--export {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
}

.emotion-result__button--export:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 92, 246, 0.5);
}

.emotion-result__button--back {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.emotion-result__button--back:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
}

/* 滚动条样式 */
.emotion-result__list::-webkit-scrollbar {
  width: 6px;
}

.emotion-result__list::-webkit-scrollbar-track {
  background: rgba(226, 232, 240, 0.3);
  border-radius: 3px;
}

.emotion-result__list::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

.emotion-result__list::-webkit-scrollbar-thumb:hover {
  background: rgba(107, 114, 128, 0.7);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .emotion-result__container {
    padding: 1.5rem;
  }
  
  .emotion-result__title {
    font-size: 1.5rem;
  }
  
  .emotion-result__overview {
    grid-template-columns: 1fr;
  }
  
  .emotion-result__record {
    grid-template-columns: 40px 1fr;
    grid-template-rows: auto auto auto;
  }
  
  .emotion-result__record-time {
    grid-column: 1 / 3;
    justify-content: flex-start;
    margin-top: 0.25rem;
  }
  
  .emotion-result__record-bar {
    grid-column: 1 / 3;
  }
  
  .emotion-result__chart-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .emotion-result__chart-value {
    text-align: left;
  }
  
  .emotion-result__actions {
    flex-direction: column;
    align-items: center;
  }
  
  .emotion-result__button {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .emotion-result {
    padding: 0.5rem;
  }
  
  .emotion-result__container {
    padding: 1rem;
  }
  
  .emotion-result__stat-card {
    padding: 1rem;
  }
}
</style> 
<template>
  <div class="app">
    <div class="app__header">
      <h1 class="app__title">智能情绪识别系统</h1>
      <div class="app__nav">
        <button 
          @click="currentView = 'camera'" 
          :class="{ active: currentView === 'camera' }"
          class="app__nav-btn"
        >
          摄像头识别
        </button>
        <button 
          @click="currentView = 'test'" 
          :class="{ active: currentView === 'test' }"
          class="app__nav-btn"
        >
          API测试
        </button>
      </div>
    </div>
    
    <div class="app__content">
      <CameraEmotionPage 
        v-if="currentView === 'camera'"
        @show-result="handleShowResult"
      />
      
      <EmotionResult 
        v-else-if="currentView === 'result'"
        :emotion-data="emotionData"
        @back-to-camera="handleBackToCamera"
      />
      
      <ApiTestPage 
        v-else-if="currentView === 'test'"
        @back="currentView = 'camera'"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CameraEmotionPage from './components/CameraEmotionPage.vue'
import EmotionResult from './components/EmotionResult.vue'
import ApiTestPage from './components/ApiTestPage.vue'

const currentView = ref('camera')
const emotionData = ref([])

const handleShowResult = (data) => {
  emotionData.value = data
  currentView.value = 'result'
}

const handleBackToCamera = () => {
  emotionData.value = []
  currentView.value = 'camera'
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.app__header {
  text-align: center;
  padding: 2rem 0;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.app__title {
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.app__content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.app__nav {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.app__nav-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.app__nav-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.app__nav-btn.active {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  font-weight: 600;
}

@media (max-width: 768px) {
  .app__title {
    font-size: 1.8rem;
  }
  
  .app__content {
    padding: 1rem;
  }
  
  .app__nav {
    flex-direction: column;
    align-items: center;
  }
}
</style> 
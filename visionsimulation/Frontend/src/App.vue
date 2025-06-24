<template>
  <div class="app">
    <div class="app__header">
      <h1 class="app__title">智能情绪识别系统</h1>
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
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CameraEmotionPage from './components/CameraEmotionPage.vue'
import EmotionResult from './components/EmotionResult.vue'

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

@media (max-width: 768px) {
  .app__title {
    font-size: 1.8rem;
  }
  
  .app__content {
    padding: 1rem;
  }
}
</style> 
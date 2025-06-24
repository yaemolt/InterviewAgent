<template>
  <div class="camera-emotion-page">
    <div class="camera-emotion-page__container">
      <!-- 摄像头预览区域 -->
      <div class="camera-emotion-page__video-section">
        <video
          ref="videoElement"
          class="camera-emotion-page__video"
          autoplay
          muted
          playsinline
        ></video>
        
        <div v-if="!isRecording && !hasStarted" class="camera-emotion-page__overlay">
          <div class="camera-emotion-page__overlay-text">
            点击开始按钮开始情绪识别
          </div>
        </div>
      </div>

      <!-- 状态信息显示区域 -->
      <div class="camera-emotion-page__info">
        <div class="camera-emotion-page__status">
          <span class="camera-emotion-page__status-label">状态：</span>
          <span 
            :class="[
              'camera-emotion-page__status-value',
              { 'camera-emotion-page__status-value--recording': isRecording }
            ]"
          >
            {{ statusText }}
          </span>
        </div>
        
        <div class="camera-emotion-page__counter">
          <span class="camera-emotion-page__counter-label">识别次数：</span>
          <span class="camera-emotion-page__counter-value">{{ emotionResults.length }}</span>
        </div>

        <!-- 最新情绪结果显示 -->
        <div v-if="latestEmotion" class="camera-emotion-page__latest-result">
          <h3 class="camera-emotion-page__latest-title">最新识别结果</h3>
          <div class="camera-emotion-page__emotion-item">
            <span class="camera-emotion-page__emotion-label">情绪：</span>
            <span class="camera-emotion-page__emotion-value">{{ latestEmotion.emotion }}</span>
          </div>
          <div class="camera-emotion-page__emotion-item">
            <span class="camera-emotion-page__emotion-label">置信度：</span>
            <span class="camera-emotion-page__emotion-value">{{ latestEmotion.confidence }}%</span>
          </div>
        </div>
      </div>

      <!-- 控制按钮区域 -->
      <div class="camera-emotion-page__controls">
        <button
          v-if="!hasStarted"
          @click="startRecording"
          :disabled="loading"
          class="camera-emotion-page__button camera-emotion-page__button--start"
        >
          开始识别
        </button>
        
        <button
          v-if="isRecording"
          @click="stopRecording"
          class="camera-emotion-page__button camera-emotion-page__button--stop"
        >
          结束识别
        </button>

        <button
          v-if="hasStarted && !isRecording && emotionResults.length > 0"
          @click="viewResults"
          class="camera-emotion-page__button camera-emotion-page__button--result"
        >
          查看完整结果
        </button>

        <button
          @click="testVideoAPI"
          class="camera-emotion-page__button camera-emotion-page__button--test"
          :disabled="loading"
        >
          测试API连接
        </button>
      </div>

      <!-- 错误信息显示 -->
      <div v-if="error" class="camera-emotion-page__error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { recognizeEmotion, checkAPIHealth, testAPI } from '@/api/emotion.js'

const emit = defineEmits(['show-result'])

// 响应式数据
const videoElement = ref(null)
const isRecording = ref(false)
const hasStarted = ref(false)
const loading = ref(false)
const error = ref('')
const emotionResults = ref([])

let mediaStream = null
let mediaRecorder = null

// 计算属性
const statusText = computed(() => {
  if (loading.value) return '初始化中...'
  if (!hasStarted.value) return '准备就绪'
  if (isRecording.value) return '识别中...'
  return '已停止'
})

const latestEmotion = computed(() => {
  if (emotionResults.value.length === 0) return null
  return emotionResults.value[emotionResults.value.length - 1]
})

// 检查API健康状态
const checkBackendHealth = async () => {
  try {
    const response = await checkAPIHealth()
    if (response.data && response.data.status === 'healthy' && response.data.model_loaded) {
      console.log('✅ 后端API健康检查通过')
      console.log('模型状态:', response.data.model_loaded ? '已加载' : '未加载')
      console.log('设备:', response.data.device || 'unknown')
      return true
    } else {
      console.warn('⚠️ 后端API状态异常:', response.data)
      error.value = '后端模型未加载，请检查后端服务'
      return false
    }
  } catch (err) {
    console.error('❌ 后端健康检查失败:', err)
    error.value = '无法连接到后端服务，请确保后端运行在 localhost:5000'
    return false
  }
}

// 初始化摄像头
const initCamera = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 首先检查后端API状态
    const backendReady = await checkBackendHealth()
    if (!backendReady) {
      loading.value = false
      return
    }
    
    const constraints = {
      video: {
        width: { ideal: 640, max: 1280 },
        height: { ideal: 480, max: 720 },
        frameRate: { ideal: 8, max: 8 }, // 确保8fps，每秒8帧
        facingMode: 'user'
      },
      audio: false
    }

    mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
    
    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
    }
    
    console.log('摄像头初始化成功，帧率设置为8fps')
  } catch (err) {
    console.error('摄像头初始化失败：', err)
    error.value = '无法访问摄像头，请检查权限设置'
  } finally {
    loading.value = false
  }
}

// 开始录制
const startRecording = async () => {
  try {
    if (!mediaStream) {
      await initCamera()
    }
    
    if (!mediaStream) return

    hasStarted.value = true
    isRecording.value = true
    error.value = ''

    // 配置MediaRecorder，使用最稳定的设置
    let options = {}
    
    // 尝试不同的视频格式，优先使用最兼容的
    const supportedTypes = [
      'video/mp4',
      'video/webm;codecs=vp8',
      'video/webm;codecs=vp9', 
      'video/webm'
    ]
    
    console.log('🎬 检查支持的视频格式：')
    for (const type of supportedTypes) {
      const supported = MediaRecorder.isTypeSupported(type)
      console.log(`   ${type}: ${supported ? '✅' : '❌'}`)
      
      if (supported && !options.mimeType) {
        options = { 
          mimeType: type,
          videoBitsPerSecond: 1000000 // 1Mbps，减少文件大小
        }
        console.log(`✅ 选择格式: ${type}`)
      }
    }
    
    if (!options.mimeType) {
      console.warn('⚠️ 使用默认视频格式')
      options = {
        videoBitsPerSecond: 1000000
      }
    }
    
    mediaRecorder = new MediaRecorder(mediaStream, options)
    
    mediaRecorder.ondataavailable = async (event) => {
      if (event.data && event.data.size > 0) {
        console.log('📹 收到视频片段')
        console.log('   大小：', event.data.size, 'bytes')
        console.log('   类型：', event.data.type)
        console.log('   实际格式：', options?.mimeType || 'default')
        await handleVideoData(event.data)
      }
    }
    
    mediaRecorder.onerror = (event) => {
      console.error('MediaRecorder错误：', event.error)
      error.value = '录制过程中发生错误'
    }

    // 每1000ms触发一次dataavailable事件，获取过去1s的8帧视频
    mediaRecorder.start(1000)
    console.log('开始录制，每1秒收集8帧视频片段')
    
  } catch (err) {
    console.error('开始录制失败：', err)
    error.value = '开始录制失败'
    isRecording.value = false
  }
}

// 停止录制
const stopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    console.log('录制已停止')
  }
}

// 处理视频数据并发送到后端
const handleVideoData = async (videoBlob) => {
  try {
    console.log('正在发送视频片段进行情绪识别...')
    const response = await recognizeEmotion(videoBlob)
    
    // 添加详细的调试日志
    console.log('🔍 完整API响应：', response)
    console.log('🔍 响应状态：', response.status)
    console.log('🔍 响应数据：', response.data)
    
    if (response.data && response.data.success) {
      const data = response.data.data
      
      // 找到主导情绪和置信度
      const dominantEmotion = data.dominant_emotion || '未知'
      const overallEngagement = data.overall_engagement || 0
      
      // 处理四个维度的情绪数据
      const emotionData = {
        emotion: dominantEmotion,
        confidence: Math.round(overallEngagement * 100 / 3), // 转换为百分比 (0-3 -> 0-100)
        timestamp: new Date().toISOString(),
        processingTime: data.processing_time || '0ms',
        allEmotions: data.emotions || [],
        overallEngagement: data.overall_engagement || 0,
        overallConfusion: data.overall_confusion || 0,
        rawData: response.data
      }
      
      emotionResults.value.push(emotionData)
      console.log('✅ 情绪识别成功，当前识别次数：', emotionResults.value.length)
      console.log('🎯 识别结果：', emotionData)
      console.log('📊 详细情绪数据：', data.emotions)
    } else {
      console.warn('⚠️ 情绪识别返回异常数据：', response.data)
      
      // 即使格式不对，也尝试处理数据（容错处理）
      if (response.data) {
        const fallbackData = {
          emotion: '未知',
          confidence: 0,
          timestamp: new Date().toISOString(),
          processingTime: '0ms',
          allEmotions: [],
          overallEngagement: 0,
          overallConfusion: 0,
          rawData: response.data
        }
        emotionResults.value.push(fallbackData)
        console.log('📝 使用容错数据，当前识别次数：', emotionResults.value.length)
      }
    }
  } catch (err) {
    console.error('❌ 情绪识别失败：', err)
    
    // 添加一个错误记录
    const errorData = {
      emotion: '错误',
      confidence: 0,
      timestamp: new Date().toISOString(),
      processingTime: '0ms',
      allEmotions: [],
      overallEngagement: 0,
      overallConfusion: 0,
      error: err.message,
      rawData: null
    }
    emotionResults.value.push(errorData)
    console.log('🚨 添加错误记录，当前识别次数：', emotionResults.value.length)
  }
}

// 查看完整结果
const viewResults = () => {
  emit('show-result', emotionResults.value)
}

// 测试视频API连接
const testVideoAPI = async () => {
  try {
    loading.value = true
    error.value = ''
    
    console.log('🧪 开始测试API连接...')
    
    // 先测试健康检查
    const healthResponse = await checkAPIHealth()
    console.log('🏥 健康检查结果：', healthResponse.data)
    
    // 再测试虚拟数据API
    const testResponse = await testAPI()
    console.log('🧪 测试API结果：', testResponse.data)
    
    // 如果成功，添加一个测试结果
    if (testResponse.data && testResponse.data.success) {
      const testData = {
        emotion: '测试成功',
        confidence: 100,
        timestamp: new Date().toISOString(),
        processingTime: testResponse.data.data?.processing_time || '0ms',
        allEmotions: testResponse.data.data?.emotions || [],
        overallEngagement: testResponse.data.data?.overall_engagement || 0,
        overallConfusion: testResponse.data.data?.overall_confusion || 0,
        rawData: testResponse.data
      }
      
      emotionResults.value.push(testData)
      console.log('✅ API测试成功，当前识别次数：', emotionResults.value.length)
    }
    
  } catch (err) {
    console.error('❌ API测试失败：', err)
    error.value = `API测试失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

// 清理资源
const cleanup = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
  }
  
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
}

// 生命周期钩子
onMounted(() => {
  initCamera()
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.camera-emotion-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 1rem;
}

.camera-emotion-page__container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  max-width: 800px;
  width: 100%;
}

.camera-emotion-page__video-section {
  position: relative;
  margin-bottom: 2rem;
  border-radius: 16px;
  overflow: hidden;
  background: #000;
}

.camera-emotion-page__video {
  width: 100%;
  height: auto;
  max-height: 400px;
  display: block;
  object-fit: cover;
}

.camera-emotion-page__overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-emotion-page__overlay-text {
  color: white;
  font-size: 1.2rem;
  text-align: center;
  padding: 1rem;
}

.camera-emotion-page__info {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(247, 250, 252, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.camera-emotion-page__status,
.camera-emotion-page__counter {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.camera-emotion-page__status-label,
.camera-emotion-page__counter-label {
  font-weight: 600;
  color: #374151;
  min-width: 80px;
}

.camera-emotion-page__status-value {
  color: #6b7280;
  font-weight: 500;
}

.camera-emotion-page__status-value--recording {
  color: #ef4444;
  animation: pulse 1.5s ease-in-out infinite;
}

.camera-emotion-page__counter-value {
  color: #3b82f6;
  font-weight: 600;
  font-size: 1.1rem;
}

.camera-emotion-page__latest-result {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
}

.camera-emotion-page__latest-title {
  margin: 0 0 0.75rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.camera-emotion-page__emotion-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.25rem;
}

.camera-emotion-page__emotion-label {
  font-weight: 500;
  color: #6b7280;
  min-width: 70px;
}

.camera-emotion-page__emotion-value {
  color: #059669;
  font-weight: 600;
}

.camera-emotion-page__controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.camera-emotion-page__button {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.camera-emotion-page__button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.camera-emotion-page__button--start {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.camera-emotion-page__button--start:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5);
}

.camera-emotion-page__button--stop {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.camera-emotion-page__button--stop:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.5);
}

.camera-emotion-page__button--result {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.camera-emotion-page__button--result:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
}

.camera-emotion-page__error {
  margin-top: 1rem;
  padding: 1rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .camera-emotion-page__container {
    padding: 1.5rem;
  }
  
  .camera-emotion-page__video {
    max-height: 300px;
  }
  
  .camera-emotion-page__controls {
    flex-direction: column;
    align-items: center;
  }
  
  .camera-emotion-page__button {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .camera-emotion-page {
    padding: 0.5rem;
  }
  
  .camera-emotion-page__container {
    padding: 1rem;
  }
  
  .camera-emotion-page__overlay-text {
    font-size: 1rem;
  }
}
</style> 
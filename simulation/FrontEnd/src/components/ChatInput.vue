<template>
  <div class="chat-input">
    <!-- 文字输入模式 -->
    <div v-if="inputMode === 'text'" class="text-input-container">
      <input
        v-model="inputMessage"
        type="text"
        placeholder="请输入消息..."
        @keypress.enter="handleSend"
        :disabled="loading"
        class="text-input"
      />
      <button 
        @click="handleSend" 
        :disabled="!inputMessage.trim() || loading"
        class="send-btn"
      >
        {{ loading ? '发送中...' : '发送' }}
      </button>
      
      <!-- 切换到语音模式按钮 -->
      <button 
        @click="switchToVoiceMode" 
        :disabled="loading || !asrAvailable"
        class="voice-mode-btn"
        :title="asrAvailable ? '切换到语音输入' : '语音识别服务不可用'"
      >
        🎤
      </button>
    </div>

    <!-- 语音输入模式 -->
    <div v-else class="voice-input-container">
      <!-- 语音状态显示 -->
      <div class="voice-status">
        <!-- 录音状态 -->
        <div v-if="isRecording" class="recording-status">
          <div class="recording-animation">
            <div class="pulse"></div>
            <div class="pulse"></div>
            <div class="pulse"></div>
          </div>
          <span class="status-text">正在录音... ({{ recordingTime }}s)</span>
        </div>
        
        <!-- 识别状态 -->
        <div v-else-if="isRecognizing" class="recognizing-status">
          <div class="loading-dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
          <span class="status-text">正在识别语音...</span>
        </div>
        
        <!-- 默认状态 -->
        <div v-else class="ready-status">
          <span class="status-text">点击按钮开始录音</span>
        </div>
      </div>

      <!-- 录音控制按钮 -->
      <div class="voice-controls">
        <button 
          @click="toggleRecording"
          :disabled="loading || isRecognizing"
          :class="['record-btn', { 
            'recording': isRecording,
            'ready': !isRecording && !isRecognizing
          }]"
        >
          <span v-if="isRecording">⏹️ 停止录音</span>
          <span v-else>🎤 开始录音</span>
        </button>
        
        <!-- 切换回文字模式按钮 -->
        <button 
          @click="switchToTextMode" 
          :disabled="loading || isRecording || isRecognizing"
          class="text-mode-btn"
        >
          ⌨️ 文字输入
        </button>
      </div>

      <!-- 错误提示 -->
      <div v-if="voiceError" class="voice-error">
        {{ voiceError }}
      </div>

      <!-- 识别结果预览 -->
      <div v-if="recognizedText" class="recognized-text">
        <div class="text-preview">
          <span class="label">识别结果:</span>
          <span class="text">{{ recognizedText }}</span>
        </div>
        <div class="preview-actions">
          <button @click="handleSendRecognizedText" class="send-recognized-btn">
            📤 发送
          </button>
          <button @click="clearRecognizedText" class="clear-btn">
            🗑️ 清除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { recognizeSpeech } from '@/api/chat.js'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  asrAvailable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send'])

// 输入模式状态
const inputMode = ref('text') // 'text' | 'voice'
const inputMessage = ref('')

// 语音录制相关状态
const isRecording = ref(false)
const isRecognizing = ref(false)
const recordingTime = ref(0)
const recognizedText = ref('')
const voiceError = ref('')

// 录音相关变量
let mediaRecorder = null
let audioChunks = []
let recordingTimer = null
let recordingStartTime = null

// 文字发送
const handleSend = () => {
  const message = inputMessage.value.trim()
  if (message && !props.loading) {
    emit('send', message)
    inputMessage.value = ''
  }
}

// 发送识别的文字
const handleSendRecognizedText = () => {
  if (recognizedText.value && !props.loading) {
    emit('send', recognizedText.value)
    clearRecognizedText()
  }
}

// 清除识别结果
const clearRecognizedText = () => {
  recognizedText.value = ''
  voiceError.value = ''
}

// 切换输入模式
const switchToVoiceMode = () => {
  if (props.asrAvailable) {
    inputMode.value = 'voice'
    clearRecognizedText()
  }
}

const switchToTextMode = () => {
  inputMode.value = 'text'
  if (isRecording.value) {
    stopRecording()
  }
  clearRecognizedText()
}

// 初始化麦克风
const initMicrophone = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true
      } 
    })
    
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    })
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }
    
    mediaRecorder.onstop = async () => {
      await processRecording()
    }
    
    return true
  } catch (error) {
    console.error('麦克风初始化失败:', error)
    voiceError.value = '无法访问麦克风，请检查浏览器权限'
    return false
  }
}

// 开始录音
const startRecording = async () => {
  try {
    voiceError.value = ''
    
    // 如果还没有初始化麦克风，先初始化
    if (!mediaRecorder) {
      const success = await initMicrophone()
      if (!success) return
    }
    
    // 清空之前的录音数据
    audioChunks = []
    
    // 开始录音
    mediaRecorder.start(100) // 每100ms收集一次数据
    isRecording.value = true
    recordingStartTime = Date.now()
    
    // 开始计时
    recordingTimer = setInterval(() => {
      recordingTime.value = Math.floor((Date.now() - recordingStartTime) / 1000)
    }, 1000)
    
    console.log('🎤 开始录音')
  } catch (error) {
    console.error('录音启动失败:', error)
    voiceError.value = '录音启动失败'
  }
}

// 停止录音
const stopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    
    // 清除计时器
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
    
    console.log('🎤 停止录音')
  }
}

// 处理录音数据
const processRecording = async () => {
  try {
    if (audioChunks.length === 0) {
      voiceError.value = '录音数据为空，请重新录音'
      return
    }
    
    // 创建音频Blob
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' })
    console.log(`🎤 录音完成，文件大小: ${audioBlob.size} bytes`)
    
    // 开始识别
    isRecognizing.value = true
    voiceError.value = ''
    
    // 调用语音识别API
    const result = await recognizeSpeech(audioBlob)
    
    if (result.success) {
      recognizedText.value = result.text
      console.log('🎤 语音识别成功:', result.text)
    } else {
      voiceError.value = result.error || '语音识别失败'
    }
  } catch (error) {
    console.error('语音识别处理失败:', error)
    voiceError.value = error.message || '语音识别失败'
  } finally {
    isRecognizing.value = false
    recordingTime.value = 0
    audioChunks = []
  }
}

// 切换录音状态
const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 检查浏览器是否支持录音
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    console.warn('浏览器不支持录音功能')
  }
})

// 组件卸载时清理
onUnmounted(() => {
  if (isRecording.value) {
    stopRecording()
  }
  
  if (recordingTimer) {
    clearInterval(recordingTimer)
  }
  
  // 释放媒体流
  if (mediaRecorder && mediaRecorder.stream) {
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.chat-input {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

/* 文字输入模式 */
.text-input-container {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.text-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
}

.text-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.text-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn, .voice-mode-btn, .text-mode-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled),
.voice-mode-btn:hover:not(:disabled),
.text-mode-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.send-btn:disabled,
.voice-mode-btn:disabled,
.text-mode-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.voice-mode-btn {
  padding: 0.75rem;
  font-size: 1.2rem;
  min-width: auto;
}

/* 语音输入模式 */
.voice-input-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.voice-status {
  text-align: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.recording-status, .recognizing-status, .ready-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.status-text {
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 录音动画 */
.recording-animation {
  display: flex;
  gap: 4px;
}

.pulse {
  width: 8px;
  height: 8px;
  background: #ff4757;
  border-radius: 50%;
  animation: pulse 1.5s infinite ease-in-out;
}

.pulse:nth-child(1) { animation-delay: 0s; }
.pulse:nth-child(2) { animation-delay: 0.2s; }
.pulse:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 60%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  30% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 识别动画 */
.loading-dots {
  display: flex;
  gap: 3px;
}

.loading-dots .dot {
  width: 6px;
  height: 6px;
  background: #ffa726;
  border-radius: 50%;
  animation: loading 1.4s infinite ease-in-out;
}

.loading-dots .dot:nth-child(1) { animation-delay: -0.32s; }
.loading-dots .dot:nth-child(2) { animation-delay: -0.16s; }
.loading-dots .dot:nth-child(3) { animation-delay: 0s; }

@keyframes loading {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 录音控制 */
.voice-controls {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.record-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.record-btn.ready {
  background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);
  color: white;
}

.record-btn.recording {
  background: linear-gradient(135deg, #ff4757 0%, #ff3742 100%);
  color: white;
  animation: recordingPulse 2s infinite;
}

@keyframes recordingPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.4); }
  50% { box-shadow: 0 0 0 10px rgba(255, 71, 87, 0); }
}

.record-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.record-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 错误提示 */
.voice-error {
  color: #ff4757;
  font-size: 0.85rem;
  text-align: center;
  padding: 0.5rem;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.3);
  border-radius: 8px;
}

/* 识别结果 */
.recognized-text {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
}

.text-preview {
  margin-bottom: 0.75rem;
}

.text-preview .label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.8rem;
  display: block;
  margin-bottom: 0.25rem;
}

.text-preview .text {
  color: white;
  font-size: 0.95rem;
  line-height: 1.4;
}

.preview-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.send-recognized-btn {
  background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn {
  background: linear-gradient(135deg, #ff7043 0%, #f4511e 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.send-recognized-btn:hover,
.clear-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .text-input-container {
    flex-wrap: wrap;
  }
  
  .text-input {
    min-width: 0;
    font-size: 0.9rem;
  }
  
  .send-btn, .voice-mode-btn, .text-mode-btn {
    font-size: 0.9rem;
    padding: 0.6rem 1.2rem;
  }
  
  .voice-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .preview-actions {
    flex-direction: column;
  }
}
</style> 
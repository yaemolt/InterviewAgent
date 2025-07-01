<template>
  <div class="chat-list" ref="chatListRef">
    <div
      v-for="message in messages"
      :key="message.id"
      :class="['message', message.type]"
    >
      <div class="message-content">
        <div class="message-text">{{ message.text }}</div>
        
        <!-- 面试官消息的语音状态显示 -->
        <div v-if="message.type === 'bot'" class="voice-status-display">
          <!-- 语音生成状态 -->
          <div v-if="isGeneratingVoice && currentVoiceMessageId === message.id" class="voice-indicator generating">
            <div class="loading-dots">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
            <span class="status-text">正在生成语音...</span>
          </div>
          
          <!-- 语音播放状态 -->
          <div v-else-if="isPlayingVoice && currentVoiceMessageId === message.id" class="voice-indicator playing">
            <div class="voice-animation">
              <div class="wave"></div>
              <div class="wave"></div>
              <div class="wave"></div>
              <div class="wave"></div>
              <div class="wave"></div>
            </div>
            <span class="status-text">正在播放语音...</span>
          </div>
          
          <!-- 语音错误提示 -->
          <div v-if="voiceError && currentVoiceMessageId === message.id" class="voice-error">
            {{ voiceError }}
          </div>
        </div>
      </div>
      
      <div class="message-time">{{ formatTime(message.timestamp) }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { formatTime } from '@/utils/index.js'
import { generateSpeech } from '@/api/chat.js'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  ttsAvailable: {
    type: Boolean,
    default: false
  }
})

const chatListRef = ref(null)

// 语音播放相关状态
const isGeneratingVoice = ref(false)
const isPlayingVoice = ref(false)
const currentVoiceMessageId = ref(null)
const voiceError = ref('')
const currentAudio = ref(null)

// 自动滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
  })
}

// 记录上一次消息数量，用于检测新消息
const lastMessageCount = ref(0)

// 监听消息变化，自动滚动到底部并处理语音播放
watch(
  () => props.messages,
  (newMessages) => {
    scrollToBottom()
    
    // 检测是否有新的bot消息
    if (newMessages.length > lastMessageCount.value) {
      const newBotMessages = newMessages.slice(lastMessageCount.value).filter(msg => msg.type === 'bot')
      
      // 处理新的bot消息
      newBotMessages.forEach((message, index) => {
        // 跳过欢迎消息（包含"我已经收到您的简历信息"或者消息ID为1的初始欢迎消息）
        const isWelcomeMessage = message.text.includes('我已经收到您的简历信息') || 
                                message.text.includes('让我们开始面试吧') ||
                                message.text.includes('我是您的智能面试助手') ||
                                (message.id === 1) // 跳过ID为1的初始消息
        
        if (!isWelcomeMessage) {
          // 延迟1秒后自动播放语音
          setTimeout(() => {
            autoPlayVoice(message)
          }, 1000 + (index * 100)) // 如果有多条消息，略微错开播放时间
        } else {
          console.log('🔇 跳过欢迎消息语音播放:', message.text.substring(0, 30) + '...')
        }
      })
    }
    
    lastMessageCount.value = newMessages.length
  },
  { deep: true }
)

// 自动播放语音
const autoPlayVoice = async (message) => {
  try {
    // 停止当前播放的音频
    if (currentAudio.value) {
      currentAudio.value.pause()
      currentAudio.value = null
      isPlayingVoice.value = false
    }
    
    // 重置错误状态
    voiceError.value = ''
    currentVoiceMessageId.value = message.id
    
    // 检查TTS是否可用
    if (!props.ttsAvailable) {
      voiceError.value = '语音合成服务不可用'
      return
    }
    
    // 开始生成语音
    isGeneratingVoice.value = true
    console.log('🔊 自动生成语音:', message.text.substring(0, 50) + '...')
    
    // 调用语音生成API
    const audioBlob = await generateSpeech(message.text)
    
    // 生成完成，开始播放
    isGeneratingVoice.value = false
    isPlayingVoice.value = true
    
    // 创建音频对象
    const audioUrl = URL.createObjectURL(audioBlob)
    const audio = new Audio(audioUrl)
    currentAudio.value = audio
    
    // 设置音频事件监听
    audio.addEventListener('ended', () => {
      isPlayingVoice.value = false
      currentVoiceMessageId.value = null
      currentAudio.value = null
      URL.revokeObjectURL(audioUrl) // 清理URL对象
      console.log('🔊 语音播放完成')
    })
    
    audio.addEventListener('error', (e) => {
      isPlayingVoice.value = false
      currentVoiceMessageId.value = null
      currentAudio.value = null
      voiceError.value = '音频播放失败'
      URL.revokeObjectURL(audioUrl)
      console.error('❌ 音频播放错误:', e)
    })
    
    // 开始播放
    await audio.play()
    console.log('🔊 开始播放语音')
    
  } catch (error) {
    // 处理错误
    isGeneratingVoice.value = false
    isPlayingVoice.value = false
    currentVoiceMessageId.value = null
    voiceError.value = error.message || '语音生成失败'
    
    console.error('❌ 语音播放失败:', error)
  }
}

// 组件卸载时清理音频
const cleanupAudio = () => {
  if (currentAudio.value) {
    currentAudio.value.pause()
    currentAudio.value = null
  }
  isPlayingVoice.value = false
  isGeneratingVoice.value = false
  currentVoiceMessageId.value = null
}

// 在组件挂载时初始化
onMounted(() => {
  // 初始化消息计数，避免初始消息被当作新消息处理
  lastMessageCount.value = props.messages.length
})

// 在组件卸载时清理
onUnmounted(() => {
  cleanupAudio()
})
</script>

<style scoped>
.message {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-text {
  margin-bottom: 4px;
}

.message-time {
  font-size: 12px;
  opacity: 0.6;
  align-self: flex-end;
}

.message.user .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.message.bot .message-time {
  color: rgba(0, 0, 0, 0.5);
}

/* 语音状态显示样式 */
.voice-status-display {
  margin-top: 8px;
}

.voice-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 11px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.voice-indicator.generating {
  background: linear-gradient(135deg, rgba(255, 167, 38, 0.9) 0%, rgba(255, 112, 67, 0.9) 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(255, 167, 38, 0.3);
}

.voice-indicator.playing {
  background: linear-gradient(135deg, rgba(102, 187, 106, 0.9) 0%, rgba(67, 160, 71, 0.9) 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 187, 106, 0.3);
}

.status-text {
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* 加载动画 */
.loading-dots {
  display: flex;
  gap: 2px;
}

.loading-dots .dot {
  width: 4px;
  height: 4px;
  background: white;
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

/* 语音播放动画 */
.voice-animation {
  display: flex;
  gap: 2px;
  align-items: end;
  height: 16px;
}

.voice-animation .wave {
  width: 3px;
  background: white;
  border-radius: 2px;
  animation: wave 1.2s infinite ease-in-out;
}

.voice-animation .wave:nth-child(1) { animation-delay: 0s; }
.voice-animation .wave:nth-child(2) { animation-delay: 0.1s; }
.voice-animation .wave:nth-child(3) { animation-delay: 0.2s; }
.voice-animation .wave:nth-child(4) { animation-delay: 0.3s; }
.voice-animation .wave:nth-child(5) { animation-delay: 0.4s; }

@keyframes wave {
  0%, 40%, 100% {
    height: 4px;
  }
  20% {
    height: 16px;
  }
}

/* 错误提示 */
.voice-error {
  color: #f44336;
  font-size: 11px;
  margin-top: 4px;
  padding: 4px 8px;
  background: rgba(244, 67, 54, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(244, 67, 54, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .voice-indicator {
    font-size: 10px;
    padding: 4px 8px;
    gap: 6px;
  }
  
  .voice-animation {
    height: 12px;
  }
  
  .voice-animation .wave {
    width: 2px;
  }
  
  @keyframes wave {
    0%, 40%, 100% {
      height: 3px;
    }
    20% {
      height: 12px;
    }
  }
  
  .loading-dots .dot {
    width: 3px;
    height: 3px;
  }
}
</style> 
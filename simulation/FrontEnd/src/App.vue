<template>
  <div class="app-container">
    <!-- 简历填写页面 -->
    <ResumeForm 
      v-if="currentPage === 'resume'"
      :loading="resumeLoading"
      @submit="handleResumeSubmit"
      @cancel="currentPage = 'chat'"
    />
    
    <!-- 聊天界面 -->
    <div v-else-if="currentPage === 'chat'" class="chat-container">
      <div class="chat-header">
        <h1>🤖 智能面试助手</h1>
        <button @click="currentPage = 'resume'" class="resume-btn">
          📝 填写简历
        </button>
      </div>
      <ChatList :messages="messages" />
      <ChatInput @send="handleSendMessage" :loading="loading" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChatList from '@/components/ChatList.vue'
import ChatInput from '@/components/ChatInput.vue'
import ResumeForm from '@/components/ResumeForm.vue'
import { sendMessage, submitResume } from '@/api/chat.js'

// 页面状态管理
const currentPage = ref('resume') // 默认显示简历页面
const resumeLoading = ref(false)

const messages = ref([
  {
    id: 1,
    text: '您好！我是您的智能面试助手。请先填写简历信息，我将根据您的简历生成个性化的面试问题。',
    type: 'bot',
    timestamp: Date.now()
  }
])

const loading = ref(false)

// 处理简历提交
const handleResumeSubmit = async (resumeData) => {
  resumeLoading.value = true
  try {
    const response = await submitResume(resumeData)
    
    // 切换到聊天页面
    currentPage.value = 'chat'
    
    // 清空之前的消息，添加面试官的第一个问题
    messages.value = [
      {
        id: 1,
        text: `您好 ${resumeData.name}！我已经收到您的简历信息。让我们开始面试吧！`,
        type: 'bot',
        timestamp: Date.now()
      },
      {
        id: 2,
        text: response.data.firstQuestion || '请简单介绍一下您自己。',
        type: 'bot',
        timestamp: Date.now() + 1000
      }
    ]
  } catch (error) {
    console.error('简历提交失败：', error)
    alert('简历提交失败，请检查网络连接')
  } finally {
    resumeLoading.value = false
  }
}

const handleSendMessage = async (messageText) => {
  // 添加用户消息
  const userMessage = {
    id: Date.now(),
    text: messageText,
    type: 'user',
    timestamp: Date.now()
  }
  messages.value.push(userMessage)

  // 发送到后端
  loading.value = true
  try {
    const response = await sendMessage(messageText)
    
    // 添加机器人回复
    const botMessage = {
      id: Date.now() + 1,
      text: response.data.response || '抱歉，我暂时无法回答您的问题。',
      type: 'bot',
      timestamp: Date.now()
    }
    messages.value.push(botMessage)
  } catch (error) {
    console.error('发送消息失败：', error)
    
    // 添加错误消息
    const errorMessage = {
      id: Date.now() + 1,
      text: '抱歉，网络连接出现问题，请稍后再试。',
      type: 'bot',
      timestamp: Date.now()
    }
    messages.value.push(errorMessage)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.chat-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.chat-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.chat-header h1 {
  color: white;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.resume-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.resume-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .chat-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .chat-header h1 {
    font-size: 1.2rem;
  }
}
</style> 
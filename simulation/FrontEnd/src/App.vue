<template>
  <div class="chat-container">
    <div class="chat-header">我的聊天助手</div>
    <ChatList :messages="messages" />
    <ChatInput @send="handleSendMessage" :loading="loading" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChatList from '@/components/ChatList.vue'
import ChatInput from '@/components/ChatInput.vue'
import { sendMessage } from '@/api/chat.js'

const messages = ref([
  {
    id: 1,
    text: '您好！我是您的聊天助手，有什么可以帮助您的吗？',
    type: 'bot',
    timestamp: Date.now()
  }
])

const loading = ref(false)

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
      text: response.data.message || '抱歉，我暂时无法回答您的问题。',
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
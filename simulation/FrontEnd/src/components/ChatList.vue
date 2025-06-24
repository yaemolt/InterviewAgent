<template>
  <div class="chat-list" ref="chatListRef">
    <div
      v-for="message in messages"
      :key="message.id"
      :class="['message', message.type]"
    >
      <div class="message-text">{{ message.text }}</div>
      <div class="message-time">{{ formatTime(message.timestamp) }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { formatTime } from '@/utils/index.js'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  }
})

const chatListRef = ref(null)

// 自动滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动到底部
watch(
  () => props.messages,
  () => {
    scrollToBottom()
  },
  { deep: true }
)
</script>

<style scoped>
.message {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
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
</style> 
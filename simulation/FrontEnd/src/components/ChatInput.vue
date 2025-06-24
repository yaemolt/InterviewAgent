<template>
  <div class="chat-input">
    <input
      v-model="inputMessage"
      type="text"
      placeholder="请输入消息..."
      @keypress.enter="handleSend"
      :disabled="loading"
    />
    <button @click="handleSend" :disabled="!inputMessage.trim() || loading">
      {{ loading ? '发送中...' : '发送' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send'])

const inputMessage = ref('')

const handleSend = () => {
  const message = inputMessage.value.trim()
  if (message && !props.loading) {
    emit('send', message)
    inputMessage.value = ''
  }
}
</script> 
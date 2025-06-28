<template>
  <div class="api-test-page">
    <div class="api-test-page__container">
      <h2>API连接测试</h2>
      
      <!-- 健康检查 -->
      <div class="test-section">
        <h3>1. 健康检查测试</h3>
        <button @click="testHealth" :disabled="loading">测试健康检查</button>
        <div v-if="healthResult" class="result">
          <pre>{{ healthResult }}</pre>
        </div>
      </div>

      <!-- 测试API -->
      <div class="test-section">
        <h3>2. 测试API调用</h3>
        <button @click="testEmotionAPI" :disabled="loading">测试虚拟数据</button>
        <div v-if="testResult" class="result">
          <pre>{{ testResult }}</pre>
        </div>
      </div>

      <!-- 模型信息 -->
      <div class="test-section">
        <h3>3. 模型信息</h3>
        <button @click="getModels" :disabled="loading">获取模型信息</button>
        <div v-if="modelResult" class="result">
          <pre>{{ modelResult }}</pre>
        </div>
      </div>

      <!-- 视频上传测试 -->
      <div class="test-section">
        <h3>4. 视频文件测试</h3>
        <input type="file" @change="onFileSelect" accept="video/*" />
        <button @click="testVideoUpload" :disabled="!selectedFile || loading">
          测试视频上传
        </button>
        <div v-if="uploadResult" class="result">
          <pre>{{ uploadResult }}</pre>
        </div>
      </div>

      <!-- 错误信息 -->
      <div v-if="error" class="error">
        {{ error }}
      </div>

      <div class="back-button">
        <button @click="$emit('back')">返回摄像头页面</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { checkAPIHealth, testAPI, getAvailableModels, recognizeEmotion } from '@/api/emotion.js'

const emit = defineEmits(['back'])

const loading = ref(false)
const error = ref('')
const healthResult = ref('')
const testResult = ref('')
const modelResult = ref('')
const uploadResult = ref('')
const selectedFile = ref(null)

const testHealth = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await checkAPIHealth()
    healthResult.value = JSON.stringify(response.data, null, 2)
    console.log('健康检查结果：', response.data)
  } catch (err) {
    error.value = `健康检查失败: ${err.message}`
    console.error('健康检查失败：', err)
  } finally {
    loading.value = false
  }
}

const testEmotionAPI = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await testAPI()
    testResult.value = JSON.stringify(response.data, null, 2)
    console.log('API测试结果：', response.data)
  } catch (err) {
    error.value = `API测试失败: ${err.message}`
    console.error('API测试失败：', err)
  } finally {
    loading.value = false
  }
}

const getModels = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await getAvailableModels()
    modelResult.value = JSON.stringify(response.data, null, 2)
    console.log('模型信息：', response.data)
  } catch (err) {
    error.value = `获取模型信息失败: ${err.message}`
    console.error('获取模型信息失败：', err)
  } finally {
    loading.value = false
  }
}

const onFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
}

const testVideoUpload = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  error.value = ''
  try {
    const response = await recognizeEmotion(selectedFile.value)
    uploadResult.value = JSON.stringify(response.data, null, 2)
    console.log('视频上传测试结果：', response.data)
  } catch (err) {
    error.value = `视频上传测试失败: ${err.message}`
    console.error('视频上传测试失败：', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.api-test-page {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.api-test-page__container {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-section {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.test-section h3 {
  margin-top: 0;
  color: #374151;
}

button {
  background: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 1rem;
}

button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background: #2563eb;
}

.result {
  margin-top: 1rem;
  padding: 1rem;
  background: #f3f4f6;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.result pre {
  margin: 0;
  white-space: pre-wrap;
  font-size: 0.9rem;
}

.error {
  color: #ef4444;
  background: #fef2f2;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.back-button {
  margin-top: 2rem;
  text-align: center;
}

input[type="file"] {
  margin-bottom: 1rem;
  display: block;
}
</style> 
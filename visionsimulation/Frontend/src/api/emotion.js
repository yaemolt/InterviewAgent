import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API请求：', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求拦截器错误：', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应：', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('API响应错误：', error)
    if (error.code === 'ERR_NETWORK') {
      console.error('网络连接失败，请检查后端服务是否启动')
    } else if (error.code === 'ECONNABORTED') {
      console.error('请求超时，请稍后重试')
    }
    return Promise.reject(error)
  }
)

/**
 * 发送视频片段到后端进行情绪识别
 * @param {Blob} videoBlob - 视频blob数据
 * @returns {Promise<AxiosResponse>} API响应
 */
export const recognizeEmotion = async (videoBlob) => {
  try {
    const formData = new FormData()
    
    // 根据blob类型确定文件扩展名
    let filename = 'emotion_clip.mp4'
    if (videoBlob.type) {
      if (videoBlob.type.includes('webm')) {
        filename = 'emotion_clip.webm'
      } else if (videoBlob.type.includes('mp4')) {
        filename = 'emotion_clip.mp4'
      }
    }
    
    console.log(`📤 发送视频文件: ${filename}, 类型: ${videoBlob.type}, 大小: ${videoBlob.size} bytes`)
    formData.append('video', videoBlob, filename)
    
    const response = await api.post('/emotions/analyze', formData)
    return response
  } catch (error) {
    console.error('情绪识别API调用失败：', error)
    
    if (error.response) {
      // 服务器响应错误
      console.error('服务器响应:', error.response.data)
      throw new Error(`服务器错误: ${error.response.status} - ${error.response.data?.response || error.response.statusText}`)
    } else if (error.request) {
      // 网络错误
      throw new Error('网络连接失败，请检查网络')
    } else {
      // 其他错误
      throw new Error('请求失败，请重试')
    }
  }
}

/**
 * 检查API健康状态
 * @returns {Promise<AxiosResponse>} API响应
 */
export const checkAPIHealth = async () => {
  try {
    const response = await api.get('/health')
    return response
  } catch (error) {
    console.error('健康检查失败：', error)
    throw error
  }
}

/**
 * 使用虚拟数据测试API
 * @returns {Promise<AxiosResponse>} API响应
 */
export const testAPI = async () => {
  try {
    const response = await api.post('/emotions/test')
    return response
  } catch (error) {
    console.error('API测试失败：', error)
    throw error
  }
}

/**
 * 获取可用模型列表
 * @returns {Promise<AxiosResponse>} API响应
 */
export const getAvailableModels = async () => {
  try {
    const response = await api.get('/models')
    return response
  } catch (error) {
    console.error('获取模型列表失败：', error)
    throw error
  }
}

export default api 
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
    formData.append('video', videoBlob, 'emotion_clip.webm')
    
    const response = await api.post('/face/emotionRecognition', formData)
    return response
  } catch (error) {
    console.error('情绪识别API调用失败：', error)
    
    if (error.response) {
      // 服务器响应错误
      throw new Error(`服务器错误: ${error.response.status}`)
    } else if (error.request) {
      // 网络错误
      throw new Error('网络连接失败，请检查网络')
    } else {
      // 其他错误
      throw new Error('请求失败，请重试')
    }
  }
}

export default api 
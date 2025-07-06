import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api' : '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 在这里可以添加认证token等
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    console.log('发送API请求:', config.url, config.data)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.status, response.data)
    return response
  },
  (error) => {
    console.error('API请求错误：', error)
    return Promise.reject(error)
  }
)

/**
 * 发送聊天消息
 * @param {string} message - 用户消息
 * @returns {Promise} - 返回Promise对象
 */
/**
 * 提交简历信息并获取面试官第一个问题
 * @param {Object} resumeData - 简历数据
 * @returns {Promise} - 返回Promise对象
 */
export const submitResume = async (resumeData) => {
  try {
    const response = await api.post('/interview/start', {
      resume: resumeData,
      timestamp: Date.now()
    })
    return response
  } catch (error) {
    console.error('提交简历失败：', error)
    
    // 网络连接错误时的处理
    if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
      throw new Error('无法连接到服务器，请检查后端服务是否已启动（端口5000）')
    }
    
    // 超时错误
    if (error.code === 'ECONNABORTED') {
      throw new Error('请求超时，请稍后重试')
    }
    
    // 服务器错误
    if (error.response) {
      const status = error.response.status
      const errorMsg = error.response.data?.error || '服务器响应错误'
      throw new Error(`服务器错误 (${status}): ${errorMsg}`)
    }
    
    throw error
  }
}

/**
 * 发送聊天消息
 * @param {string} message - 用户消息
 * @returns {Promise} - 返回Promise对象
 */
export const sendMessage = async (message) => {
  try {
    const response = await api.post('/chat', {
      message: message,
      timestamp: Date.now()
    })
    return response
  } catch (error) {
    console.error('发送消息失败：', error)
    
    // 网络连接错误时的处理
    if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
      throw new Error('无法连接到服务器，请检查后端服务是否已启动（端口5000）')
    }
    
    // 超时错误
    if (error.code === 'ECONNABORTED') {
      throw new Error('请求超时，请稍后重试')
    }
    
    // 服务器错误
    if (error.response) {
      const status = error.response.status
      const errorMsg = error.response.data?.error || '服务器响应错误'
      throw new Error(`服务器错误 (${status}): ${errorMsg}`)
    }
    
    throw error
  }
}

/**
 * 生成语音文件
 * @param {string} text - 需要转换为语音的文本
 * @returns {Promise} - 返回Promise对象，成功时返回音频Blob
 */
export const generateSpeech = async (text) => {
  try {
    const response = await api.post('/tts/generate', {
      text: text
    }, {
      responseType: 'blob' // 重要：指定响应类型为blob
    })
    
    // 返回音频Blob对象
    return new Blob([response.data], { type: 'audio/mpeg' })
  } catch (error) {
    console.error('语音生成失败：', error)
    
    // 网络连接错误时的处理
    if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
      throw new Error('无法连接到服务器，请检查后端服务是否已启动')
    }
    
    // 超时错误
    if (error.code === 'ECONNABORTED') {
      throw new Error('语音生成超时，请稍后重试')
    }
    
    // 服务器错误
    if (error.response) {
      const status = error.response.status
      
      // 尝试解析错误消息（对于blob响应需要特殊处理）
      if (error.response.data instanceof Blob) {
        try {
          const errorText = await error.response.data.text()
          const errorData = JSON.parse(errorText)
          throw new Error(`语音生成失败 (${status}): ${errorData.error || '未知错误'}`)
        } catch (parseError) {
          throw new Error(`语音生成失败 (${status}): 服务器响应格式错误`)
        }
      } else {
        const errorMsg = error.response.data?.error || '语音生成失败'
        throw new Error(`语音生成失败 (${status}): ${errorMsg}`)
      }
    }
    
    throw error
  }
}

/**
 * 检查TTS服务状态
 * @returns {Promise} - 返回Promise对象
 */
export const checkTTSStatus = async () => {
  try {
    const response = await api.get('/tts/status')
    return response
  } catch (error) {
    console.error('检查TTS状态失败：', error)
    throw error
  }
}

/**
 * 语音识别 - 将音频转为文字
 * @param {Blob} audioBlob - 音频Blob对象
 * @returns {Promise} - 返回Promise对象，成功时返回识别的文字
 */
export const recognizeSpeech = async (audioBlob) => {
  try {
    // 创建FormData对象
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')
    
    const response = await api.post('/asr/recognize', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000 // 语音识别可能需要更长时间
    })
    
    return response.data
  } catch (error) {
    console.error('语音识别失败：', error)
    
    // 网络连接错误时的处理
    if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
      throw new Error('无法连接到服务器，请检查后端服务是否已启动')
    }
    
    // 超时错误
    if (error.code === 'ECONNABORTED') {
      throw new Error('语音识别超时，请稍后重试')
    }
    
    // 服务器错误
    if (error.response) {
      const status = error.response.status
      const errorMsg = error.response.data?.error || '语音识别失败'
      throw new Error(`语音识别失败 (${status}): ${errorMsg}`)
    }
    
    throw error
  }
}

/**
 * 检查ASR服务状态
 * @returns {Promise} - 返回Promise对象
 */
export const checkASRStatus = async () => {
  try {
    const response = await api.get('/asr/status')
    return response
  } catch (error) {
    console.error('检查ASR状态失败：', error)
    throw error
  }
}

export default api 
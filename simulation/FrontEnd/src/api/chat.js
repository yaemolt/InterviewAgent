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

export default api 
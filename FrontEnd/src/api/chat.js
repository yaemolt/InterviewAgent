import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8080/api',
  timeout: 10000,
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
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
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
export const sendMessage = async (message) => {
  try {
    const response = await api.post('/chat', {
      message: message,
      timestamp: Date.now()
    })
    return response
  } catch (error) {
    // 模拟响应（用于开发测试）
    if (error.code === 'ERR_NETWORK') {
      console.warn('网络连接失败，使用模拟响应')
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              message: `您刚才说："${message}"。这是一个模拟回复，请配置后端API接口。`,
              timestamp: Date.now()
            }
          })
        }, 1000)
      })
    }
    throw error
  }
}

export default api 
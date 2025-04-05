import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// 创建axios实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000
})

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(config => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

// 响应拦截器 - 处理错误
apiClient.interceptors.response.use(
  response => response,
  error => {
    // 处理401错误 - 认证失败
    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API服务
export const api = {
  // 通用CRUD操作
  async get(endpoint, params = {}) {
    try {
      const response = await apiClient.get(endpoint, { params })
      return response.data
    } catch (error) {
      console.error(`GET ${endpoint} 失败:`, error)
      throw error
    }
  },
  
  async post(endpoint, data = {}) {
    try {
      const response = await apiClient.post(endpoint, data)
      return response.data
    } catch (error) {
      console.error(`POST ${endpoint} 失败:`, error)
      throw error
    }
  },
  
  async put(endpoint, data = {}) {
    try {
      const response = await apiClient.put(endpoint, data)
      return response.data
    } catch (error) {
      console.error(`PUT ${endpoint} 失败:`, error)
      throw error
    }
  },
  
  async delete(endpoint) {
    try {
      const response = await apiClient.delete(endpoint)
      return response.data
    } catch (error) {
      console.error(`DELETE ${endpoint} 失败:`, error)
      throw error
    }
  },
  
  // 认证相关
  auth: {
    async login(credentials) {
      return await api.post('/auth/login', credentials)
    },
    
    async register(userData) {
      return await api.post('/auth/register', userData)
    },
    
    async getProfile() {
      return await api.get('/auth/profile')
    }
  },
  
  // 插件相关
  plugins: {
    async getAll() {
      return await api.get('/plugins')
    },
    
    async getById(id) {
      return await api.get(`/plugins/${id}`)
    },
    
    async toggleStatus(id, active) {
      return await api.put(`/plugins/${id}/status`, { active })
    },
    
    async install(pluginData) {
      return await api.post('/plugins/install', pluginData)
    }
  },
  
  // LLM服务相关
  llm: {
    async getServices() {
      return await api.get('/llm/services')
    },
    
    async testConnection(config) {
      return await api.post('/llm/test-connection', config)
    },
    
    async chat(model, messages) {
      return await api.post('/llm/chat', { model, messages })
    }
  },
  
  // 系统相关
  system: {
    async getStatus() {
      return await api.get('/system/status')
    },
    
    async getLogs(filters = {}) {
      return await api.get('/system/logs', filters)
    },
    
    async clearCache() {
      return await api.post('/system/clear-cache')
    }
  }
}

export default api

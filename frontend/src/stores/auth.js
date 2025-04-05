import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    userFullName: (state) => state.user ? `${state.user.firstName} ${state.user.lastName}` : '游客'
  },
  
  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      
      try {
        // 在实际应用中，这里应该调用API登录
        // const response = await api.post('/auth/login', credentials)
        
        // 模拟登录响应
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // 检查凭据
        if (credentials.email === 'admin@aivk.com' && credentials.password === 'password') {
          const userData = {
            id: 1,
            email: 'admin@aivk.com',
            firstName: '管理员',
            lastName: '',
            role: 'admin',
            avatar: null
          }
          
          const token = 'fake-jwt-token-' + Math.random().toString(36).substring(2)
          
          // 保存数据到状态
          this.setUserData(userData, token)
          
          return { success: true }
        } else {
          throw new Error('邮箱或密码不正确')
        }
      } catch (error) {
        this.error = error.message || '登录失败，请稍后重试'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    async register(userData) {
      this.loading = true
      this.error = null
      
      try {
        // 在实际应用中，这里应该调用API注册
        // const response = await api.post('/auth/register', userData)
        
        // 模拟注册响应
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 模拟注册成功
        const newUser = {
          id: Date.now(),
          email: userData.email,
          firstName: userData.firstName,
          lastName: userData.lastName,
          role: 'user',
          avatar: null
        }
        
        const token = 'fake-jwt-token-' + Math.random().toString(36).substring(2)
        
        // 保存数据到状态
        this.setUserData(newUser, token)
        
        return { success: true }
      } catch (error) {
        this.error = error.message || '注册失败，请稍后重试'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    setUserData(user, token) {
      this.user = user
      this.token = token
      
      // 保存token到localStorage以便持久化
      localStorage.setItem('token', token)
    },
    
    async logout() {
      // 在实际应用中，这里可能需要调用API进行登出
      // await api.post('/auth/logout')
      
      // 清除状态
      this.user = null
      this.token = null
      
      // 清除localStorage中的token
      localStorage.removeItem('token')
    },
    
    async fetchUserProfile() {
      if (!this.token) return
      
      this.loading = true
      
      try {
        // 在实际应用中，这里应该调用API获取用户信息
        // const response = await api.get('/auth/profile')
        
        // 模拟请求延迟
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 模拟用户数据
        this.user = {
          id: 1,
          email: 'admin@aivk.com',
          firstName: '管理员',
          lastName: '',
          role: 'admin',
          avatar: null
        }
      } catch (error) {
        console.error('获取用户信息失败', error)
        // 如果获取用户信息失败，可能是token已过期
        this.logout()
      } finally {
        this.loading = false
      }
    }
  }
})

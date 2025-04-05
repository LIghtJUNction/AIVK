<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-content card">
        <div class="auth-header">
          <div class="auth-logo">
            <img src="@/assets/images/aivk-logo.svg" alt="AIVK Logo">
          </div>
          <h1 class="auth-title">登录到AIVK</h1>
        </div>
        
        <form @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="email">邮箱</label>
            <div class="input-with-icon">
              <i class="fas fa-envelope"></i>
              <input 
                type="email" 
                id="email" 
                v-model="email" 
                class="input-field" 
                placeholder="your@email.com"
                required
              >
            </div>
          </div>
          
          <div class="form-group">
            <label for="password">密码</label>
            <div class="input-with-icon">
              <i class="fas fa-lock"></i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="password" 
                v-model="password" 
                class="input-field" 
                placeholder="输入密码"
                required
              >
              <button 
                type="button" 
                class="toggle-password" 
                @click="showPassword = !showPassword"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          
          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" v-model="rememberMe">
              <span>记住我</span>
            </label>
            
            <a href="#" class="forgot-password">忘记密码?</a>
          </div>
          
          <div v-if="error" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ error }}
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary login-btn" 
            :disabled="loading"
          >
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            <span v-else>登录</span>
          </button>
          
          <div class="auth-divider">
            <span>或</span>
          </div>
          
          <div class="social-login">
            <button type="button" class="social-btn google">
              <i class="fab fa-google"></i>
              <span>使用Google登录</span>
            </button>
            
            <button type="button" class="social-btn github">
              <i class="fab fa-github"></i>
              <span>使用GitHub登录</span>
            </button>
          </div>
        </form>
        
        <div class="auth-footer">
          <p>还没有账号? <router-link to="/register" class="auth-link">立即注册</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMainStore } from '@/stores/main'

const router = useRouter()
const authStore = useAuthStore()
const mainStore = useMainStore()

// 表单数据
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)

// 状态
const loading = ref(false)
const error = ref('')

// 处理登录
async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    const result = await authStore.login({
      email: email.value,
      password: password.value
    })
    
    if (result.success) {
      mainStore.addNotification({
        message: '登录成功，欢迎回来!',
        type: 'success'
      })
      
      // 登录成功后重定向到首页或来源页面
      router.push('/')
    } else {
      error.value = result.error
    }
  } catch (err) {
    error.value = '登录失败，请稍后重试'
    console.error('登录错误:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-gradient);
  padding: 20px;
  width: 100%;
}

.auth-container {
  width: 100%;
  max-width: 450px;
  margin: 0 auto;
}

.auth-content {
  padding: 40px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  border-radius: var(--border-radius);
  background-color: var(--card-bg);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-logo {
  margin-bottom: 20px;
}

.auth-logo img {
  width: 80px;
  height: 80px;
}

.auth-title {
  font-size: 24px;
  margin-bottom: 10px;
}

.auth-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.input-with-icon {
  position: relative;
}

.input-with-icon i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.input-with-icon .input-field {
  padding-left: 40px;
}

.toggle-password {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.forgot-password {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 14px;
}

.forgot-password:hover {
  text-decoration: underline;
}

.error-message {
  padding: 10px;
  background-color: rgba(255, 94, 87, 0.1);
  border-radius: var(--border-radius);
  color: var(--danger-color);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.auth-divider {
  position: relative;
  text-align: center;
  margin: 20px 0;
}

.auth-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 45%;
  height: 1px;
  background-color: var(--border-color);
}

.auth-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  right: 0;
  width: 45%;
  height: 1px;
  background-color: var(--border-color);
}

.auth-divider span {
  background-color: var(--card-bg);
  padding: 0 15px;
  position: relative;
  z-index: 1;
  color: var(--text-secondary);
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  background-color: var(--bg-tertiary);
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.social-btn:hover {
  transform: translateY(-2px);
}

.social-btn.google:hover {
  background-color: rgba(234, 67, 53, 0.1);
  border-color: #ea4335;
}

.social-btn.github:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: #ffffff;
}

.auth-footer {
  text-align: center;
  color: var(--text-secondary);
}

.auth-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.auth-link:hover {
  text-decoration: underline;
}

/* 响应式调整 */
@media (max-width: 576px) {
  .auth-content {
    padding: 30px 20px;
  }
  
  .auth-page {
    padding: 15px;
  }
}
</style>

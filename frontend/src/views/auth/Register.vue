<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-content card">
        <div class="auth-header">
          <div class="auth-logo">
            <img src="@/assets/images/aivk-logo.svg" alt="AIVK Logo">
          </div>
          <h1 class="auth-title">创建AIVK账号</h1>
        </div>
        
        <form @submit.prevent="handleRegister" class="auth-form">
          <div class="form-grid">
            <div class="form-group">
              <label for="firstName">名字</label>
              <div class="input-with-icon">
                <i class="fas fa-user"></i>
                <input 
                  type="text" 
                  id="firstName" 
                  v-model="firstName" 
                  class="input-field" 
                  placeholder="输入名字"
                  required
                >
              </div>
            </div>
            
            <div class="form-group">
              <label for="lastName">姓氏</label>
              <div class="input-with-icon">
                <i class="fas fa-user"></i>
                <input 
                  type="text" 
                  id="lastName" 
                  v-model="lastName" 
                  class="input-field" 
                  placeholder="输入姓氏"
                >
              </div>
            </div>
          </div>
          
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
                placeholder="至少6位字符"
                minlength="6"
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
          
          <div class="form-group">
            <label for="confirmPassword">确认密码</label>
            <div class="input-with-icon">
              <i class="fas fa-lock"></i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                id="confirmPassword" 
                v-model="confirmPassword" 
                class="input-field" 
                placeholder="再次输入密码"
                minlength="6"
                required
              >
            </div>
          </div>
          
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="agreeTerms" required>
              <span>我已阅读并同意 <a href="#" class="auth-link">服务条款</a> 和 <a href="#" class="auth-link">隐私政策</a></span>
            </label>
          </div>
          
          <div v-if="error" class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            {{ error }}
          </div>
          
          <button 
            type="submit" 
            class="btn btn-primary register-btn" 
            :disabled="loading || !agreeTerms || password !== confirmPassword"
          >
            <i v-if="loading" class="fas fa-spinner fa-spin"></i>
            <span v-else>注册</span>
          </button>
        </form>
        
        <div class="auth-footer">
          <p>已有账号? <router-link to="/login" class="auth-link">返回登录</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMainStore } from '@/stores/main'

const router = useRouter()
const authStore = useAuthStore()
const mainStore = useMainStore()

// 表单数据
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const agreeTerms = ref(false)
const showPassword = ref(false)

// 状态
const loading = ref(false)
const error = ref('')

// 监听密码一致性
watch([password, confirmPassword], ([newPassword, newConfirmPassword]) => {
  if (newConfirmPassword && newPassword !== newConfirmPassword) {
    error.value = '两次输入的密码不一致'
  } else {
    error.value = ''
  }
})

// 处理注册
async function handleRegister() {
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const result = await authStore.register({
      firstName: firstName.value,
      lastName: lastName.value,
      email: email.value,
      password: password.value
    })
    
    if (result.success) {
      mainStore.addNotification({
        message: '注册成功，欢迎加入AIVK!',
        type: 'success'
      })
      
      // 注册成功后重定向到首页
      router.push('/')
    } else {
      error.value = result.error
    }
  } catch (err) {
    error.value = '注册失败，请稍后重试'
    console.error('注册错误:', err)
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
  max-width: 500px;
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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
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

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input {
  margin-top: 4px;
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

.register-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
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
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>

<template>
  <div class="profile-view">
    <h1 class="page-title">个人中心</h1>
    
    <div class="profile-container">
      <div class="profile-sidebar card">
        <div class="user-info">
          <div class="user-avatar">
            <div v-if="user.avatar" class="avatar-image">
              <img :src="user.avatar" :alt="user.firstName">
            </div>
            <div v-else class="avatar-placeholder">{{ userInitials }}</div>
            
            <button class="change-avatar-btn">
              <i class="fas fa-camera"></i>
            </button>
          </div>
          
          <div class="user-details">
            <h2 class="user-name">{{ userFullName }}</h2>
            <div class="user-role">
              <span class="role-badge">{{ user.role === 'admin' ? '管理员' : '用户' }}</span>
            </div>
            <div class="user-email">{{ user.email }}</div>
          </div>
          
          <div class="user-actions">
            <button class="btn btn-primary" @click="editProfile">
              <i class="fas fa-edit"></i> 编辑资料
            </button>
          </div>
        </div>
        
        <div class="profile-menu">
          <div 
            v-for="(section, index) in profileSections" 
            :key="index"
            class="menu-item"
            :class="{ active: activeSection === section.id }"
            @click="activeSection = section.id"
          >
            <i :class="`fas ${section.icon}`"></i>
            <span>{{ section.name }}</span>
          </div>
        </div>
      </div>
      
      <div class="profile-content card">
        <!-- 概览 -->
        <div v-if="activeSection === 'overview'" class="profile-section">
          <h3 class="section-title">概览</h3>
          
          <div class="overview-stats">
            <div class="stat-item">
              <div class="stat-value">{{ activityStats.totalChats }}</div>
              <div class="stat-label">对话总数</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-value">{{ activityStats.lastActive }}</div>
              <div class="stat-label">上次活动</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-value">{{ activityStats.favoriteModel }}</div>
              <div class="stat-label">常用模型</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-value">{{ activityStats.apiCalls }}</div>
              <div class="stat-label">API调用</div>
            </div>
          </div>
          
          <div class="section-divider"></div>
          
          <div class="recent-activities">
            <h4>最近活动</h4>
            
            <div v-if="recentActivities.length === 0" class="no-data">
              暂无活动记录
            </div>
            
            <div v-else class="activities-list">
              <div 
                v-for="(activity, index) in recentActivities" 
                :key="index" 
                class="activity-item"
              >
                <div class="activity-icon">
                  <i :class="getActivityIcon(activity.type)"></i>
                </div>
                <div class="activity-content">
                  <div class="activity-title">{{ activity.title }}</div>
                  <div class="activity-time">{{ activity.time }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 我的对话 -->
        <div v-else-if="activeSection === 'chats'" class="profile-section">
          <h3 class="section-title">我的对话</h3>
          
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="chatSearchQuery" 
              placeholder="搜索对话..." 
              class="search-input"
            >
          </div>
          
          <div v-if="userChats.length === 0" class="no-data">
            没有找到对话记录
          </div>
          
          <div v-else class="chats-list">
            <div 
              v-for="(chat, index) in filteredChats" 
              :key="index" 
              class="chat-item"
              @click="openChat(chat.id)"
            >
              <div class="chat-model-icon" :style="{ backgroundColor: getModelColor(chat.model) }">
                <i class="fas fa-comments"></i>
              </div>
              
              <div class="chat-details">
                <div class="chat-title">{{ chat.title }}</div>
                <div class="chat-preview">{{ chat.preview }}</div>
                <div class="chat-meta">
                  <span class="chat-time">{{ chat.time }}</span>
                  <span class="chat-model">{{ chat.model }}</span>
                  <span class="chat-messages">{{ chat.messages }}条消息</span>
                </div>
              </div>
              
              <div class="chat-actions">
                <button class="action-btn" @click.stop="deleteChat(chat.id)">
                  <i class="fas fa-trash-alt"></i>
                </button>
                <button class="action-btn" @click.stop="exportChat(chat.id)">
                  <i class="fas fa-download"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 安全与隐私 -->
        <div v-else-if="activeSection === 'security'" class="profile-section">
          <h3 class="section-title">安全与隐私</h3>
          
          <div class="section-group">
            <h4>修改密码</h4>
            
            <form @submit.prevent="changePassword" class="password-form">
              <div class="form-group">
                <label for="current-password">当前密码</label>
                <div class="password-input">
                  <input 
                    :type="showCurrentPassword ? 'text' : 'password'" 
                    id="current-password" 
                    v-model="passwordData.currentPassword" 
                    class="input-field" 
                    required
                  >
                  <button 
                    type="button" 
                    class="toggle-password"
                    @click="showCurrentPassword = !showCurrentPassword"
                  >
                    <i :class="showCurrentPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
              </div>
              
              <div class="form-group">
                <label for="new-password">新密码</label>
                <div class="password-input">
                  <input 
                    :type="showNewPassword ? 'text' : 'password'" 
                    id="new-password" 
                    v-model="passwordData.newPassword" 
                    class="input-field" 
                    required
                    minlength="6"
                  >
                  <button 
                    type="button" 
                    class="toggle-password"
                    @click="showNewPassword = !showNewPassword"
                  >
                    <i :class="showNewPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </div>
              </div>
              
              <div class="form-group">
                <label for="confirm-password">确认新密码</label>
                <div class="password-input">
                  <input 
                    :type="showNewPassword ? 'text' : 'password'" 
                    id="confirm-password" 
                    v-model="passwordData.confirmPassword" 
                    class="input-field" 
                    required
                  >
                </div>
              </div>
              
              <div v-if="passwordError" class="form-error">
                <i class="fas fa-exclamation-circle"></i>
                {{ passwordError }}
              </div>
              
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="isPasswordSubmitting || !canSubmitPassword"
              >
                <i v-if="isPasswordSubmitting" class="fas fa-spinner fa-spin"></i>
                <span v-else>更新密码</span>
              </button>
            </form>
          </div>
          
          <div class="section-divider"></div>
          
          <div class="section-group">
            <h4>登录活动</h4>
            <p class="section-description">以下是您最近的登录活动。如果发现任何可疑活动，请立即修改密码。</p>
            
            <div class="login-activities">
              <div v-for="(login, index) in loginActivities" :key="index" class="login-activity-item">
                <div class="login-activity-icon" :class="login.current ? 'current' : ''">
                  <i class="fas fa-desktop"></i>
                </div>
                <div class="login-activity-details">
                  <div class="login-device">
                    {{ login.device }}
                    <span v-if="login.current" class="current-device">(当前设备)</span>
                  </div>
                  <div class="login-location">{{ login.location }}</div>
                  <div class="login-time">{{ login.time }}</div>
                </div>
                <div class="login-status" :class="login.status">
                  <i v-if="login.status === 'success'" class="fas fa-check-circle"></i>
                  <i v-else class="fas fa-times-circle"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- API密钥 -->
        <div v-else-if="activeSection === 'api-keys'" class="profile-section">
          <h3 class="section-title">API密钥</h3>
          
          <div class="section-description">
            API密钥允许您以编程方式访问AIVK平台的API。请妥善保管您的密钥，不要与他人共享。
          </div>
          
          <div class="section-actions">
            <button class="btn btn-primary" @click="generateNewApiKey">
              <i class="fas fa-plus"></i> 创建新API密钥
            </button>
          </div>
          
          <div v-if="apiKeys.length === 0" class="no-data">
            您还没有创建任何API密钥
          </div>
          
          <div v-else class="api-keys-list">
            <div v-for="(key, index) in apiKeys" :key="index" class="api-key-item">
              <div class="api-key-details">
                <div class="api-key-name">{{ key.name }}</div>
                <div class="api-key-created">创建于: {{ key.created }}</div>
                <div class="api-key-expires">过期时间: {{ key.expires || '永不过期' }}</div>
              </div>
              
              <div class="api-key-value">
                <span v-if="key.visible">{{ key.value }}</span>
                <span v-else>••••••••••••••••••••••••••</span>
                <button 
                  class="toggle-visibility-btn" 
                  @click="toggleApiKeyVisibility(index)"
                  :title="key.visible ? '隐藏' : '显示'"
                >
                  <i :class="key.visible ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
                <button 
                  class="copy-btn" 
                  @click="copyApiKey(key.value)"
                  title="复制"
                >
                  <i class="fas fa-copy"></i>
                </button>
              </div>
              
              <div class="api-key-actions">
                <button class="btn btn-sm" @click="refreshApiKey(index)">
                  <i class="fas fa-sync-alt"></i> 刷新
                </button>
                <button class="btn btn-sm btn-danger" @click="revokeApiKey(index)">
                  <i class="fas fa-trash-alt"></i> 撤销
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑资料弹窗 -->
    <div class="modal" v-if="showEditProfileModal">
      <div class="modal-backdrop" @click="showEditProfileModal = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>编辑个人资料</h3>
          <button class="modal-close" @click="showEditProfileModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveProfile">
            <div class="form-group">
              <label for="profile-firstname">名字</label>
              <input 
                type="text" 
                id="profile-firstname" 
                v-model="profileData.firstName" 
                class="input-field" 
                required
              >
            </div>
            
            <div class="form-group">
              <label for="profile-lastname">姓氏</label>
              <input 
                type="text" 
                id="profile-lastname" 
                v-model="profileData.lastName" 
                class="input-field"
              >
            </div>
            
            <div class="form-group">
              <label for="profile-email">邮箱</label>
              <input 
                type="email" 
                id="profile-email" 
                v-model="profileData.email" 
                class="input-field" 
                required
                disabled
              >
              <div class="form-hint">邮箱地址不可更改</div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn" @click="showEditProfileModal = false">取消</button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="isProfileSubmitting"
              >
                <i v-if="isProfileSubmitting" class="fas fa-spinner fa-spin"></i>
                <span v-else>保存</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 新建API密钥弹窗 -->
    <div class="modal" v-if="showCreateApiKeyModal">
      <div class="modal-backdrop" @click="showCreateApiKeyModal = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>创建新API密钥</h3>
          <button class="modal-close" @click="showCreateApiKeyModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createApiKey">
            <div class="form-group">
              <label for="api-key-name">密钥名称</label>
              <input 
                type="text" 
                id="api-key-name" 
                v-model="newApiKey.name" 
                class="input-field" 
                placeholder="例如：开发环境"
                required
              >
            </div>
            
            <div class="form-group">
              <label for="api-key-expiry">过期时间</label>
              <select id="api-key-expiry" v-model="newApiKey.expiry" class="input-field">
                <option value="never">永不过期</option>
                <option value="30days">30天</option>
                <option value="90days">90天</option>
                <option value="1year">1年</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>权限范围</label>
              <div class="checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="newApiKey.permissions.read">
                  <span>读取权限</span>
                </label>
                
                <label class="checkbox-label">
                  <input type="checkbox" v-model="newApiKey.permissions.write">
                  <span>写入权限</span>
                </label>
                
                <label class="checkbox-label">
                  <input type="checkbox" v-model="newApiKey.permissions.execute">
                  <span>执行权限</span>
                </label>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn" @click="showCreateApiKeyModal = false">取消</button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="isApiKeySubmitting || !newApiKey.name"
              >
                <i v-if="isApiKeySubmitting" class="fas fa-spinner fa-spin"></i>
                <span v-else>创建</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMainStore } from '@/stores/main'

const authStore = useAuthStore()
const mainStore = useMainStore()

// 用户数据
const user = computed(() => authStore.user || {})
const userFullName = computed(() => {
  return [user.value.firstName, user.value.lastName].filter(Boolean).join(' ')
})
const userInitials = computed(() => {
  const firstName = user.value.firstName || ''
  const lastName = user.value.lastName || ''
  return (firstName.charAt(0) + (lastName.charAt(0) || '')).toUpperCase()
})

// 页面状态
const activeSection = ref('overview')
const profileSections = [
  { id: 'overview', name: '概览', icon: 'fa-tachometer-alt' },
  { id: 'chats', name: '我的对话', icon: 'fa-comments' },
  { id: 'security', name: '安全与隐私', icon: 'fa-shield-alt' },
  { id: 'api-keys', name: 'API密钥', icon: 'fa-key' }
]

// 个人概览数据
const activityStats = reactive({
  totalChats: 32,
  lastActive: '今天',
  favoriteModel: 'GPT-4',
  apiCalls: 562
})

// 最近活动
const recentActivities = ref([
  {
    type: 'chat',
    title: '使用GPT-4创建了新对话',
    time: '今天 10:25'
  },
  {
    type: 'login',
    title: '从新设备登录',
    time: '昨天 18:30'
  },
  {
    type: 'api',
    title: '创建了新API密钥',
    time: '3天前'
  },
  {
    type: 'plugin',
    title: '安装了PDF转换器插件',
    time: '上周'
  }
])

// 获取活动图标
function getActivityIcon(type) {
  const icons = {
    'chat': 'fas fa-comments',
    'login': 'fas fa-sign-in-alt',
    'api': 'fas fa-key',
    'plugin': 'fas fa-puzzle-piece'
  }
  return icons[type] || 'fas fa-bell'
}

// 对话相关
const chatSearchQuery = ref('')
const userChats = ref([
  {
    id: 1,
    title: '项目规划讨论',
    preview: '我们讨论了项目的基础设施和用户体验设计方案...',
    model: 'GPT-4',
    time: '今天 10:25',
    messages: 18
  },
  {
    id: 2,
    title: 'Python脚本帮助',
    preview: '请帮我编写一个CSV数据处理脚本...',
    model: 'GPT-3.5 Turbo',
    time: '昨天',
    messages: 12
  },
  {
    id: 3,
    title: '研究论文摘要',
    preview: '请帮我总结一下这篇关于深度学习的论文...',
    model: 'Claude 3 Opus',
    time: '3天前',
    messages: 8
  },
  {
    id: 4,
    title: 'React问题排查',
    preview: '我的组件渲染有问题，错误信息如下...',
    model: 'GPT-4',
    time: '上周',
    messages: 25
  }
])

// 模型颜色
function getModelColor(model) {
  const colors = {
    'GPT-4': 'rgba(0, 168, 255, 0.2)',
    'GPT-3.5 Turbo': 'rgba(5, 196, 107, 0.2)',
    'Claude 3 Opus': 'rgba(127, 17, 224, 0.2)',
    'Claude 3 Sonnet': 'rgba(255, 94, 87, 0.2)',
    'Gemini Pro': 'rgba(255, 168, 1, 0.2)'
  }
  return colors[model] || 'rgba(0, 168, 255, 0.2)'
}

// 过滤用户对话
const filteredChats = computed(() => {
  if (!chatSearchQuery.value) return userChats.value
  
  const query = chatSearchQuery.value.toLowerCase()
  return userChats.value.filter(chat => 
    chat.title.toLowerCase().includes(query) || 
    chat.preview.toLowerCase().includes(query) ||
    chat.model.toLowerCase().includes(query)
  )
})

// 打开对话
function openChat(chatId) {
  // 实际应用中，这里会导航到对话页面
  console.log('打开对话:', chatId)
}

// 删除对话
function deleteChat(chatId) {
  // 实际应用中，这里会调用API删除对话
  console.log('删除对话:', chatId)
  userChats.value = userChats.value.filter(chat => chat.id !== chatId)
  
  mainStore.addNotification({
    type: 'success',
    message: '对话已删除'
  })
}

// 导出对话
function exportChat(chatId) {
  // 实际应用中，这里会调用API导出对话
  console.log('导出对话:', chatId)
  
  mainStore.addNotification({
    type: 'success',
    message: '对话导出成功'
  })
}

// 安全相关
const passwordData = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const passwordError = ref('')
const isPasswordSubmitting = ref(false)

// 是否可以提交密码表单
const canSubmitPassword = computed(() => {
  return (
    passwordData.currentPassword &&
    passwordData.newPassword &&
    passwordData.confirmPassword &&
    passwordData.newPassword === passwordData.confirmPassword &&
    passwordData.newPassword.length >= 6
  )
})

// 更改密码
async function changePassword() {
  if (!canSubmitPassword.value) {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      passwordError.value = '两次输入的密码不一致'
    } else if (passwordData.newPassword.length < 6) {
      passwordError.value = '密码长度必须至少为6位'
    }
    return
  }
  
  isPasswordSubmitting.value = true
  passwordError.value = ''
  
  try {
    // 在实际应用中，这里会调用API更改密码
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 重置表单
    passwordData.currentPassword = ''
    passwordData.newPassword = ''
    passwordData.confirmPassword = ''
    
    mainStore.addNotification({
      type: 'success',
      message: '密码已成功更新'
    })
  } catch (error) {
    passwordError.value = '密码更新失败，请确认当前密码是否正确'
  } finally {
    isPasswordSubmitting.value = false
  }
}

// 登录活动
const loginActivities = ref([
  {
    device: 'Chrome浏览器 (Windows 10)',
    location: '北京, 中国',
    time: '今天 08:25',
    status: 'success',
    current: true
  },
  {
    device: 'Firefox浏览器 (MacOS)',
    location: '上海, 中国',
    time: '昨天 21:40',
    status: 'success',
    current: false
  },
  {
    device: 'Safari浏览器 (iOS)',
    location: '成都, 中国',
    time: '上周一 14:15',
    status: 'success',
    current: false
  },
  {
    device: 'Chrome浏览器 (Android)',
    location: '广州, 中国',
    time: '2周前',
    status: 'failed',
    current: false
  }
])

// API密钥
const apiKeys = ref([
  {
    name: '开发环境',
    value: 'sk_live_ABCdefGHIjkl1234567890MNOPQRSTUVWXYZ',
    created: '2023-10-15',
    expires: null,
    visible: false
  },
  {
    name: '测试环境',
    value: 'sk_test_XYZabcDEFghi0987654321MLKJIHGFEDCBA',
    created: '2023-11-20',
    expires: '2024-11-20',
    visible: false
  }
])
const showCreateApiKeyModal = ref(false)
const isApiKeySubmitting = ref(false)
const newApiKey = reactive({
  name: '',
  expiry: 'never',
  permissions: {
    read: true,
    write: false,
    execute: false
  }
})

// 复制API密钥
function copyApiKey(key) {
  navigator.clipboard.writeText(key).then(() => {
    mainStore.addNotification({
      type: 'success',
      message: 'API密钥已复制到剪贴板'
    })
  }).catch(err => {
    console.error('复制失败:', err)
    mainStore.addNotification({
      type: 'error',
      message: '复制失败，请手动复制'
    })
  })
}

// 切换API密钥可见性
function toggleApiKeyVisibility(index) {
  apiKeys.value[index].visible = !apiKeys.value[index].visible
}

// 刷新API密钥
function refreshApiKey(index) {
  // 实际应用中，这里会调用API刷新密钥
  console.log('刷新API密钥:', index)
  
  // 模拟刷新
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = 'sk_live_'
  for (let i = 0; i < 32; i++) {
    result += letters.charAt(Math.floor(Math.random() * letters.length))
  }
  
  apiKeys.value[index].value = result
  apiKeys.value[index].created = new Date().toISOString().split('T')[0]
  apiKeys.value[index].visible = true
  
  mainStore.addNotification({
    type: 'success',
    message: 'API密钥已刷新'
  })
}

// 撤销API密钥
function revokeApiKey(index) {
  // 实际应用中，这里会调用API撤销密钥
  console.log('撤销API密钥:', index)
  
  apiKeys.value.splice(index, 1)
  
  mainStore.addNotification({
    type: 'success',
    message: 'API密钥已撤销'
  })
}

// 生成新API密钥
function generateNewApiKey() {
  // 重置表单
  newApiKey.name = ''
  newApiKey.expiry = 'never'
  newApiKey.permissions.read = true
  newApiKey.permissions.write = false
  newApiKey.permissions.execute = false
  
  // 显示弹窗
  showCreateApiKeyModal.value = true
}

// 创建API密钥
async function createApiKey() {
  if (!newApiKey.name) return
  
  isApiKeySubmitting.value = true
  
  try {
    // 在实际应用中，这里会调用API创建新密钥
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟创建
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let keyValue = 'sk_live_'
    for (let i = 0; i < 32; i++) {
      keyValue += letters.charAt(Math.floor(Math.random() * letters.length))
    }
    
    let expires = null
    if (newApiKey.expiry === '30days') {
      const date = new Date()
      date.setDate(date.getDate() + 30)
      expires = date.toISOString().split('T')[0]
    } else if (newApiKey.expiry === '90days') {
      const date = new Date()
      date.setDate(date.getDate() + 90)
      expires = date.toISOString().split('T')[0]
    } else if (newApiKey.expiry === '1year') {
      const date = new Date()
      date.setFullYear(date.getFullYear() + 1)
      expires = date.toISOString().split('T')[0]
    }
    
    apiKeys.value.push({
      name: newApiKey.name,
      value: keyValue,
      created: new Date().toISOString().split('T')[0],
      expires: expires,
      visible: true
    })
    
    showCreateApiKeyModal.value = false
    
    mainStore.addNotification({
      type: 'success',
      message: 'API密钥已创建，请保存您的密钥'
    })
  } catch (error) {
    console.error('创建API密钥失败:', error)
    
    mainStore.addNotification({
      type: 'error',
      message: '创建API密钥失败，请稍后重试'
    })
  } finally {
    isApiKeySubmitting.value = false
  }
}

// 编辑个人资料
const showEditProfileModal = ref(false)
const isProfileSubmitting = ref(false)
const profileData = reactive({
  firstName: '',
  lastName: '',
  email: ''
})

// 打开编辑资料弹窗
function editProfile() {
  profileData.firstName = user.value.firstName || ''
  profileData.lastName = user.value.lastName || ''
  profileData.email = user.value.email || ''
  
  showEditProfileModal.value = true
}

// 保存个人资料
async function saveProfile() {
  isProfileSubmitting.value = true
  
  try {
    // 在实际应用中，这里会调用API更新个人资料
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟更新
    authStore.user.firstName = profileData.firstName
    authStore.user.lastName = profileData.lastName
    
    showEditProfileModal.value = false
    
    mainStore.addNotification({
      type: 'success',
      message: '个人资料已更新'
    })
  } catch (error) {
    console.error('更新资料失败:', error)
    
    mainStore.addNotification({
      type: 'error',
      message: '更新资料失败，请稍后重试'
    })
  } finally {
    isProfileSubmitting.value = false
  }
}
</script>

<style scoped>
.profile-view {
  padding-bottom: 40px;
}

.profile-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  margin-top: 20px;
}

.profile-sidebar {
  height: fit-content;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.user-avatar {
  position: relative;
  width: 100px;
  height: 100px;
  margin-bottom: 15px;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 42px;
  color: white;
  font-weight: 500;
}

.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: all var(--transition-speed) ease;
}

.change-avatar-btn:hover {
  transform: scale(1.1);
}

.user-name {
  font-size: 24px;
  margin-bottom: 5px;
}

.user-role {
  margin-bottom: 5px;
}

.role-badge {
  display: inline-block;
  padding: 3px 8px;
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
  border-radius: 12px;
  font-size: 12px;
}

.user-email {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 15px;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.profile-menu {
  padding: 20px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.menu-item:hover {
  background-color: var(--bg-tertiary);
}

.menu-item.active {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
}

.menu-item i {
  width: 20px;
  margin-right: 10px;
  text-align: center;
}

.profile-content {
  padding: 30px;
}

.section-title {
  margin-bottom: 20px;
  font-size: 22px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 5px;
  color: var(--primary-color);
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.section-divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 30px 0;
}

.recent-activities h4,
.section-group h4 {
  font-size: 18px;
  margin-bottom: 15px;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(0, 168, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-size: 16px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  margin-bottom: 5px;
}

.activity-time {
  color: var(--text-secondary);
  font-size: 12px;
}

.search-box {
  position: relative;
  margin-bottom: 20px;
}

.search-box i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.search-input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border-radius: 20px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-color);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(0, 168, 255, 0.1);
}

.chats-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chat-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.chat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.chat-model-icon {
  width: 45px;
  height: 45px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.chat-details {
  flex: 1;
  min-width: 0;
}

.chat-title {
  font-weight: 500;
  margin-bottom: 5px;
}

.chat-preview {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 12px;
  color: var(--text-secondary);
}

.chat-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
  padding: 5px;
}

.action-btn:hover {
  color: var(--primary-color);
}

.no-data {
  padding: 30px;
  text-align: center;
  color: var(--text-secondary);
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
}

.section-description {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.section-actions {
  margin-bottom: 20px;
}

.password-form {
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 5px;
}

.password-input {
  position: relative;
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

.form-error {
  padding: 10px;
  background-color: rgba(255, 94, 87, 0.1);
  color: var(--danger-color);
  border-radius: var(--border-radius);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.login-activities {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.login-activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
}

.login-activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(0, 168, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-size: 16px;
}

.login-activity-icon.current {
  background-color: rgba(5, 196, 107, 0.1);
  color: var(--success-color);
}

.login-activity-details {
  flex: 1;
}

.login-device {
  margin-bottom: 5px;
}

.current-device {
  font-size: 12px;
  color: var(--success-color);
  margin-left: 5px;
}

.login-location,
.login-time {
  color: var(--text-secondary);
  font-size: 12px;
}

.login-status {
  font-size: 20px;
}

.login-status.success {
  color: var(--success-color);
}

.login-status.failed {
  color: var(--danger-color);
}

.api-keys-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.api-key-item {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 20px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
}

.api-key-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.api-key-created,
.api-key-expires {
  color: var(--text-secondary);
  font-size: 14px;
}

.api-key-value {
  font-family: 'Fira Code', monospace;
  background-color: var(--bg-color);
  padding: 10px 15px;
  border-radius: var(--border-radius);
  position: relative;
  overflow-wrap: break-word;
  word-break: break-all;
}

.toggle-visibility-btn,
.copy-btn {
  position: absolute;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color var(--transition-speed) ease;
}

.toggle-visibility-btn {
  right: 40px;
  top: 10px;
}

.copy-btn {
  right: 10px;
  top: 10px;
}

.toggle-visibility-btn:hover,
.copy-btn:hover {
  color: var(--primary-color);
}

.api-key-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}

/* 复选框样式 */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
}

.modal-content {
  position: relative;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 18px;
}

.modal-body {
  padding: 20px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.install-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.install-tab {
  padding: 10px 15px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.install-tab.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

@keyframes modalSlideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* 响应式调整 */
@media (max-width: 992px) {
  .profile-container {
    grid-template-columns: 1fr;
  }
  
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .overview-stats {
    grid-template-columns: 1fr;
  }
  
  .chat-item,
  .activity-item,
  .login-activity-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chat-actions {
    align-self: flex-end;
  }
  
  .modal-content {
    width: 95%;
  }
}
</style>

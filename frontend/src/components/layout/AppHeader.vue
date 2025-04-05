<template>
  <header class="app-header">
    <div class="header-left">
      <button class="toggle-sidebar-btn" @click="$emit('toggle-sidebar')">
        <i class="fas fa-bars"></i>
      </button>
      <div class="search-container">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            placeholder="搜索..." 
            class="search-input"
            v-model="searchQuery"
            @focus="showSearchResults = true"
            @blur="hideSearchResultsDelayed"
          >
          <button v-if="searchQuery" class="clear-search" @click="clearSearch">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="search-results" v-if="showSearchResults && searchQuery">
          <div class="search-results-header">
            搜索结果
          </div>
          <div class="search-results-content">
            <div v-if="filteredResults.length === 0" class="no-results">
              没有找到匹配"{{ searchQuery }}"的结果
            </div>
            <div v-else class="results-list">
              <router-link 
                v-for="result in filteredResults" 
                :key="result.path" 
                :to="result.path"
                class="result-item"
                @click="showSearchResults = false"
              >
                <div class="result-icon">
                  <i :class="`fas ${result.icon}`"></i>
                </div>
                <div class="result-info">
                  <div class="result-title">{{ result.title }}</div>
                  <div class="result-description">{{ result.description }}</div>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="header-right">
      <div class="header-actions">
        <button class="header-action-btn" @click="toggleDarkMode">
          <i :class="`fas ${isDarkMode ? 'fa-sun' : 'fa-moon'}`"></i>
        </button>
        
        <button class="header-action-btn" @click="openNotifications">
          <i class="fas fa-bell"></i>
          <span class="notification-badge" v-if="unreadNotifications > 0">
            {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
          </span>
        </button>
        
        <button class="header-action-btn" @click="startNewChat">
          <i class="fas fa-plus"></i>
        </button>
      </div>
      
      <div class="user-menu" ref="userMenuRef">
        <button class="user-menu-btn" @click="toggleUserMenu">
          <div class="user-avatar" v-if="userAvatar">
            <img :src="userAvatar" alt="User Avatar">
          </div>
          <div class="user-avatar" v-else>
            {{ userInitials }}
          </div>
          <div class="user-info">
            <div class="user-name">{{ userFullName }}</div>
            <div class="user-role">{{ userRole }}</div>
          </div>
          <i class="fas fa-chevron-down menu-arrow"></i>
        </button>
        
        <div class="user-dropdown" v-if="showUserMenu">
          <div class="dropdown-header">
            <div class="dropdown-user-info">
              <div class="dropdown-user-name">{{ userFullName }}</div>
              <div class="dropdown-user-email">{{ userEmail }}</div>
            </div>
          </div>
          
          <div class="dropdown-menu">
            <router-link to="/profile" class="dropdown-item">
              <i class="fas fa-user"></i>
              <span>个人资料</span>
            </router-link>
            
            <router-link to="/settings" class="dropdown-item">
              <i class="fas fa-cog"></i>
              <span>设置</span>
            </router-link>
            
            <router-link to="/profile" class="dropdown-item">
              <i class="fas fa-user"></i>
              <span>个人中心</span>
            </router-link>
            
            <div class="dropdown-divider"></div>
            
            <button class="dropdown-item" @click="logout">
              <i class="fas fa-sign-out-alt"></i>
              <span>退出登录</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMainStore } from '@/stores/main'

const router = useRouter()
const authStore = useAuthStore()
const mainStore = useMainStore()

// 搜索状态
const searchQuery = ref('')
const showSearchResults = ref(false)
let hideSearchTimeout = null

// 用户菜单状态
const showUserMenu = ref(false)
const userMenuRef = ref(null)

// 用户状态
const userFullName = computed(() => authStore.userFullName)
const userInitials = computed(() => {
  const name = userFullName.value
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2)
})
const userAvatar = computed(() => authStore.user?.avatar || null)
const userEmail = computed(() => authStore.user?.email || '')
const userRole = computed(() => {
  const roleMap = {
    'admin': '管理员',
    'user': '用户',
    'guest': '访客'
  }
  return roleMap[authStore.user?.role] || '用户'
})

// 通知数
const unreadNotifications = ref(3)

// 主题模式
const isDarkMode = ref(true)

// 模拟搜索结果
const searchResults = [
  {
    title: '仪表盘',
    description: '系统概览和主要指标',
    path: '/',
    icon: 'fa-chart-line'
  },
  {
    title: '插件管理',
    description: '管理和配置系统插件',
    path: '/plugins',
    icon: 'fa-puzzle-piece'
  },
  {
    title: 'LLM服务',
    description: '配置和监控LLM API服务',
    path: '/llm-services',
    icon: 'fa-brain'
  },
  {
    title: '终端命令',
    description: '执行系统命令和脚本',
    path: '/terminal',
    icon: 'fa-terminal'
  },
  {
    title: '系统日志',
    description: '查看和分析系统日志',
    path: '/logs',
    icon: 'fa-clipboard-list'
  },
  {
    title: '系统设置',
    description: '配置系统参数和偏好',
    path: '/settings',
    icon: 'fa-cog'
  }
]

// 过滤搜索结果
const filteredResults = computed(() => {
  if (!searchQuery.value) return []
  
  const query = searchQuery.value.toLowerCase()
  return searchResults.filter(result => 
    result.title.toLowerCase().includes(query) || 
    result.description.toLowerCase().includes(query)
  )
})

// 清除搜索
function clearSearch() {
  searchQuery.value = ''
}

// 延迟隐藏搜索结果
function hideSearchResultsDelayed() {
  hideSearchTimeout = setTimeout(() => {
    showSearchResults.value = false
  }, 200)
}

// 切换暗/亮模式
function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
  // TODO: 实际应用中这里需要更新全局主题状态
}

// 打开通知面板
function openNotifications() {
  unreadNotifications.value = 0
  // TODO: 实际应用中这里需要打开通知面板
}

// 开始新的聊天
function startNewChat() {
  mainStore.addNotification({
    message: '开始新的聊天...',
    type: 'info'
  })
  // TODO: 实际应用中这里需要开始新的聊天会话
}

// 切换用户菜单
function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

// 处理用户点击其他地方时关闭菜单
function handleClickOutside(event) {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

// 退出登录
async function logout() {
  await authStore.logout()
  mainStore.addNotification({
    message: '您已成功退出登录',
    type: 'info'
  })
  router.push('/login')
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  if (hideSearchTimeout) {
    clearTimeout(hideSearchTimeout)
  }
})
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-sidebar-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 20px;
  cursor: pointer;
  margin-right: 15px;
  transition: color var(--transition-speed) ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.toggle-sidebar-btn:hover {
  color: var(--text-color);
}

.search-container {
  position: relative;
}

.search-box {
  position: relative;
  width: 300px;
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
  height: 36px;
  padding: 0 40px;
  border-radius: 18px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  font-size: 14px;
  transition: all var(--transition-speed) ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: var(--glow-shadow);
  width: 400px;
}

.clear-search {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.search-results {
  position: absolute;
  top: 45px;
  left: 0;
  width: 500px;
  max-width: 100%;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  z-index: 1000;
  overflow: hidden;
}

.search-results-header {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.no-results {
  padding: 20px;
  text-align: center;
  color: var(--text-secondary);
}

.results-list {
  max-height: 350px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
  text-decoration: none;
  transition: background-color var(--transition-speed) ease;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item:hover {
  background-color: var(--bg-tertiary);
  text-decoration: none;
}

.result-icon {
  width: 36px;
  height: 36px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: var(--primary-color);
}

.result-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.result-description {
  font-size: 12px;
  color: var(--text-secondary);
}

.header-right {
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  margin-right: 15px;
}

.header-action-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 16px;
  cursor: pointer;
  margin-left: 15px;
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all var(--transition-speed) ease;
}

.header-action-btn:hover {
  background-color: var(--bg-tertiary);
  color: var(--text-color);
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 18px;
  height: 18px;
  background-color: var(--danger-color);
  color: white;
  font-size: 11px;
  font-weight: bold;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}

.user-menu {
  position: relative;
}

.user-menu-btn {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: var(--border-radius);
  color: var(--text-color);
  transition: background-color var(--transition-speed) ease;
}

.user-menu-btn:hover {
  background-color: var(--bg-tertiary);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  margin: 0 10px;
  text-align: left;
}

.user-name {
  font-weight: 500;
}

.user-role {
  font-size: 12px;
  color: var(--text-secondary);
}

.menu-arrow {
  color: var(--text-secondary);
  font-size: 10px;
  transition: transform var(--transition-speed) ease;
}

.user-menu-btn:hover .menu-arrow,
.user-dropdown:hover + .user-menu-btn .menu-arrow {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: 60px;
  right: 0;
  width: 250px;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  z-index: 1000;
  overflow: hidden;
}

.dropdown-header {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
}

.dropdown-user-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.dropdown-user-email {
  font-size: 12px;
  color: var(--text-secondary);
}

.dropdown-menu {
  padding: 5px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  color: var(--text-color);
  text-decoration: none;
  transition: background-color var(--transition-speed) ease;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 14px;
}

.dropdown-item:hover {
  background-color: var(--bg-tertiary);
  text-decoration: none;
}

.dropdown-item i {
  width: 20px;
  margin-right: 10px;
  color: var(--text-secondary);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 5px 0;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .search-box {
    width: 200px;
  }
  
  .search-input:focus {
    width: 300px;
  }
  
  .search-results {
    width: 400px;
  }
  
  .user-info {
    display: none;
  }
}

@media (max-width: 768px) {
  .search-box {
    width: 150px;
  }
  
  .search-input:focus {
    width: 250px;
  }
  
  .search-results {
    width: 300px;
  }
  
  .header-action-btn {
    margin-left: 10px;
  }
}

@media (max-width: 576px) {
  .search-container {
    display: none;
  }
}
</style>

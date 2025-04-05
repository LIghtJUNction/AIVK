<template>
  <div class="aivk-app" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <template v-if="isAuthRoute">
      <router-view />
    </template>
    
    <template v-else>
      <AppSidebar :collapsed="sidebarCollapsed" @toggle="toggleSidebar" />
      <div class="main-content">
        <AppHeader @toggle-sidebar="toggleSidebar" />
        <div class="content-container">
          <Transition name="fade" mode="out-in">
            <router-view v-slot="{ Component }">
              <component :is="Component" />
            </router-view>
          </Transition>
        </div>
        <AppFooter />
      </div>
    </template>
    
    <AppNotifications />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMainStore } from '@/stores/main'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AppNotifications from '@/components/ui/AppNotifications.vue'

const route = useRoute()
const authStore = useAuthStore()
const mainStore = useMainStore()

// 侧边栏状态
const sidebarCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')

// 计算属性：判断当前是否为认证相关页面
const isAuthRoute = computed(() => {
  return route.path === '/login' || route.path === '/register' || 
         route.path === '/forgot-password' || route.path === '/reset-password'
})

// 切换侧边栏状态
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem('sidebar-collapsed', sidebarCollapsed.value)
}

// 监听路由变化
watch(
  () => route.path,
  () => {
    // 记录最近访问
    if (!isAuthRoute.value) {
      mainStore.addRecentPage(route)
    }
  }
)

// 页面加载时检查登录状态
onMounted(() => {
  // 如果有token但没有用户信息，尝试获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchUserProfile()
  }
  
  // 加载最近访问记录
  mainStore.loadRecentPages()
  
  // 记录当前页面
  if (!isAuthRoute.value) {
    mainStore.addRecentPage(route)
  }
})
</script>

<style>
:root {
  /* 颜色变量 */
  --primary-color: #00A8FF;
  --secondary-color: #642AFF;
  --accent-color: #00D8D6;
  --success-color: #05C46B;
  --warning-color: #FFA801;
  --danger-color: #FF5E57;
  
  /* 暗色主题 */
  --bg-color: #0A0E17;
  --bg-secondary: #12161F;
  --bg-tertiary: #1A1F2C;
  --card-bg: #12161F;
  --text-color: #EDF0F5;
  --text-secondary: #A5B0C4;
  --border-color: #2A3142;
  
  /* 其他 */
  --border-radius: 10px;
  --sidebar-width: 250px;
  --sidebar-collapsed-width: 70px;
  --header-height: 60px;
  --transition-speed: 0.3s;
  --glow-shadow: 0 0 10px rgba(0, 168, 255, 0.3);
  --bg-gradient: linear-gradient(135deg, #0A0E17, #12161F, #0A0E17);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  line-height: 1.5;
}

.aivk-app {
  display: flex;
  height: 100vh;
  background-color: var(--bg-color);
  color: var(--text-color);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: margin-left var(--transition-speed) ease;
  margin-left: var(--sidebar-width);
}

.aivk-app.sidebar-collapsed .main-content {
  margin-left: var(--sidebar-collapsed-width);
}

.content-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-left: 15px; /* 减小与侧边栏的间距 */
}

.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  font-weight: 600;
}

.card {
  background-color: var(--card-bg);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.btn {
  padding: 8px 16px;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  background-color: var(--bg-tertiary);
  color: var(--text-color);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn:hover {
  border-color: var(--primary-color);
  background-color: rgba(0, 168, 255, 0.1);
}

.btn-primary {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: darken(var(--primary-color), 10%);
  border-color: darken(var(--primary-color), 10%);
}

.btn-danger {
  background-color: var(--danger-color);
  border-color: var(--danger-color);
  color: white;
}

.btn-danger:hover {
  background-color: darken(var(--danger-color), 10%);
  border-color: darken(var(--danger-color), 10%);
}

.btn-icon {
  width: 36px;
  height: 36px;
  padding: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-field {
  padding: 10px 15px;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  background-color: var(--bg-tertiary);
  color: var(--text-color);
  width: 100%;
  font-size: 14px;
  transition: border-color var(--transition-speed) ease;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: var(--glow-shadow);
}

a {
  color: var(--primary-color);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Grid Utilities */
.grid {
  display: grid;
  gap: 20px;
}

.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

.grid-4 {
  grid-template-columns: repeat(4, 1fr);
}

/* 响应式调整 */
@media (max-width: 992px) {
  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .main-content {
    margin-left: 0 !important;
  }
  
  .content-container {
    padding-left: 15px; /* 在移动视图中保持一致的内边距 */
  }
}

@media (max-width: 768px) {
  .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
  
  .grid-2 {
    grid-template-columns: 1fr;
  }
  
  .content-container {
    padding: 15px;
  }
}
</style>

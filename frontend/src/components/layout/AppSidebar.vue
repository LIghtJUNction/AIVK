<template>
  <div class="app-sidebar" :class="{ 'collapsed': collapsed, 'mobile-visible': mobileVisible }">
    <div class="sidebar-header">
      <div class="logo">
        <img src="@/assets/images/aivk-logo.svg" alt="AIVK Logo" class="logo-img">
        <span class="logo-text" v-if="!collapsed">AIVK</span>
      </div>
      <button class="toggle-btn" @click="$emit('toggle')">
        <i class="fas fa-chevron-left"></i>
      </button>
    </div>
    
    <div class="sidebar-menu">
      <router-link 
        v-for="item in menuItems" 
        :key="item.path" 
        :to="item.path" 
        class="menu-item" 
        :class="{ 'active': isActive(item) }"
        :title="collapsed ? item.title : ''"
        v-show="!item.meta?.hidden"
        exact-active-class="active"
      >
        <i :class="`fas ${item.meta.icon}`"></i>
        <span class="menu-text">{{ item.title }}</span>
      </router-link>
    </div>
    
    <div class="sidebar-footer">
      <div class="recent-title" v-if="!collapsed">
        <span>最近访问</span>
      </div>
      
      <div class="recent-menu">
        <router-link 
          v-for="(page, index) in recentPages" 
          :key="index"
          :to="page.path" 
          class="menu-item" 
          :class="{ 'active': isActive(page) }"
          :title="collapsed ? page.title : ''"
          v-show="index < 2"
        >
          <i :class="`fas ${page.icon}`"></i>
          <span class="menu-text">{{ page.title }}</span>
        </router-link>
        
        <div v-if="recentPages.length === 0" class="no-recent" :title="collapsed ? '无最近访问' : ''">
          <i class="fas fa-history"></i>
          <span class="menu-text">无最近访问</span>
        </div>
      </div>
    </div>
    
    <div class="mobile-overlay" v-if="mobileVisible" @click="closeMobileMenu"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMainStore } from '@/stores/main'

// 接收props
const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

// 自定义事件
const emit = defineEmits(['toggle'])

const route = useRoute()
const router = useRouter()
const mainStore = useMainStore()

// 移动端菜单状态
const mobileVisible = ref(false)

// 获取路由菜单项
const menuItems = computed(() => {
  return router.options.routes
    .filter(route => !route.meta?.hidden)
    .map(route => ({
      path: route.path,
      title: route.meta?.title || route.name,
      meta: route.meta
    }))
})

// 获取最近访问的页面
const recentPages = computed(() => {
  return mainStore.recentPages
})

// 判断路由是否激活
function isActive(item) {
  return route.path === item.path
}

// 移动端关闭菜单
function closeMobileMenu() {
  mobileVisible.value = false
}

// 监听路由变化以记录最近访问
watch(() => route, (newRoute) => {
  mainStore.addRecentPage(newRoute)
}, { immediate: true, deep: true })

// 页面加载时
onMounted(() => {
  // 加载最近访问记录
  mainStore.loadRecentPages()
  
  // 记录当前页面
  mainStore.addRecentPage(route)
})
</script>

<style scoped>
.app-sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  transition: width var(--transition-speed) ease;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

.app-sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
}

.logo-img {
  height: 40px;
  width: auto;
}

.logo-text {
  margin-left: 10px;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-color);
}

.toggle-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.toggle-btn:hover {
  background-color: var(--primary-color);
  color: white;
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-radius: var(--border-radius);
  text-decoration: none;
  color: var(--text-secondary);
  transition: all var(--transition-speed) ease;
}

.menu-item:hover {
  background-color: var(--bg-tertiary);
  color: var(--text-color);
}

.menu-item.active {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
}

.menu-item i {
  width: 20px;
  margin-right: 10px;
  font-size: 16px;
  text-align: center;
}

.menu-text {
  font-size: 14px;
}

.sidebar-footer {
  margin-top: auto;
  border-top: 1px solid var(--border-color);
  padding: 10px 0;
}

.recent-title {
  padding: 10px 15px;
  font-size: 12px;
  text-transform: uppercase;
  color: var(--text-secondary);
  letter-spacing: 1px;
}

.recent-menu {
  display: flex;
  flex-direction: column;
}

.no-recent {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  color: var(--text-secondary);
  font-size: 14px;
}

.no-recent i {
  width: 20px;
  margin-right: 10px;
  font-size: 16px;
  text-align: center;
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 99;
}

@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    transform: translateX(-100%);
  }
  
  .app-sidebar.mobile-visible {
    transform: translateX(0);
  }
}

@media (max-width: 992px) {
  .app-sidebar {
    transform: translateX(-100%);
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
    z-index: 1000;
  }
  
  .app-sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .app-sidebar.mobile-visible {
    transform: translateX(0);
  }
}
</style>

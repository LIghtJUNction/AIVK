<template>
  <div class="dashboard">
    <h1 class="page-title">仪表盘</h1>
    
    <div class="dashboard-overview">
      <div class="stats-container grid grid-4">
        <div class="stat-card card">
          <div class="stat-icon">
            <i class="fas fa-puzzle-piece"></i>
          </div>
          <div class="stat-content">
            <div class="stat-title">已安装插件</div>
            <div class="stat-value">{{ plugins.length }}</div>
            <div class="stat-info">{{ getActivePluginsCount() }} 个已启用</div>
          </div>
        </div>
        
        <div class="stat-card card">
          <div class="stat-icon">
            <i class="fas fa-brain"></i>
          </div>
          <div class="stat-content">
            <div class="stat-title">LLM 服务</div>
            <div class="stat-value">{{ llmServices.length }}</div>
            <div class="stat-info">{{ getApiCallsCount() }} 次调用</div>
          </div>
        </div>
        
        <div class="stat-card card">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <div class="stat-title">运行时间</div>
            <div class="stat-value">{{ uptime.days }}天</div>
            <div class="stat-info">{{ uptime.hours }}小时 {{ uptime.minutes }}分钟</div>
          </div>
        </div>
        
        <div class="stat-card card">
          <div class="stat-icon">
            <i class="fas fa-microchip"></i>
          </div>
          <div class="stat-content">
            <div class="stat-title">系统资源</div>
            <div class="stat-value">{{ systemStats.cpu }}%</div>
            <div class="stat-info">内存: {{ systemStats.memory }}MB</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="dashboard-main grid">
      <div class="recent-activities card">
        <div class="card-header">
          <h2>最近活动</h2>
          <button class="btn btn-icon" @click="refreshActivities">
            <i class="fas fa-sync-alt"></i>
          </button>
        </div>
        
        <div class="activities-list">
          <div v-if="activities.length === 0" class="no-data">
            暂无活动记录
          </div>
          
          <div v-else v-for="(activity, index) in activities" :key="index" class="activity-item">
            <div class="activity-icon" :class="activity.type">
              <i :class="getActivityIcon(activity.type)"></i>
            </div>
            <div class="activity-content">
              <div class="activity-text">{{ activity.message }}</div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="system-health-container">
        <div class="system-health card">
          <div class="card-header">
            <h2>系统健康</h2>
          </div>
          
          <div class="health-status">
            <div class="status-item">
              <div class="status-label">API 服务</div>
              <div class="status-value">
                <span class="status-badge connected">已连接</span>
              </div>
            </div>
            
            <div class="status-item">
              <div class="status-label">数据库</div>
              <div class="status-value">
                <span class="status-badge connected">已连接</span>
              </div>
            </div>
            
            <div class="status-item">
              <div class="status-label">文件系统</div>
              <div class="status-value">
                <span class="status-badge warning">空间不足</span>
              </div>
            </div>
            
            <div class="status-item">
              <div class="status-label">网络</div>
              <div class="status-value">
                <span class="status-badge connected">正常</span>
              </div>
            </div>
          </div>
          
          <div class="disk-usage">
            <div class="usage-header">
              <div class="usage-title">磁盘使用情况</div>
              <div class="usage-value">{{ diskUsagePercentage }}%</div>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${diskUsagePercentage}%` }"></div>
            </div>
            <div class="usage-details">
              <span>{{ usedSpace }} / {{ totalSpace }}</span>
              <button class="btn btn-sm" @click="clearCache">
                <i class="fas fa-trash-alt"></i> 清理缓存
              </button>
            </div>
          </div>
        </div>
        
        <div class="quick-actions card">
          <div class="card-header">
            <h2>快速操作</h2>
          </div>
          
          <div class="actions-grid">
            <router-link to="/llm-services" class="action-btn">
              <i class="fas fa-brain"></i>
              <span>管理LLM服务</span>
            </router-link>
            
            <router-link to="/plugins" class="action-btn">
              <i class="fas fa-puzzle-piece"></i>
              <span>管理插件</span>
            </router-link>
            
            <router-link to="/settings" class="action-btn">
              <i class="fas fa-cog"></i>
              <span>系统设置</span>
            </router-link>
            
            <router-link to="/terminal" class="action-btn">
              <i class="fas fa-terminal"></i>
              <span>命令终端</span>
            </router-link>
            
            <button class="action-btn" @click="updateCheck">
              <i class="fas fa-sync-alt"></i>
              <span>检查更新</span>
            </button>
            
            <a href="#" target="_blank" class="action-btn">
              <i class="fas fa-question-circle"></i>
              <span>帮助文档</span>
            </a>
          </div>
        </div>
      </div>
    </div>
    
    <div class="recent-plugins card">
      <div class="card-header">
        <h2>插件状态</h2>
        <router-link to="/plugins" class="btn">
          <i class="fas fa-th-list"></i> 查看全部
        </router-link>
      </div>
      
      <div class="plugins-list">
        <div v-if="plugins.length === 0" class="no-data">
          暂无已安装的插件
        </div>
        
        <div v-else v-for="plugin in plugins.slice(0, 4)" :key="plugin.id" class="plugin-item">
          <div class="plugin-icon" :style="{ backgroundColor: plugin.color || 'rgba(0, 168, 255, 0.2)' }">
            <i :class="`fas ${plugin.icon || 'fa-puzzle-piece'}`"></i>
          </div>
          <div class="plugin-info">
            <div class="plugin-name">{{ plugin.name }}</div>
            <div class="plugin-details">v{{ plugin.version || '1.0.0' }} | {{ plugin.author || '未知作者' }}</div>
          </div>
          <div class="plugin-status-toggle">
            <div 
              class="toggle-track" 
              :class="{ active: plugin.active }"
              @click="togglePlugin(plugin.id)"
            >
              <div class="toggle-thumb"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useMainStore } from '@/stores/main'

const store = useMainStore()

// 状态
const plugins = computed(() => store.plugins)
const llmServices = computed(() => store.llmServices)
const activities = computed(() => store.activities)

const uptime = ref({
  days: 2,
  hours: 14,
  minutes: 37
})

const systemStats = ref({
  cpu: 12,
  memory: 876
})

const usedSpace = ref('8.2GB')
const totalSpace = ref('20GB')
const diskUsagePercentage = ref(62)

// 定时更新CPU等数据
let statsInterval = null

// 获取活跃插件数量
function getActivePluginsCount() {
  return plugins.value.filter(p => p.active).length
}

// 获取API调用次数
function getApiCallsCount() {
  return llmServices.value.reduce((total, service) => total + (service.apiCalls || 0), 0)
}

// 获取活动图标
function getActivityIcon(type) {
  const icons = {
    'info': 'fas fa-info-circle',
    'warning': 'fas fa-exclamation-triangle',
    'error': 'fas fa-times-circle',
    'success': 'fas fa-check-circle'
  }
  return icons[type] || icons.info
}

// 刷新活动记录
function refreshActivities() {
  store.fetchActivities()
  store.addNotification({
    message: '活动记录已刷新',
    type: 'info'
  })
}

// 清理缓存
function clearCache() {
  // 实际应用中，这里会调用API清理缓存
  store.addNotification({
    message: '缓存清理成功，释放了 1.5GB 空间',
    type: 'success'
  })
  
  // 模拟更新使用情况
  setTimeout(() => {
    usedSpace.value = '6.7GB'
    diskUsagePercentage.value = 33
  }, 500)
}

// 检查更新
function updateCheck() {
  store.addNotification({
    message: '正在检查更新...',
    type: 'info'
  })
  
  // 模拟检查更新
  setTimeout(() => {
    store.addNotification({
      message: '您已经在使用最新版本',
      type: 'success'
    })
  }, 1500)
}

// 切换插件状态
function togglePlugin(pluginId) {
  store.togglePlugin(pluginId)
}

// 更新系统资源统计
function updateSystemStats() {
  // 实际应用中，这里会从API获取实时数据
  systemStats.value = {
    cpu: Math.floor(Math.random() * 20) + 5,
    memory: Math.floor(Math.random() * 200) + 800
  }
}

onMounted(() => {
  // 初始化数据
  if (plugins.value.length === 0) {
    store.fetchPlugins()
  }
  
  if (llmServices.value.length === 0) {
    store.fetchLLMServices()
  }
  
  if (activities.value.length === 0) {
    store.fetchActivities()
  }
  
  // 定时更新系统资源统计
  statsInterval = setInterval(updateSystemStats, 5000)
})

onBeforeUnmount(() => {
  // 清除定时器
  if (statsInterval) {
    clearInterval(statsInterval)
  }
})
</script>

<style scoped>
.dashboard {
  padding-bottom: 40px;
}

.dashboard-overview {
  margin-bottom: 15px; /* 减小顶部和后续内容的间距 */
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 18px; /* 略微减小内边距使卡片更紧凑 */
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  margin-right: 20px;
}

.stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 28px;
  font-weight: 700;
  margin: 5px 0;
}

.stat-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.dashboard-main {
  grid-template-columns: 1fr 1fr;
  margin-bottom: 15px; /* 减小底部边距 */
  gap: 15px; /* 减小网格间距 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px; /* 减小卡片标题与内容的间距 */
}

.card-header h2 {
  font-size: 22px;
  margin: 0;
}

.activities-list {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.activity-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.activity-icon.info {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
}

.activity-icon.warning {
  background-color: rgba(255, 168, 1, 0.1);
  color: var(--warning-color);
}

.activity-icon.error {
  background-color: rgba(255, 94, 87, 0.1);
  color: var(--danger-color);
}

.activity-icon.success {
  background-color: rgba(5, 196, 107, 0.1);
  color: var(--success-color);
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin-bottom: 5px;
}

.activity-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.no-data {
  color: var(--text-secondary);
  text-align: center;
  padding: 20px;
}

.system-health-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.health-status {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  color: var(--text-secondary);
}

.status-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.connected {
  background-color: rgba(5, 196, 107, 0.1);
  color: var(--success-color);
}

.status-badge.warning {
  background-color: rgba(255, 168, 1, 0.1);
  color: var(--warning-color);
}

.status-badge.error {
  background-color: rgba(255, 94, 87, 0.1);
  color: var(--danger-color);
}

.disk-usage {
  margin-top: 20px;
}

.usage-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.usage-title {
  color: var(--text-secondary);
}

.usage-value {
  font-weight: 500;
}

.progress-bar {
  height: 8px;
  background-color: var(--bg-tertiary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  border-radius: 4px;
}

.usage-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-secondary);
}

.quick-actions {
  flex: 1;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  text-decoration: none;
  color: var(--text-color);
  transition: all var(--transition-speed) ease;
  border: none;
  cursor: pointer;
  font-size: 14px;
  text-align: center;
}

.action-btn i {
  font-size: 24px;
  margin-bottom: 10px;
  color: var(--primary-color);
}

.action-btn:hover {
  background-color: rgba(0, 168, 255, 0.1);
  transform: translateY(-2px);
}

.recent-plugins {
  margin-top: 15px; /* 减小顶部边距 */
}

.plugins-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.plugin-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
}

.plugin-icon {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 15px;
}

.plugin-info {
  flex: 1;
}

.plugin-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.plugin-details {
  font-size: 12px;
  color: var(--text-secondary);
}

.plugin-status-toggle {
  margin-left: 10px;
}

.toggle-track {
  width: 40px;
  height: 20px;
  background-color: var(--bg-tertiary);
  border-radius: 20px;
  position: relative;
  transition: all var(--transition-speed) ease;
  cursor: pointer;
  border: 1px solid var(--border-color);
}

.toggle-track.active {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.toggle-thumb {
  width: 16px;
  height: 16px;
  background-color: var(--text-color);
  border-radius: 50%;
  position: absolute;
  top: 1px;
  left: 2px;
  transition: all var(--transition-speed) ease;
}

.toggle-track.active .toggle-thumb {
  left: 22px;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .plugins-list {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px; /* 减小间距 */
  }
}

@media (max-width: 992px) {
  .dashboard-main {
    grid-template-columns: 1fr;
  }
  
  .system-health-container {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .stat-value {
    font-size: 24px;
  }
  
  .plugins-list {
    grid-template-columns: 1fr;
  }
  
  .health-status {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>

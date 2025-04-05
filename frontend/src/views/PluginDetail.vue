<template>
  <div class="plugin-detail">
    <div class="back-nav">
      <router-link to="/plugins" class="back-link">
        <i class="fas fa-arrow-left"></i> 返回插件列表
      </router-link>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="tech-loader"></div>
      <div class="loading-text">加载插件信息<span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></div>
    </div>
    
    <div v-else-if="error" class="error-container card">
      <div class="error-icon"><i class="fas fa-exclamation-triangle"></i></div>
      <div class="error-message">{{ error }}</div>
      <button class="btn" @click="fetchPluginData">重试</button>
    </div>
    
    <template v-else>
      <div class="plugin-header card">
        <div class="plugin-header-content">
          <div class="plugin-icon" :style="{ backgroundColor: plugin.color || 'rgba(0, 168, 255, 0.2)' }">
            <i :class="`fas ${plugin.icon || 'fa-puzzle-piece'}`"></i>
          </div>
          
          <div class="plugin-info">
            <h1 class="plugin-name">{{ plugin.name }}</h1>
            <div class="plugin-meta">
              <span class="plugin-version">v{{ plugin.version }}</span>
              <span class="plugin-author">作者: {{ plugin.author }}</span>
              <span class="plugin-license">许可证: {{ plugin.license }}</span>
            </div>
            <div class="plugin-status" :class="{ active: plugin.active }">
              {{ plugin.active ? '已启用' : '已禁用' }}
            </div>
          </div>
          
          <div class="plugin-actions">
            <button 
              class="btn" 
              :class="plugin.active ? 'btn-warning' : 'btn-success'"
              @click="togglePlugin"
            >
              <i :class="plugin.active ? 'fas fa-pause' : 'fas fa-play'"></i>
              {{ plugin.active ? '停用' : '启用' }}
            </button>
            <button class="btn btn-danger" @click="showUninstallConfirm = true">
              <i class="fas fa-trash-alt"></i> 卸载
            </button>
          </div>
        </div>
      </div>
      
      <div class="plugin-content">
        <div class="plugin-details card">
          <h2>插件详情</h2>
          <div class="plugin-description">{{ plugin.description }}</div>
          
          <div class="detail-section">
            <h3>功能特性</h3>
            <ul class="features-list">
              <li v-for="(feature, index) in plugin.features" :key="index">
                <i class="fas fa-check"></i> {{ feature }}
              </li>
            </ul>
          </div>
          
          <div class="detail-section">
            <h3>依赖要求</h3>
            <div class="dependencies">
              <div v-for="(version, dep) in plugin.dependencies" :key="dep" class="dependency-item">
                <span class="dependency-name">{{ dep }}</span>
                <span class="dependency-version">{{ version }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="plugin-settings card">
          <div class="card-header">
            <h2>插件设置</h2>
            <div class="settings-actions" v-if="isEditing">
              <button class="btn btn-secondary" @click="cancelEdit">取消</button>
              <button class="btn btn-primary" @click="saveSettings">保存设置</button>
            </div>
            <div class="settings-actions" v-else>
              <button class="btn" @click="startEdit">
                <i class="fas fa-edit"></i> 编辑
              </button>
            </div>
          </div>
          
          <div v-if="!plugin.settings || Object.keys(plugin.settings).length === 0" class="no-settings">
            此插件没有可配置的设置
          </div>
          
          <div v-else class="settings-form" :class="{ 'editing': isEditing }">
            <div 
              v-for="(setting, key) in plugin.settings" 
              :key="key" 
              class="setting-item"
            >
              <div class="setting-label">
                <label :for="`setting-${key}`">{{ setting.label || key }}</label>
                <div class="setting-description" v-if="setting.description">
                  {{ setting.description }}
                </div>
              </div>
              
              <div class="setting-input">
                <!-- 文本输入 -->
                <input 
                  v-if="setting.type === 'string'" 
                  :id="`setting-${key}`"
                  type="text" 
                  v-model="editedSettings[key]"
                  class="input-field"
                  :disabled="!isEditing"
                  :placeholder="setting.placeholder"
                />
                
                <!-- 数字输入 -->
                <input 
                  v-else-if="setting.type === 'number'" 
                  :id="`setting-${key}`"
                  type="number" 
                  v-model.number="editedSettings[key]"
                  class="input-field"
                  :disabled="!isEditing"
                  :min="setting.min"
                  :max="setting.max"
                  :step="setting.step || 1"
                />
                
                <!-- 布尔值开关 -->
                <div v-else-if="setting.type === 'boolean'" class="toggle-switch">
                  <div 
                    class="toggle-track" 
                    :class="{ active: editedSettings[key] }"
                    @click="isEditing && (editedSettings[key] = !editedSettings[key])"
                  >
                    <div class="toggle-thumb"></div>
                  </div>
                </div>
                
                <!-- 选择框 -->
                <select 
                  v-else-if="setting.type === 'select'" 
                  :id="`setting-${key}`"
                  v-model="editedSettings[key]"
                  class="input-field"
                  :disabled="!isEditing"
                >
                  <option 
                    v-for="option in setting.options" 
                    :key="option.value" 
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                
                <!-- 默认/未知类型 -->
                <input 
                  v-else
                  :id="`setting-${key}`"
                  type="text" 
                  v-model="editedSettings[key]"
                  class="input-field"
                  :disabled="!isEditing"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="plugin-logs card">
        <div class="card-header">
          <h2>插件日志</h2>
          <button class="btn btn-icon" @click="refreshLogs" title="刷新日志">
            <i class="fas fa-sync-alt"></i>
          </button>
        </div>
        
        <div class="logs-container">
          <div v-if="logs.length === 0" class="no-logs">
            暂无日志记录
          </div>
          
          <div v-else class="log-entries">
            <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="log.level">
              <div class="log-time">{{ log.timestamp }}</div>
              <div class="log-level">{{ formatLevel(log.level) }}</div>
              <div class="log-message">{{ log.message }}</div>
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <!-- 卸载确认对话框 -->
    <div class="modal" v-if="showUninstallConfirm">
      <div class="modal-backdrop" @click="showUninstallConfirm = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>确认卸载</h3>
          <button class="modal-close" @click="showUninstallConfirm = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>您确定要卸载插件 <strong>{{ plugin.name }}</strong> 吗？</p>
          <p class="warning-text">此操作不可逆，可能会导致依赖此插件的功能失效。</p>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showUninstallConfirm = false">取消</button>
          <button class="btn btn-danger" @click="uninstallPlugin">
            <i class="fas fa-trash-alt"></i> 确认卸载
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useMainStore } from '@/stores/main'
import { pluginApi } from '@/services/api'
import eventBus, { EventType } from '@/services/eventBus'

const route = useRoute()
const router = useRouter()
const store = useMainStore()

// 状态数据
const pluginId = computed(() => route.params.id)
const plugin = ref({})
const loading = ref(true)
const error = ref(null)
const isEditing = ref(false)
const editedSettings = ref({})
const logs = ref([])
const showUninstallConfirm = ref(false)

// 获取插件数据
async function fetchPluginData() {
  loading.value = true
  error.value = null
  
  try {
    // 在实际应用中，这里会通过API获取详细数据
    // const response = await pluginApi.getDetails(pluginId.value)
    // plugin.value = response
    
    // 模拟数据
    const storePlugin = store.plugins.find(p => p.id.toString() === pluginId.value.toString())
    
    if (!storePlugin) {
      error.value = '插件不存在或已被删除'
      return
    }
    
    // 模拟扩展数据
    plugin.value = {
      ...storePlugin,
      version: '1.2.3',
      author: 'AIVK团队',
      license: 'MIT',
      description: '这是一个示例插件，提供了基本的功能和配置选项。',
      features: [
        '支持多种LLM模型接入',
        '提供丰富的API接口',
        '支持自定义配置',
        '高效的数据处理'
      ],
      dependencies: {
        'python': '>=3.8',
        'openai': '>=0.27.0',
        'numpy': '>=1.20.0'
      },
      settings: {
        apiKey: {
          type: 'string',
          label: 'API密钥',
          description: '用于访问服务的API密钥',
          placeholder: '输入您的API密钥',
          value: 'sk-xxxx'
        },
        modelName: {
          type: 'select',
          label: '模型名称',
          description: '选择要使用的模型',
          options: [
            { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
            { value: 'gpt-4', label: 'GPT-4' },
            { value: 'gpt-4-32k', label: 'GPT-4 32K' }
          ],
          value: 'gpt-3.5-turbo'
        },
        maxTokens: {
          type: 'number',
          label: '最大令牌数',
          description: '生成文本的最大长度',
          min: 100,
          max: 8000,
          step: 100,
          value: 2048
        },
        debug: {
          type: 'boolean',
          label: '调试模式',
          description: '启用详细日志记录',
          value: false
        }
      }
    }
    
    // 初始化编辑设置
    initEditSettings()
    
    // 获取日志
    fetchPluginLogs()
  } catch (err) {
    console.error('获取插件详情失败:', err)
    error.value = '获取插件信息失败，请重试'
  } finally {
    loading.value = false
  }
}

// 初始化设置编辑状态
function initEditSettings() {
  if (plugin.value.settings) {
    const settings = {}
    
    // 使用默认值或当前值初始化
    for (const [key, setting] of Object.entries(plugin.value.settings)) {
      settings[key] = setting.value !== undefined ? setting.value : 
                      (setting.default !== undefined ? setting.default : 
                       (setting.type === 'boolean' ? false : 
                        (setting.type === 'number' ? 0 : '')))
    }
    
    editedSettings.value = settings
  }
}

// 检查是否有未保存的更改
function hasUnsavedChanges() {
  if (!isEditing.value) return false
  
  // 比较当前编辑值与原始值
  for (const key in editedSettings.value) {
    if (plugin.value.settings[key] && 
        plugin.value.settings[key].value !== editedSettings.value[key]) {
      return true
    }
  }
  return false
}

// 开始编辑设置
function startEdit() {
  isEditing.value = true
}

// 取消编辑
function cancelEdit() {
  isEditing.value = false
  initEditSettings()
}

// 保存设置
async function saveSettings() {
  try {
    // 在实际应用中，这里会调用API保存设置
    // await pluginApi.updateSettings(pluginId.value, editedSettings.value)
    
    // 模拟保存成功
    console.log('保存设置:', editedSettings.value)
    
    // 更新当前插件设置的值
    for (const key in editedSettings.value) {
      if (plugin.value.settings[key]) {
        plugin.value.settings[key].value = editedSettings.value[key]
      }
    }
    
    isEditing.value = false
    
    // 添加通知
    store.addNotification({
      message: `${plugin.value.name} 设置已更新`,
      type: 'success'
    })
    
    // 添加到日志
    logs.value.unshift({
      timestamp: new Date().toLocaleString(),
      level: 'info',
      message: '插件设置已更新'
    })
  } catch (err) {
    console.error('保存设置失败:', err)
    store.addNotification({
      message: '保存设置失败',
      type: 'error'
    })
  }
}

// 切换插件状态
async function togglePlugin() {
  try {
    store.togglePlugin(plugin.value.id)
    plugin.value.active = !plugin.value.active
    plugin.value.status = plugin.value.active ? '正常运行中' : '已暂停'
    
    // 添加到日志
    logs.value.unshift({
      timestamp: new Date().toLocaleString(),
      level: 'info',
      message: plugin.value.active ? '插件已启用' : '插件已禁用'
    })
  } catch (err) {
    console.error('切换插件状态失败:', err)
    store.addNotification({
      message: '切换插件状态失败',
      type: 'error'
    })
  }
}

// 卸载插件
async function uninstallPlugin() {
  try {
    // 在实际应用中，这里会调用API卸载插件
    // await pluginApi.uninstall(pluginId.value)
    
    // 模拟卸载成功
    console.log('卸载插件:', pluginId.value)
    showUninstallConfirm.value = false
    
    // 添加通知
    store.addNotification({
      message: `${plugin.value.name} 插件已卸载`,
      type: 'success'
    })
    
    // 添加活动记录
    const now = new Date()
    const time = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`
    store.addActivity({
      time,
      type: 'info',
      message: `${plugin.value.name} 插件已卸载`
    })
    
    // 返回插件列表
    router.push('/plugins')
  } catch (err) {
    console.error('卸载插件失败:', err)
    showUninstallConfirm.value = false
    store.addNotification({
      message: '卸载插件失败',
      type: 'error'
    })
  }
}

// 获取插件日志
async function fetchPluginLogs() {
  try {
    // 在实际应用中，这里会调用API获取日志
    // const response = await api.get(`/plugins/${pluginId.value}/logs`)
    // logs.value = response.data
    
    // 模拟日志数据
    logs.value = [
      { timestamp: '2023-12-01 15:42:30', level: 'info', message: '插件已启动' },
      { timestamp: '2023-12-01 15:42:35', level: 'info', message: '连接到API服务器' },
      { timestamp: '2023-12-01 15:43:01', level: 'warning', message: '请求速率接近限制' },
      { timestamp: '2023-12-01 15:45:22', level: 'error', message: 'API请求失败: 超时' },
      { timestamp: '2023-12-01 15:46:30', level: 'info', message: '重新连接成功' }
    ]
  } catch (err) {
    console.error('获取插件日志失败:', err)
  }
}

// 刷新日志
function refreshLogs() {
  fetchPluginLogs()
  
  // 添加模拟新日志条目
  logs.value.unshift({
    timestamp: new Date().toLocaleString(),
    level: 'info',
    message: '日志已刷新'
  })
  
  // 显示通知
  store.addNotification({
    message: '插件日志已刷新',
    type: 'info'
  })
}

// 格式化日志级别
function formatLevel(level) {
  const levelMap = {
    'info': '信息',
    'warning': '警告',
    'error': '错误',
    'debug': '调试'
  }
  return levelMap[level] || level
}

// 添加路由离开守卫
onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges()) {
    const confirm = window.confirm('您有未保存的更改，确定要离开吗？')
    if (confirm) {
      next()
    } else {
      next(false)
    }
  } else {
    next()
  }
})

// 生命周期钩子
onMounted(() => {
  fetchPluginData()
  
  // 订阅相关事件
  const unsubscribe = eventBus.on(EventType.PLUGIN_ERROR, (data) => {
    if (data.pluginId?.toString() === pluginId.value.toString()) {
      logs.value.unshift({
        timestamp: new Date().toLocaleString(),
        level: 'error',
        message: data.message
      })
    }
  })
  
  // 组件卸载时取消订阅
  onBeforeUnmount(() => {
    unsubscribe()
  })
})
</script>

<style scoped>
.plugin-detail {
  padding-bottom: 40px;
}

.back-nav {
  margin-bottom: 20px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  color: var(--text-secondary);
  transition: color var(--transition-speed) ease;
}

.back-link:hover {
  color: var(--primary-color);
}

.back-link i {
  margin-right: 5px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  gap: 20px;
}

.loading-text {
  color: var(--text-secondary);
  font-size: 18px;
}

.error-container {
  text-align: center;
  padding: 40px;
}

.error-icon {
  font-size: 48px;
  color: var(--danger-color);
  margin-bottom: 20px;
}

.error-message {
  margin-bottom: 20px;
  color: var(--text-secondary);
}

.plugin-header {
  margin-bottom: 20px;
}

.plugin-header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.plugin-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  color: var(--primary-color);
}

.plugin-info {
  flex: 1;
}

.plugin-name {
  font-size: 24px;
  margin-bottom: 5px;
}

.plugin-meta {
  display: flex;
  gap: 20px;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 10px;
}

.plugin-status {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
}

.plugin-status.active {
  background-color: rgba(5, 196, 107, 0.2);
  color: var(--success-color);
}

.plugin-actions {
  display: flex;
  gap: 10px;
}

.plugin-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.plugin-description {
  margin-bottom: 20px;
  line-height: 1.6;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h3 {
  margin-bottom: 10px;
  font-size: 18px;
}

.features-list {
  list-style: none;
  padding: 0;
}

.features-list li {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
}

.features-list li i {
  color: var(--success-color);
  margin-right: 10px;
  margin-top: 4px;
}

.dependencies {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.dependency-item {
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
}

.dependency-name {
  font-weight: 500;
}

.dependency-version {
  color: var(--primary-color);
  font-family: monospace;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.settings-form.editing .setting-item {
  background-color: var(--bg-tertiary);
  padding: 15px;
  border-radius: var(--border-radius);
  transition: all var(--transition-speed) ease;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-label label {
  font-weight: 500;
  display: block;
  margin-bottom: 5px;
}

.setting-description {
  font-size: 12px;
  color: var(--text-secondary);
}

.toggle-switch {
  display: inline-block;
  cursor: pointer;
}

.toggle-track {
  width: 40px;
  height: 20px;
  background-color: var(--bg-tertiary);
  border-radius: 20px;
  position: relative;
  transition: all var(--transition-speed) ease;
}

.toggle-track.active {
  background-color: var(--primary-color);
}

.toggle-thumb {
  width: 16px;
  height: 16px;
  background-color: var(--text-color);
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: all var(--transition-speed) ease;
}

.toggle-track.active .toggle-thumb {
  left: 22px;
}

.no-settings,
.no-logs {
  color: var(--text-secondary);
  text-align: center;
  padding: 20px;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
}

.log-entries {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-entry {
  display: flex;
  font-size: 13px;
  padding: 8px 12px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  border-left: 3px solid transparent;
}

.log-entry.info {
  border-left-color: var(--primary-color);
}

.log-entry.warning {
  border-left-color: var(--warning-color);
}

.log-entry.error {
  border-left-color: var(--danger-color);
}

.log-entry.debug {
  border-left-color: var(--accent-color);
}

.log-time {
  width: 150px;
  color: var(--text-secondary);
}

.log-level {
  width: 60px;
  font-weight: 500;
}

.log-entry.info .log-level {
  color: var(--primary-color);
}

.log-entry.warning .log-level {
  color: var(--warning-color);
}

.log-entry.error .log-level {
  color: var(--danger-color);
}

.log-entry.debug .log-level {
  color: var(--accent-color);
}

.log-message {
  flex: 1;
}

/* 模态对话框 */
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
  -webkit-backdrop-filter: blur(5px); /* 添加Safari支持 */
}

.modal-content {
  position: relative;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease;
  padding: 0;
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
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 18px;
  cursor: pointer;
}

.modal-close:hover {
  color: var(--danger-color);
}

.modal-body {
  padding: 20px;
}

.warning-text {
  color: var(--danger-color);
  margin-top: 10px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

@keyframes modalSlideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 响应式布局 */
@media (max-width: 992px) {
  .plugin-content {
    grid-template-columns: 1fr;
  }
  
  .plugin-header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .plugin-actions {
    margin-top: 10px;
  }
}

@media (max-width: 576px) {
  .plugin-meta {
    flex-direction: column;
    gap: 5px;
  }
  
  .log-time {
    width: 80px;
    font-size: 11px;
  }
  
  .log-level {
    width: 40px;
    font-size: 11px;
  }
}
</style>

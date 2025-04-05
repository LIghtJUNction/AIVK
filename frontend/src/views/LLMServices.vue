<template>
  <div class="llm-services">
    <h1 class="page-title">LLM服务</h1>
    
    <div class="services-grid">
      <!-- 服务卡片 -->
      <div 
        v-for="service in llmServices" 
        :key="service.id" 
        class="service-card card"
        :class="{ 'disabled': !service.enabled }"
      >
        <div class="service-header">
          <div class="service-icon">
            <i :class="`fas ${service.icon}`"></i>
          </div>
          <div class="service-info">
            <h2 class="service-name">{{ service.name }}</h2>
            <div class="service-status" :class="service.status">
              {{ formatStatus(service.status) }}
            </div>
          </div>
          <div class="service-actions">
            <button 
              class="toggle-switch"
              @click="toggleService(service.id)"
            >
              <div 
                class="toggle-track" 
                :class="{ active: service.enabled }"
              >
                <div class="toggle-thumb"></div>
              </div>
            </button>
          </div>
        </div>
        
        <div class="service-body">
          <div class="service-stats">
            <div class="stat-item">
              <div class="stat-label">API调用</div>
              <div class="stat-value">{{ service.apiCalls || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">平均响应</div>
              <div class="stat-value">{{ service.avgResponse || '0ms' }}</div>
            </div>
          </div>
          
          <div class="service-buttons">
            <button class="btn" @click="configureService(service.id)">
              <i class="fas fa-cog"></i> 配置
            </button>
            <button class="btn" @click="testService(service.id)">
              <i class="fas fa-vial"></i> 测试
            </button>
          </div>
        </div>
      </div>
      
      <!-- 添加新服务卡片 -->
      <div class="service-card card add-service-card" @click="openAddServiceModal">
        <div class="add-service-content">
          <div class="add-icon">
            <i class="fas fa-plus"></i>
          </div>
          <div class="add-text">添加新LLM服务</div>
        </div>
      </div>
    </div>
    
    <!-- 服务配置模态框 -->
    <div class="modal" v-if="showConfigModal">
      <div class="modal-backdrop" @click="showConfigModal = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>{{ selectedService ? '编辑服务' : '添加服务' }}</h3>
          <button class="modal-close" @click="showConfigModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <form class="config-form" @submit.prevent="saveServiceConfig">
            <div class="form-group">
              <label for="service-name">服务名称</label>
              <input type="text" id="service-name" v-model="serviceConfig.name" class="input-field" required>
            </div>
            
            <div class="form-group">
              <label for="service-api-key">API密钥</label>
              <div class="api-key-input">
                <input 
                  :type="showApiKey ? 'text' : 'password'" 
                  id="service-api-key" 
                  v-model="serviceConfig.apiKey" 
                  class="input-field"
                  required
                >
                <button type="button" class="toggle-visibility" @click="showApiKey = !showApiKey">
                  <i :class="showApiKey ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </div>
            
            <div class="form-group">
              <label for="service-model">默认模型</label>
              <select id="service-model" v-model="serviceConfig.model" class="input-field">
                <option v-for="model in availableModels" :key="model.id" :value="model.id">
                  {{ model.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="service-endpoint">API端点</label>
              <input type="url" id="service-endpoint" v-model="serviceConfig.endpoint" class="input-field">
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="serviceConfig.enabled">
                <span>启用服务</span>
              </label>
            </div>
            
            <div class="form-actions">
              <button type="button" class="btn" @click="showConfigModal = false">取消</button>
              <button type="submit" class="btn btn-primary">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '@/stores/main'

const store = useMainStore()

// 服务列表数据
const llmServices = computed(() => store.llmServices)

// 模态框状态
const showConfigModal = ref(false)
const showApiKey = ref(false)
const selectedService = ref(null)
const serviceConfig = ref({
  name: '',
  apiKey: '',
  model: '',
  endpoint: '',
  enabled: true
})

// 可用模型（实际应用中会根据选择的服务类型动态变化）
const availableModels = ref([
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
  { id: 'gpt-4', name: 'GPT-4' },
  { id: 'gpt-4-32k', name: 'GPT-4 32K' },
  { id: 'claude-2', name: 'Claude 2' },
  { id: 'claude-instant', name: 'Claude Instant' },
  { id: 'gemini-pro', name: 'Gemini Pro' },
  { id: 'llama-2-70b', name: 'Llama 2 70B' }
])

// 格式化服务状态
function formatStatus(status) {
  const statusMap = {
    'connected': '已连接',
    'disconnected': '未连接',
    'error': '连接错误',
    'rate_limited': '速率限制'
  }
  return statusMap[status] || status
}

// 切换服务状态
function toggleService(serviceId) {
  store.toggleLLMService(serviceId)
}

// 配置服务
function configureService(serviceId) {
  const service = llmServices.value.find(s => s.id === serviceId)
  if (service) {
    selectedService.value = service
    serviceConfig.value = {
      name: service.name,
      apiKey: 'sk-••••••••••••••••••••••••', // 实际应用中从安全存储中获取
      model: service.model || availableModels.value[0].id,
      endpoint: service.endpoint || '',
      enabled: service.enabled
    }
    showConfigModal.value = true
  }
}

// 测试服务连接
function testService(serviceId) {
  console.log('测试服务连接:', serviceId)
  // 实际应用中，会发送测试请求到后端
  store.addNotification({
    message: '服务连接测试成功',
    type: 'success'
  })
}

// 打开添加服务模态框
function openAddServiceModal() {
  selectedService.value = null
  serviceConfig.value = {
    name: '',
    apiKey: '',
    model: availableModels.value[0].id,
    endpoint: '',
    enabled: true
  }
  showConfigModal.value = true
}

// 保存服务配置
function saveServiceConfig() {
  console.log('保存服务配置:', serviceConfig.value)
  
  // 在实际应用中，这里会调用API保存配置
  if (selectedService.value) {
    // 更新现有服务
    const service = llmServices.value.find(s => s.id === selectedService.value.id)
    if (service) {
      service.name = serviceConfig.value.name
      service.enabled = serviceConfig.value.enabled
      service.model = serviceConfig.value.model
      service.endpoint = serviceConfig.value.endpoint
      
      store.addNotification({
        message: `${service.name} 配置已更新`,
        type: 'success'
      })
    }
  } else {
    // 添加新服务
    const newService = {
      id: Date.now(),
      name: serviceConfig.value.name,
      enabled: serviceConfig.value.enabled,
      status: 'disconnected',
      icon: 'fa-robot',
      model: serviceConfig.value.model,
      endpoint: serviceConfig.value.endpoint,
      apiCalls: 0,
      avgResponse: '0ms'
    }
    
    // 在实际应用中，这里会通过API添加新服务
    store.llmServices.push(newService)
    
    store.addNotification({
      message: `${newService.name} 服务已添加`,
      type: 'success'
    })
  }
  
  showConfigModal.value = false
}

onMounted(() => {
  store.fetchLLMServices()
})
</script>

<style scoped>
.llm-services {
  padding-bottom: 40px;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.service-card {
  display: flex;
  flex-direction: column;
  min-height: 200px;
}

.service-card.disabled {
  opacity: 0.7;
}

.service-header {
  display: flex;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.service-icon {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  background-color: rgba(0, 168, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--primary-color);
  margin-right: 15px;
}

.service-info {
  flex: 1;
}

.service-name {
  font-size: 18px;
  margin-bottom: 5px;
}

.service-status {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  background-color: var(--bg-tertiary);
}

.service-status.connected {
  background-color: rgba(5, 196, 107, 0.1);
  color: var(--success-color);
}

.service-status.disconnected {
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
}

.service-status.error {
  background-color: rgba(255, 94, 87, 0.1);
  color: var(--danger-color);
}

.service-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-top: 16px;
}

.service-stats {
  display: flex;
  margin-bottom: 20px;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 18px;
  font-weight: 500;
}

.service-buttons {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.service-buttons .btn {
  flex: 1;
}

.add-service-card {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px dashed var(--border-color);
  background: transparent;
  transition: all var(--transition-speed) ease;
}

.add-service-card:hover {
  border-color: var(--primary-color);
  background: rgba(0, 168, 255, 0.05);
}

.add-service-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.add-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--text-secondary);
}

.add-text {
  color: var(--text-secondary);
  font-weight: 500;
}

.toggle-switch {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
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

/* 配置表单样式 */
.config-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.api-key-input {
  position: relative;
}

.toggle-visibility {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-label input {
  margin-right: 10px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

@media (max-width: 768px) {
  .services-grid {
    grid-template-columns: 1fr;
  }
}
</style>

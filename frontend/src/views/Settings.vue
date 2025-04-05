<template>
  <div class="settings-view">
    <h1 class="page-title">系统设置</h1>
    
    <div class="settings-container">
      <div class="settings-sidebar card">
        <div class="settings-nav">
          <div 
            v-for="section in settingSections" 
            :key="section.id" 
            class="nav-item"
            :class="{ active: activeSection === section.id }"
            @click="activeSection = section.id"
          >
            <i :class="`fas ${section.icon}`"></i>
            <span>{{ section.name }}</span>
          </div>
        </div>
      </div>
      
      <div class="settings-content card">
        <!-- 常规设置 -->
        <div v-if="activeSection === 'general'" class="settings-section">
          <h2 class="section-title">常规设置</h2>
          
          <div class="settings-form">
            <div class="form-group">
              <label for="app-language">语言</label>
              <select id="app-language" v-model="settings.language" class="input-field">
                <option value="zh-CN">简体中文</option>
                <option value="en-US">English (US)</option>
                <option value="ja-JP">日本語</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="theme-select">主题</label>
              <select id="theme-select" v-model="settings.theme" class="input-field">
                <option value="dark">深色模式</option>
                <option value="light">浅色模式</option>
                <option value="system">跟随系统</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.autoUpdate">
                <span>自动更新</span>
              </label>
              <div class="form-hint">启用后，系统将在后台自动检查和应用更新</div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.telemetry">
                <span>允许数据收集</span>
              </label>
              <div class="form-hint">帮助我们改进应用程序的使用体验（不会收集个人数据）</div>
            </div>
          </div>
        </div>
        
        <!-- LiteLLM 代理设置 -->
        <div v-else-if="activeSection === 'litellm'" class="settings-section">
          <h2 class="section-title">LiteLLM 代理设置</h2>
          
          <div class="settings-form">
            <div class="form-group">
              <label for="litellm-host">代理服务器地址</label>
              <input 
                type="text" 
                id="litellm-host" 
                v-model="settings.litellm.host" 
                placeholder="http://localhost:8000" 
                class="input-field"
              >
              <div class="form-hint">LiteLLM代理服务器的地址</div>
            </div>
            
            <div class="form-group">
              <label for="litellm-api-key">API密钥（可选）</label>
              <div class="password-input">
                <input 
                  :type="showLiteLLMApiKey ? 'text' : 'password'" 
                  id="litellm-api-key" 
                  v-model="settings.litellm.apiKey" 
                  placeholder="如果LiteLLM代理设置了身份验证，请输入API密钥" 
                  class="input-field"
                >
                <button type="button" class="toggle-visibility" @click="showLiteLLMApiKey = !showLiteLLMApiKey">
                  <i :class="showLiteLLMApiKey ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </div>
            
            <div class="form-group">
              <label for="litellm-timeout">请求超时（秒）</label>
              <input 
                type="number" 
                id="litellm-timeout" 
                v-model="settings.litellm.timeout" 
                min="5" 
                max="300" 
                class="input-field"
              >
            </div>
            
            <div class="form-group">
              <label for="litellm-retry">重试次数</label>
              <input 
                type="number" 
                id="litellm-retry" 
                v-model="settings.litellm.retries" 
                min="0" 
                max="5" 
                class="input-field"
              >
            </div>
            
            <div class="form-group">
              <label for="litellm-fallback-providers">备选LLM提供商</label>
              <select 
                id="litellm-fallback-providers" 
                v-model="settings.litellm.fallbackProviders" 
                multiple 
                class="input-field multiple-select"
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="azure">Azure OpenAI</option>
                <option value="google">Google Gemini</option>
                <option value="mistral">Mistral AI</option>
                <option value="ollama">Ollama</option>
              </select>
              <div class="form-hint">当首选提供商不可用时使用的备选提供商</div>
            </div>
            
            <div class="form-group">
              <label for="litellm-default-model">默认模型</label>
              <select id="litellm-default-model" v-model="settings.litellm.defaultModel" class="input-field">
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="claude-3-opus">Claude 3 Opus</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                <option value="gemini-pro">Gemini Pro</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                <option value="mistral-medium">Mistral Medium</option>
                <option value="llama-3-70b">Llama 3 70B</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.litellm.debugMode">
                <span>调试模式</span>
              </label>
              <div class="form-hint">记录详细的请求和响应日志（生产环境建议禁用）</div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.litellm.logRequests">
                <span>记录请求</span>
              </label>
              <div class="form-hint">记录所有API请求到日志文件</div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.litellm.cacheEnabled">
                <span>启用响应缓存</span>
              </label>
              <div class="form-hint">缓存相同提示的响应，可以节省API调用费用</div>
            </div>
            
            <div v-if="settings.litellm.cacheEnabled" class="form-group sub-options">
              <label for="litellm-cache-ttl">缓存有效期（秒）</label>
              <input 
                type="number" 
                id="litellm-cache-ttl" 
                v-model="settings.litellm.cacheTTL" 
                min="60" 
                max="86400" 
                class="input-field"
              >
            </div>
          </div>
          
          <div class="test-connection-container">
            <button class="btn btn-primary" @click="testLiteLLMConnection">
              <i class="fas fa-plug"></i> 测试连接
            </button>
            <div v-if="litellmConnectionStatus" class="connection-status" :class="litellmConnectionStatus.type">
              {{ litellmConnectionStatus.message }}
            </div>
          </div>
        </div>
        
        <!-- OpenAI Agents设置 -->
        <div v-else-if="activeSection === 'agents'" class="settings-section">
          <h2 class="section-title">OpenAI Agents 设置</h2>
          
          <div class="settings-form">
            <div class="form-group">
              <label for="agents-model">默认Agent模型</label>
              <select id="agents-model" v-model="settings.agents.defaultModel" class="input-field">
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="claude-3-opus">Claude 3 Opus</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
              </select>
              <div class="form-hint">用于创建Agent的默认模型</div>
            </div>
            
            <div class="form-group">
              <label for="agents-temperature">温度</label>
              <input 
                type="range" 
                id="agents-temperature" 
                v-model="settings.agents.temperature" 
                min="0" 
                max="2" 
                step="0.1" 
                class="slider-input"
              >
              <div class="range-value">{{ settings.agents.temperature }}</div>
              <div class="form-hint">较低的值使生成更确定性，较高的值使生成更随机创造性</div>
            </div>
            
            <div class="form-group">
              <label for="agents-max-tokens">最大输出令牌数</label>
              <input 
                type="number" 
                id="agents-max-tokens" 
                v-model="settings.agents.maxTokens" 
                min="256" 
                max="32768" 
                class="input-field"
              >
              <div class="form-hint">限制生成内容的最大长度</div>
            </div>
            
            <div class="form-group">
              <label for="agents-system-prompt">默认系统提示</label>
              <textarea 
                id="agents-system-prompt" 
                v-model="settings.agents.systemPrompt" 
                rows="4" 
                class="input-field textarea"
                placeholder="输入默认的系统指令提示词"
              ></textarea>
              <div class="form-hint">默认的Agent系统指令，指导其行为和能力</div>
            </div>
            
            <div class="form-group">
              <label for="agents-tracing-mode">追踪模式</label>
              <select id="agents-tracing-mode" v-model="settings.agents.tracingMode" class="input-field">
                <option value="disabled">禁用</option>
                <option value="local">本地</option>
                <option value="platform">平台</option>
              </select>
              <div class="form-hint">追踪模式决定如何记录和分析Agent运行情况</div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.agents.enableStreaming">
                <span>启用流式响应</span>
              </label>
              <div class="form-hint">逐字显示生成内容而不是等待完整响应</div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.agents.enableFunctionCalling">
                <span>启用函数调用</span>
              </label>
              <div class="form-hint">允许Agent使用工具和执行函数</div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.agents.allowUserHandoff">
                <span>允许用户接管</span>
              </label>
              <div class="form-hint">允许Agent在无法处理请求时将对话移交给人类用户</div>
            </div>
          </div>
        </div>
        
        <!-- API设置 -->
        <div v-else-if="activeSection === 'api'" class="settings-section">
          <h2 class="section-title">API设置</h2>
          
          <div class="settings-form">
            <div class="form-group">
              <label for="api-timeout">API请求超时（秒）</label>
              <input type="number" id="api-timeout" v-model="settings.apiTimeout" min="5" max="300" class="input-field">
            </div>
            
            <div class="form-group">
              <label for="max-retries">最大重试次数</label>
              <input type="number" id="max-retries" v-model="settings.maxRetries" min="0" max="10" class="input-field">
            </div>
            
            <div class="form-group">
              <label for="proxy-url">代理服务器 (可选)</label>
              <input type="text" id="proxy-url" v-model="settings.proxyUrl" placeholder="http://proxy.example.com:8080" class="input-field">
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.useCache">
                <span>启用API响应缓存</span>
              </label>
              <div class="form-hint">可减少重复请求，节省API调用次数</div>
            </div>
          </div>
        </div>
        
        <!-- 安全与隐私 -->
        <div v-else-if="activeSection === 'security'" class="settings-section">
          <h2 class="section-title">安全与隐私</h2>
          
          <div class="settings-form">
            <div class="form-group">
              <label for="session-timeout">会话超时（分钟）</label>
              <input type="number" id="session-timeout" v-model="settings.sessionTimeout" min="5" max="1440" class="input-field">
              <div class="form-hint">设置为0表示永不超时</div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.encryptData">
                <span>加密本地数据</span>
              </label>
              <div class="form-hint">增强敏感数据的安全性</div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.passwordProtect">
                <span>启用密码保护</span>
              </label>
            </div>
            
            <div v-if="settings.passwordProtect" class="form-group sub-options">
              <label for="password">设置密码</label>
              <div class="password-input">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  id="password" 
                  v-model="passwordInput"
                  class="input-field"
                >
                <button type="button" class="toggle-visibility" @click="showPassword = !showPassword">
                  <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <button class="btn" @click="updatePassword">更新密码</button>
            </div>
          </div>
          
          <div class="danger-zone">
            <h3>危险区域</h3>
            <div class="form-group">
              <button class="btn btn-danger" @click="showClearDataModal = true">
                <i class="fas fa-trash-alt"></i> 清除所有数据
              </button>
              <div class="form-hint">此操作将清除所有本地存储的数据，包括设置和缓存</div>
            </div>
          </div>
        </div>
        
        <!-- 高级设置 -->
        <div v-else-if="activeSection === 'advanced'" class="settings-section">
          <h2 class="section-title">高级设置</h2>
          
          <div class="settings-form">
            <div class="form-group">
              <label for="log-level">日志级别</label>
              <select id="log-level" v-model="settings.logLevel" class="input-field">
                <option value="error">错误</option>
                <option value="warning">警告</option>
                <option value="info">信息</option>
                <option value="debug">调试</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="data-dir">数据存储目录</label>
              <div class="path-input">
                <input type="text" id="data-dir" v-model="settings.dataDir" readonly class="input-field">
                <button class="btn" @click="selectDataDirectory">更改</button>
              </div>
            </div>
            
            <div class="form-group">
              <label for="max-cache">最大缓存大小 (MB)</label>
              <input type="number" id="max-cache" v-model="settings.maxCacheSize" min="50" max="5000" class="input-field">
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="settings.developerMode">
                <span>开发者模式</span>
              </label>
              <div class="form-hint">启用开发者工具和额外的调试功能</div>
            </div>
          </div>
        </div>
        
        <!-- 关于 -->
        <div v-else-if="activeSection === 'about'" class="settings-section">
          <h2 class="section-title">关于</h2>
          
          <div class="about-content">
            <div class="app-info">
              <div class="app-logo">
                <img src="@/assets/images/aivk-logo.svg" alt="AIVK Logo">
              </div>
              <div class="app-details">
                <h3>AIVK 平台</h3>
                <div class="version">版本 1.0.0</div>
                <div class="build-date">构建日期: 2023-12-15</div>
              </div>
            </div>
            
            <div class="app-description">
              AIVK是一个强大的AI工作流集成平台，支持多种大语言模型和插件扩展，为开发者和AI爱好者提供高效的开发环境。
            </div>
            
            <div class="tech-stack">
              <h4>技术栈</h4>
              <ul>
                <li>前端: Vue 3 + Vite</li>
                <li>后端: Python + FastAPI</li>
                <li>AI集成: OpenAI, Anthropic, Google Gemini...</li>
              </ul>
            </div>
            
            <div class="links">
              <a href="https://github.com/yourusername/aivk" target="_blank" class="link-item">
                <i class="fab fa-github"></i> GitHub
              </a>
              <a href="#" target="_blank" class="link-item">
                <i class="fas fa-book"></i> 文档
              </a>
              <a href="#" target="_blank" class="link-item">
                <i class="fas fa-bug"></i> 报告问题
              </a>
              <a href="#" target="_blank" class="link-item">
                <i class="fas fa-hand-holding-heart"></i> 支持项目
              </a>
            </div>
            
            <div class="license">
              <h4>许可证</h4>
              <p>MIT License &copy; 2023 AIVK Team</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 清除数据确认对话框 -->
    <div class="modal" v-if="showClearDataModal">
      <div class="modal-backdrop" @click="showClearDataModal = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>清除所有数据</h3>
          <button class="modal-close" @click="showClearDataModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p class="warning-text">
            <i class="fas fa-exclamation-triangle"></i> 警告: 这将永久删除所有本地存储的数据，此操作无法撤销。
          </p>
          <p>请输入"DELETE"确认此操作:</p>
          <input type="text" v-model="deleteConfirm" class="input-field">
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showClearDataModal = false">取消</button>
          <button 
            class="btn btn-danger" 
            @click="clearAllData"
            :disabled="deleteConfirm !== 'DELETE'"
          >
            清除所有数据
          </button>
        </div>
      </div>
    </div>
    
    <!-- 保存提示 -->
    <div class="save-bar" :class="{ 'visible': settingsChanged }">
      <span>您有未保存的更改</span>
      <div class="save-actions">
        <button class="btn" @click="resetSettings">取消</button>
        <button class="btn btn-primary" @click="saveSettings">保存设置</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useMainStore } from '@/stores/main'

const store = useMainStore()

// 设置部分
const settingSections = [
  { id: 'general', name: '常规设置', icon: 'fa-cog' },
  { id: 'litellm', name: 'LiteLLM代理', icon: 'fa-server' },
  { id: 'agents', name: 'Agents设置', icon: 'fa-robot' },
  { id: 'api', name: 'API设置', icon: 'fa-plug' },
  { id: 'security', name: '安全与隐私', icon: 'fa-shield-alt' },
  { id: 'advanced', name: '高级设置', icon: 'fa-tools' },
  { id: 'about', name: '关于', icon: 'fa-info-circle' }
]

// 状态
const activeSection = ref('general')
const showPassword = ref(false)
const showLiteLLMApiKey = ref(false)
const passwordInput = ref('')
const originalSettings = ref({})
const litellmConnectionStatus = ref(null)
const settings = reactive({
  // 常规设置
  language: 'zh-CN',
  theme: 'dark',
  autoUpdate: true,
  telemetry: false,
  
  // LiteLLM代理设置
  litellm: {
    host: 'http://localhost:8000',
    apiKey: '',
    timeout: 60,
    retries: 3,
    fallbackProviders: ['anthropic', 'azure'],
    defaultModel: 'gpt-4',
    debugMode: false,
    logRequests: true,
    cacheEnabled: true,
    cacheTTL: 3600
  },
  
  // OpenAI Agents设置
  agents: {
    defaultModel: 'gpt-4-turbo',
    temperature: 0.7,
    maxTokens: 4096,
    systemPrompt: 'You are a helpful AI assistant with access to various tools.',
    tracingMode: 'local',
    enableStreaming: true,
    enableFunctionCalling: true,
    allowUserHandoff: true
  },
  
  // API设置
  apiTimeout: 30,
  maxRetries: 3,
  proxyUrl: '',
  useCache: true,
  
  // 安全设置
  sessionTimeout: 30,
  encryptData: true,
  passwordProtect: false,
  
  // 高级设置
  logLevel: 'info',
  dataDir: 'C:\\Users\\username\\AppData\\Local\\AIVK',
  maxCacheSize: 500,
  developerMode: false
})

// 其他状态
const showClearDataModal = ref(false)
const deleteConfirm = ref('')

// 计算属性
const settingsChanged = computed(() => {
  return JSON.stringify(settings) !== JSON.stringify(originalSettings.value)
})

// 测试LiteLLM连接
async function testLiteLLMConnection() {
  litellmConnectionStatus.value = {
    type: 'loading',
    message: '正在测试连接...'
  }
  
  try {
    // 在实际应用中，这里会调用API测试连接
    // const response = await api.post('/test-litellm-connection', {
    //   host: settings.litellm.host,
    //   apiKey: settings.litellm.apiKey
    // })
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 随机成功或失败（仅用于演示）
    const success = Math.random() > 0.3
    
    if (success) {
      litellmConnectionStatus.value = {
        type: 'success',
        message: '连接成功！LiteLLM代理服务器运行正常。'
      }
    } else {
      throw new Error('无法连接到服务器')
    }
  } catch (error) {
    litellmConnectionStatus.value = {
      type: 'error',
      message: `连接失败: ${error.message || '未知错误'}`
    }
    
    console.error('LiteLLM连接测试失败:', error)
  }
  
  // 5秒后清除状态
  setTimeout(() => {
    litellmConnectionStatus.value = null
  }, 5000)
}

// 更新密码
function updatePassword() {
  if (passwordInput.value.length < 6) {
    store.addNotification({
      message: '密码长度必须大于6位',
      type: 'error'
    })
    return
  }
  
  console.log('密码已更新')
  store.addNotification({
    message: '密码已成功更新',
    type: 'success'
  })
  
  passwordInput.value = ''
  showPassword.value = false
}

// 选择数据目录
function selectDataDirectory() {
  // 在实际应用中，这里会调用本地系统的文件选择器
  console.log('选择数据目录')
  
  // 模拟选择
  setTimeout(() => {
    settings.dataDir = 'D:\\AIVK\\Data'
    store.addNotification({
      message: '数据目录已更新',
      type: 'success'
    })
  }, 500)
}

// 清除所有数据
function clearAllData() {
  if (deleteConfirm.value !== 'DELETE') return
  
  // 在实际应用中，这里会清除所有本地存储
  console.log('清除所有数据')
  
  store.addNotification({
    message: '所有数据已清除',
    type: 'success'
  })
  
  deleteConfirm.value = ''
  showClearDataModal.value = false
  
  // 重置设置为默认值
  resetSettings()
}

// 保存设置
function saveSettings() {
  // 在实际应用中，这里会保存设置到本地存储或后端
  console.log('保存设置', settings)
  
  // 更新原始设置，以便比较变更
  originalSettings.value = JSON.parse(JSON.stringify(settings))
  
  store.addNotification({
    message: '设置已保存',
    type: 'success'
  })
}

// 重置设置
function resetSettings() {
  // 恢复到上次保存的设置
  Object.assign(settings, JSON.parse(JSON.stringify(originalSettings.value)))
  
  store.addNotification({
    message: '设置已重置',
    type: 'info'
  })
}

// 监听部分变更，提供更友好的用户体验
watch(() => settings.passwordProtect, (newValue) => {
  if (!newValue) {
    passwordInput.value = ''
  }
})

// 页面加载时
onMounted(() => {
  // 在实际应用中，这里会从存储中加载设置
  // 模拟加载
  setTimeout(() => {
    // 保存一份原始设置的副本，用于比较变更
    originalSettings.value = JSON.parse(JSON.stringify(settings))
  }, 300)
})
</script>

<style scoped>
.settings-view {
  padding-bottom: 80px; /* 为保存栏留出空间 */
}

.settings-container {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 20px;
  margin-top: 20px;
}

.settings-sidebar {
  height: fit-content;
}

.settings-nav {
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 5px;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.nav-item:hover {
  background-color: var(--bg-tertiary);
}

.nav-item.active {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
}

.nav-item i {
  width: 20px;
  margin-right: 10px;
  text-align: center;
}

.settings-section {
  padding: 10px 0;
}

.section-title {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 5px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-label input {
  margin-right: 10px;
}

.sub-options {
  margin-left: 20px;
  padding-left: 15px;
  border-left: 2px solid var(--border-color);
}

.path-input {
  display: flex;
  gap: 10px;
}

.path-input .input-field {
  flex: 1;
}

.password-input {
  position: relative;
  margin-bottom: 10px;
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

.danger-zone {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.save-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: var(--bg-secondary);
  padding: 10px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transform: translateY(100%);
  transition: transform var(--transition-speed) ease;
  z-index: 90;
}

.save-bar.visible {
  transform: translateY(0);
}

.save-actions {
  display: flex;
  gap: 10px;
}

/* 关于页面样式 */
.about-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.app-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
}

.app-logo img {
  height: 80px;
  width: auto;
}

.build-date {
  color: var(--text-secondary);
  font-size: 14px;
}

.tech-stack ul {
  margin-top: 10px;
  padding-left: 20px;
}

.tech-stack li {
  margin-bottom: 5px;
}

.links {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 10px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  text-decoration: none;
  padding: 8px 15px;
  border-radius: var(--border-radius);
  background-color: var(--bg-tertiary);
  transition: all var(--transition-speed) ease;
}

.link-item:hover {
  background-color: rgba(0, 168, 255, 0.1);
}

.license {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
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
  -webkit-backdrop-filter: blur(5px);
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

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.warning-text {
  color: var(--danger-color);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: rgba(255, 94, 87, 0.1);
  border-radius: var(--border-radius);
  margin-bottom: 20px;
}

@keyframes modalSlideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* 滑块样式 */
.slider-input {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: var(--bg-tertiary);
  outline: none;
  transition: all var(--transition-speed) ease;
  -webkit-appearance: none;
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  border: none;
}

.slider-input::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  border: none;
}

.range-value {
  text-align: center;
  margin-top: 10px;
  font-weight: 500;
  color: var(--primary-color);
}

.multiple-select {
  height: auto;
  min-height: 100px;
}

.test-connection-container {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.connection-status {
  padding: 10px 15px;
  border-radius: var(--border-radius);
  font-size: 14px;
}

.connection-status.loading {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
}

.connection-status.success {
  background-color: rgba(5, 196, 107, 0.1);
  color: var(--success-color);
}

.connection-status.error {
  background-color: rgba(255, 94, 87, 0.1);
  color: var(--danger-color);
}

.textarea {
  min-height: 100px;
  font-family: inherit;
  resize: vertical;
}

/* 响应式布局 */
@media (max-width: 992px) {
  .settings-container {
    grid-template-columns: 1fr;
  }
  
  .settings-sidebar {
    height: auto;
  }
  
  .settings-nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .nav-item {
    margin-bottom: 0;
  }
}

@media (max-width: 576px) {
  .test-connection-container {
    align-items: stretch;
  }
}
</style>

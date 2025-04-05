<template>
  <div class="plugin-manager">
    <h1 class="page-title">插件管理</h1>
    
    <div class="plugin-controls card">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索插件..." 
          class="search-input"
        >
        <button v-if="searchQuery" class="clear-search" @click="searchQuery = ''">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="filter-controls">
        <div class="filter-group">
          <label for="category-filter">分类:</label>
          <select id="category-filter" v-model="categoryFilter" class="filter-select">
            <option value="all">全部分类</option>
            <option 
              v-for="category in pluginCategories" 
              :key="category.id" 
              :value="category.id"
            >
              {{ category.name }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label for="status-filter">状态:</label>
          <select id="status-filter" v-model="statusFilter" class="filter-select">
            <option value="all">全部状态</option>
            <option value="active">已启用</option>
            <option value="inactive">已停用</option>
          </select>
        </div>
      </div>
      
      <div class="view-actions">
        <button 
          class="view-btn" 
          :class="{ active: viewMode === 'grid' }" 
          @click="viewMode = 'grid'"
          title="网格视图"
        >
          <i class="fas fa-th-large"></i>
        </button>
        <button 
          class="view-btn" 
          :class="{ active: viewMode === 'list' }" 
          @click="viewMode = 'list'"
          title="列表视图"
        >
          <i class="fas fa-list"></i>
        </button>
      </div>
    </div>
    
    <div v-if="filteredPlugins.length === 0" class="no-plugins card">
      <div class="no-plugins-icon">
        <i class="fas fa-puzzle-piece"></i>
      </div>
      <h2>未找到插件</h2>
      <p>没有符合当前搜索条件的插件</p>
      <button class="btn" @click="resetFilters">清除过滤器</button>
    </div>
    
    <template v-else>
      <!-- 分类视图 -->
      <div v-if="groupByCategory" class="plugin-categories">
        <div v-for="category in pluginCategories" :key="category.id" class="plugin-category-section">
          <div class="category-header" v-if="getPluginsByCategory(category.id).length > 0">
            <div class="category-title">
              <i :class="`fas ${category.icon}`"></i>
              {{ category.name }}
              <span class="plugin-count">({{ getPluginsByCategory(category.id).length }})</span>
            </div>
          </div>
          
          <div v-if="getPluginsByCategory(category.id).length > 0" :class="viewMode === 'grid' ? 'plugins-grid' : 'plugins-list'">
            <template v-if="viewMode === 'grid'">
              <div 
                v-for="plugin in getPluginsByCategory(category.id)" 
                :key="plugin.id" 
                class="plugin-card card"
                :class="{ 'inactive': !plugin.active }"
              >
                <div class="plugin-card-header">
                  <div class="plugin-icon" :style="{ backgroundColor: plugin.color || 'rgba(0, 168, 255, 0.2)' }">
                    <i :class="`fas ${plugin.icon || 'fa-puzzle-piece'}`"></i>
                  </div>
                  <div 
                    class="toggle-track" 
                    :class="{ active: plugin.active }"
                    @click="togglePlugin(plugin.id)"
                  >
                    <div class="toggle-thumb"></div>
                  </div>
                </div>
                
                <div class="plugin-card-body">
                  <h3 class="plugin-name">{{ plugin.name }}</h3>
                  <div class="plugin-meta">
                    <span class="plugin-version">v{{ plugin.version }}</span>
                    <span class="plugin-dot">•</span>
                    <span class="plugin-author">{{ plugin.author }}</span>
                  </div>
                  <p class="plugin-description">{{ plugin.description }}</p>
                </div>
                
                <div class="plugin-card-footer">
                  <span class="plugin-category-tag">
                    <i :class="`fas ${getCategoryIcon(plugin.category)}`"></i>
                    {{ getCategoryName(plugin.category) }}
                  </span>
                  <div class="plugin-actions">
                    <router-link :to="`/plugins/${plugin.id}`" class="plugin-action-btn">
                      <i class="fas fa-cog"></i>
                    </router-link>
                  </div>
                </div>
              </div>
            </template>
            
            <template v-else>
              <div 
                v-for="plugin in getPluginsByCategory(category.id)" 
                :key="plugin.id" 
                class="plugin-list-item card"
                :class="{ 'inactive': !plugin.active }"
              >
                <div class="plugin-icon" :style="{ backgroundColor: plugin.color || 'rgba(0, 168, 255, 0.2)' }">
                  <i :class="`fas ${plugin.icon || 'fa-puzzle-piece'}`"></i>
                </div>
                <div class="plugin-info">
                  <h3 class="plugin-name">{{ plugin.name }}</h3>
                  <div class="plugin-meta">
                    <span class="plugin-version">v{{ plugin.version }}</span>
                    <span class="plugin-dot">•</span>
                    <span class="plugin-author">{{ plugin.author }}</span>
                    <span class="plugin-dot">•</span>
                    <span class="plugin-category-tag small">
                      <i :class="`fas ${getCategoryIcon(plugin.category)}`"></i>
                      {{ getCategoryName(plugin.category) }}
                    </span>
                  </div>
                  <p class="plugin-description">{{ plugin.description }}</p>
                </div>
                <div class="plugin-status">
                  <span class="status-indicator" :class="plugin.active ? 'active' : 'inactive'">
                    {{ plugin.status }}
                  </span>
                </div>
                <div class="plugin-actions">
                  <div 
                    class="toggle-track" 
                    :class="{ active: plugin.active }"
                    @click="togglePlugin(plugin.id)"
                  >
                    <div class="toggle-thumb"></div>
                  </div>
                  <router-link :to="`/plugins/${plugin.id}`" class="plugin-action-btn">
                    <i class="fas fa-cog"></i>
                  </router-link>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
      
      <!-- 非分类视图 -->
      <div v-else :class="viewMode === 'grid' ? 'plugins-grid' : 'plugins-list'">
        <template v-if="viewMode === 'grid'">
          <div 
            v-for="plugin in filteredPlugins" 
            :key="plugin.id" 
            class="plugin-card card"
            :class="{ 'inactive': !plugin.active }"
          >
            <div class="plugin-card-header">
              <div class="plugin-icon" :style="{ backgroundColor: plugin.color || 'rgba(0, 168, 255, 0.2)' }">
                <i :class="`fas ${plugin.icon || 'fa-puzzle-piece'}`"></i>
              </div>
              <div 
                class="toggle-track" 
                :class="{ active: plugin.active }"
                @click="togglePlugin(plugin.id)"
              >
                <div class="toggle-thumb"></div>
              </div>
            </div>
            
            <div class="plugin-card-body">
              <h3 class="plugin-name">{{ plugin.name }}</h3>
              <div class="plugin-meta">
                <span class="plugin-version">v{{ plugin.version }}</span>
                <span class="plugin-dot">•</span>
                <span class="plugin-author">{{ plugin.author }}</span>
              </div>
              <p class="plugin-description">{{ plugin.description }}</p>
            </div>
            
            <div class="plugin-card-footer">
              <span class="plugin-category-tag">
                <i :class="`fas ${getCategoryIcon(plugin.category)}`"></i>
                {{ getCategoryName(plugin.category) }}
              </span>
              <div class="plugin-actions">
                <router-link :to="`/plugins/${plugin.id}`" class="plugin-action-btn">
                  <i class="fas fa-cog"></i>
                </router-link>
              </div>
            </div>
          </div>
        </template>
        
        <template v-else>
          <div 
            v-for="plugin in filteredPlugins" 
            :key="plugin.id" 
            class="plugin-list-item card"
            :class="{ 'inactive': !plugin.active }"
          >
            <div class="plugin-icon" :style="{ backgroundColor: plugin.color || 'rgba(0, 168, 255, 0.2)' }">
              <i :class="`fas ${plugin.icon || 'fa-puzzle-piece'}`"></i>
            </div>
            <div class="plugin-info">
              <h3 class="plugin-name">{{ plugin.name }}</h3>
              <div class="plugin-meta">
                <span class="plugin-version">v{{ plugin.version }}</span>
                <span class="plugin-dot">•</span>
                <span class="plugin-author">{{ plugin.author }}</span>
                <span class="plugin-dot">•</span>
                <span class="plugin-category-tag small">
                  <i :class="`fas ${getCategoryIcon(plugin.category)}`"></i>
                  {{ getCategoryName(plugin.category) }}
                </span>
              </div>
              <p class="plugin-description">{{ plugin.description }}</p>
            </div>
            <div class="plugin-status">
              <span class="status-indicator" :class="plugin.active ? 'active' : 'inactive'">
                {{ plugin.status }}
              </span>
            </div>
            <div class="plugin-actions">
              <div 
                class="toggle-track" 
                :class="{ active: plugin.active }"
                @click="togglePlugin(plugin.id)"
              >
                <div class="toggle-thumb"></div>
              </div>
              <router-link :to="`/plugins/${plugin.id}`" class="plugin-action-btn">
                <i class="fas fa-cog"></i>
              </router-link>
            </div>
          </div>
        </template>
      </div>
    </template>
    
    <div class="action-fab">
      <button class="fab-btn" title="安装新插件" @click="openInstallDialog">
        <i class="fas fa-plus"></i>
      </button>
    </div>
    
    <!-- 安装插件对话框 -->
    <div class="modal" v-if="showInstallModal">
      <div class="modal-backdrop" @click="showInstallModal = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>安装新插件</h3>
          <button class="modal-close" @click="showInstallModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="install-tabs">
            <button 
              class="install-tab" 
              :class="{ active: installTab === 'market' }"
              @click="installTab = 'market'"
            >
              <i class="fas fa-store"></i>
              插件市场
            </button>
            <button 
              class="install-tab" 
              :class="{ active: installTab === 'url' }"
              @click="installTab = 'url'"
            >
              <i class="fas fa-link"></i>
              从URL安装
            </button>
            <button 
              class="install-tab" 
              :class="{ active: installTab === 'upload' }"
              @click="installTab = 'upload'"
            >
              <i class="fas fa-upload"></i>
              上传安装
            </button>
          </div>
          
          <!-- 市场安装 -->
          <div v-if="installTab === 'market'" class="market-container">
            <div class="market-search">
              <div class="search-box">
                <i class="fas fa-search"></i>
                <input 
                  type="text" 
                  v-model="marketSearchQuery" 
                  placeholder="搜索插件市场..." 
                  class="search-input"
                >
              </div>
            </div>
            
            <div class="market-list">
              <div 
                v-for="plugin in filteredMarketPlugins" 
                :key="plugin.id" 
                class="market-plugin-item"
              >
                <div class="market-plugin-icon" :style="{ backgroundColor: plugin.color }">
                  <i :class="`fas ${plugin.icon}`"></i>
                </div>
                <div class="market-plugin-info">
                  <div class="market-plugin-header">
                    <h4 class="market-plugin-name">{{ plugin.name }}</h4>
                    <div class="market-plugin-meta">
                      <span class="market-plugin-version">v{{ plugin.version }}</span>
                      <span class="market-plugin-dot">•</span>
                      <span class="market-plugin-author">{{ plugin.author }}</span>
                    </div>
                  </div>
                  <p class="market-plugin-desc">{{ plugin.description }}</p>
                  <div class="market-plugin-stats">
                    <span class="market-plugin-downloads">
                      <i class="fas fa-download"></i> {{ plugin.downloads }}
                    </span>
                    <span class="market-plugin-rating">
                      <i class="fas fa-star"></i> {{ plugin.rating }}
                    </span>
                    <span class="market-plugin-tag">
                      <i :class="`fas ${getCategoryIcon(plugin.category)}`"></i>
                      {{ getCategoryName(plugin.category) }}
                    </span>
                  </div>
                </div>
                <div class="market-plugin-action">
                  <button 
                    v-if="plugin.installed" 
                    class="btn btn-sm btn-outline" 
                    disabled
                  >
                    <i class="fas fa-check"></i> 已安装
                  </button>
                  <button 
                    v-else 
                    class="btn btn-sm btn-primary" 
                    @click="installMarketPlugin(plugin)"
                  >
                    <i class="fas fa-download"></i> 安装
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- URL安装 -->
          <div v-else-if="installTab === 'url'" class="url-install">
            <div class="form-group">
              <label for="plugin-url">插件URL</label>
              <div class="input-with-icon">
                <i class="fas fa-link"></i>
                <input 
                  type="text" 
                  id="plugin-url" 
                  v-model="pluginUrl" 
                  placeholder="https://example.com/plugin.zip" 
                  class="input-field"
                >
              </div>
              <div class="form-hint">输入插件ZIP包或Git仓库的URL</div>
            </div>
            
            <div class="form-actions">
              <button class="btn" @click="showInstallModal = false">取消</button>
              <button 
                class="btn btn-primary" 
                :disabled="!pluginUrl"
                @click="installFromUrl"
              >
                <i class="fas fa-download"></i> 安装
              </button>
            </div>
          </div>
          
          <!-- 上传安装 -->
          <div v-else-if="installTab === 'upload'" class="upload-install">
            <input 
              type="file" 
              ref="fileInput" 
              accept=".zip,.tar.gz,.tgz" 
              style="display: none" 
              @change="onFileSelected"
            >
            
            <div 
              v-if="!selectedFile"
              class="upload-area"
              @click="triggerFileInput"
              @dragover.prevent
              @drop.prevent="onFileDrop"
            >
              <div class="upload-icon">
                <i class="fas fa-cloud-upload-alt"></i>
              </div>
              <div class="upload-text">点击或拖放插件包到此处</div>
              <div class="upload-hint">支持 .zip, .tar.gz 格式</div>
            </div>
            
            <div v-else class="selected-file">
              <div class="file-info">
                <i class="fas fa-file-archive"></i>
                <div class="file-details">
                  <div class="file-name">{{ selectedFile.name }}</div>
                  <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
                </div>
              </div>
              
              <div class="file-actions">
                <button class="btn btn-sm" @click="selectedFile = null">
                  <i class="fas fa-undo"></i> 更换
                </button>
                <button class="btn btn-sm btn-primary" @click="uploadPlugin">
                  <i class="fas fa-upload"></i> 安装
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMainStore } from '@/stores/main'

const store = useMainStore()

// 状态
const plugins = computed(() => store.plugins)
const pluginCategories = computed(() => store.pluginCategories)
const searchQuery = ref('')
const categoryFilter = ref('all')
const statusFilter = ref('all')
const viewMode = ref('grid')
const groupByCategory = ref(true)
const showInstallModal = ref(false)
const installTab = ref('market')
const marketSearchQuery = ref('')
const pluginUrl = ref('')
const selectedFile = ref(null)
const fileInput = ref(null)

// 市场插件示例数据
const marketPlugins = ref([
  {
    id: 'langchain-integration',
    name: 'LangChain 集成',
    description: '集成LangChain框架，提供先进的提示链和代理功能',
    author: 'AIVK团队',
    version: '1.2.0',
    icon: 'fa-link',
    color: 'rgba(100, 42, 255, 0.2)',
    downloads: '1,245',
    rating: '4.7',
    installed: false,
    category: 'integrations'
  },
  {
    id: 'file-converter',
    name: '文件转换器',
    description: '支持多种文件格式之间的转换，包括PDF、Word、Markdown等',
    author: 'FileTools Inc.',
    version: '2.1.0',
    icon: 'fa-file-alt',
    color: 'rgba(255, 168, 1, 0.2)',
    downloads: '3,589',
    rating: '4.5',
    installed: true,
    category: 'tools'
  },
  {
    id: 'claude-connector',
    name: 'Claude 连接器',
    description: '连接Anthropic的Claude模型，提供高质量的生成式AI功能',
    author: 'AI Connectors',
    version: '1.0.5',
    icon: 'fa-comment-dots',
    color: 'rgba(0, 168, 255, 0.2)',
    downloads: '2,754',
    rating: '4.8',
    installed: false,
    category: 'llm'
  },
  {
    id: 'data-visualizer',
    name: '数据可视化工具',
    description: '将数据转换为交互式图表和可视化，支持多种图表类型',
    author: 'DataViz Team',
    version: '3.2.1',
    icon: 'fa-chart-bar',
    color: 'rgba(5, 196, 107, 0.2)',
    downloads: '5,127',
    rating: '4.6',
    installed: false,
    category: 'tools'
  },
  {
    id: 'mcp-advanced',
    name: 'MCP 高级功能',
    description: '为MCP服务添加高级功能，包括服务编排和监控工具',
    author: 'Cloud Systems',
    version: '2.0.0',
    icon: 'fa-server',
    color: 'rgba(127, 17, 224, 0.2)',
    downloads: '932',
    rating: '4.3',
    installed: false,
    category: 'mcp'
  }
])

// 过滤插件
const filteredPlugins = computed(() => {
  let result = plugins.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(plugin => 
      plugin.name.toLowerCase().includes(query) || 
      plugin.description.toLowerCase().includes(query) ||
      plugin.author.toLowerCase().includes(query)
    )
  }
  
  // 分类过滤
  if (categoryFilter.value !== 'all') {
    result = result.filter(plugin => plugin.category === categoryFilter.value)
  }
  
  // 状态过滤
  if (statusFilter.value !== 'all') {
    const isActive = statusFilter.value === 'active'
    result = result.filter(plugin => plugin.active === isActive)
  }
  
  return result
})

// 过滤市场插件
const filteredMarketPlugins = computed(() => {
  if (!marketSearchQuery.value) return marketPlugins.value
  
  const query = marketSearchQuery.value.toLowerCase()
  return marketPlugins.value.filter(plugin => 
    plugin.name.toLowerCase().includes(query) || 
    plugin.description.toLowerCase().includes(query) ||
    plugin.author.toLowerCase().includes(query)
  )
})

// 按分类获取插件
function getPluginsByCategory(categoryId) {
  return filteredPlugins.value.filter(plugin => plugin.category === categoryId)
}

// 获取分类名称
function getCategoryName(categoryId) {
  return store.getCategoryName(categoryId)
}

// 获取分类图标
function getCategoryIcon(categoryId) {
  return store.getCategoryIcon(categoryId)
}

// 切换插件状态
function togglePlugin(pluginId) {
  store.togglePlugin(pluginId)
}

// 重置过滤器
function resetFilters() {
  searchQuery.value = ''
  categoryFilter.value = 'all'
  statusFilter.value = 'all'
}

// 打开安装对话框
function openInstallDialog() {
  showInstallModal.value = true
}

// 从市场安装插件
function installMarketPlugin(plugin) {
  // 在实际应用中，这里会调用API安装插件
  plugin.installed = true
  
  // 添加通知
  store.addNotification({
    type: 'success',
    message: `${plugin.name} 已成功安装`
  })
  
  // 添加到已安装插件列表
  const newPlugin = {
    id: Date.now(),
    name: plugin.name,
    description: plugin.description,
    version: plugin.version,
    author: plugin.author,
    icon: plugin.icon,
    color: plugin.color,
    active: true,
    status: '正常运行中',
    category: plugin.category
  }
  
  store.plugins.push(newPlugin)
}

// 从URL安装
function installFromUrl() {
  if (!pluginUrl.value) return
  
  // 在实际应用中，这里会调用API安装插件
  store.addNotification({
    type: 'info',
    message: '正在从URL安装插件，请稍候...'
  })
  
  // 模拟安装过程
  setTimeout(() => {
    store.addNotification({
      type: 'success',
      message: '插件已成功安装'
    })
    
    showInstallModal.value = false
    pluginUrl.value = ''
  }, 1500)
}

// 触发文件选择
function triggerFileInput() {
  fileInput.value.click()
}

// 文件选择处理
function onFileSelected(event) {
  selectedFile.value = event.target.files[0]
}

// 文件拖放处理
function onFileDrop(event) {
  const file = event.dataTransfer.files[0]
  if (file && (file.name.endsWith('.zip') || file.name.endsWith('.tar.gz') || file.name.endsWith('.tgz'))) {
    selectedFile.value = file
  } else {
    store.addNotification({
      type: 'error',
      message: '只支持.zip、.tar.gz或.tgz格式的插件包'
    })
  }
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 上传插件包
function uploadPlugin() {
  if (!selectedFile.value) return
  
  // 在实际应用中，这里会调用API上传插件包
  store.addNotification({
    type: 'info',
    message: '正在上传并安装插件，请稍候...'
  })
  
  // 模拟上传和安装过程
  setTimeout(() => {
    store.addNotification({
      type: 'success',
      message: '插件已成功安装'
    })
    
    showInstallModal.value = false
    selectedFile.value = null
  }, 1500)
}

onMounted(() => {
  store.fetchPlugins()
})
</script>

<style scoped>
.plugin-manager {
  padding-bottom: 80px;
}

.plugin-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  margin-bottom: 20px;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
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
  height: 40px;
  padding: 0 15px 0 40px;
  border-radius: 20px;
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

.filter-controls {
  display: flex;
  gap: 15px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  color: var(--text-secondary);
  font-size: 14px;
}

.filter-select {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  color: var(--text-color);
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.view-actions {
  display: flex;
  gap: 5px;
}

.view-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.view-btn.active {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.no-plugins {
  text-align: center;
  padding: 60px 30px;
}

.no-plugins-icon {
  font-size: 48px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.no-plugins h2 {
  margin-bottom: 10px;
  font-size: 24px;
}

.no-plugins p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.plugin-categories {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 0 5px;
}

.category-title {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-color);
}

.category-title i {
  color: var(--primary-color);
  width: 22px;
  text-align: center;
}

.plugin-count {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 400;
}

.plugins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.plugin-card {
  display: flex;
  flex-direction: column;
  transition: all var(--transition-speed) ease;
  position: relative;
  overflow: hidden;
  height: 100%;
  padding: 0;
  border-left: 3px solid transparent;
}

.plugin-card.inactive {
  border-left-color: var(--text-secondary);
  opacity: 0.8;
}

.plugin-card.inactive::before {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent var(--text-secondary) transparent transparent;
  z-index: 1;
}

.plugin-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
}

.plugin-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
}

.plugin-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.plugin-card-body {
  padding: 15px;
  flex: 1;
}

.plugin-name {
  font-size: 18px;
  margin-bottom: 5px;
  color: var(--text-color);
}

.plugin-meta {
  display: flex;
  align-items: center;
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 10px;
}

.plugin-dot {
  margin: 0 5px;
}

.plugin-description {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 5px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.plugin-card-footer {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
}

.plugin-category-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  background-color: var(--bg-tertiary);
  border-radius: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.plugin-category-tag.small {
  padding: 2px 6px;
  font-size: 11px;
}

.plugin-category-tag i {
  font-size: 11px;
}

.plugin-actions {
  display: flex;
  gap: 8px;
}

.plugin-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 16px;
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  transition: all var(--transition-speed) ease;
}

.plugin-action-btn:hover {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.toggle-track {
  width: 40px;
  height: 20px;
  background-color: var(--bg-tertiary);
  border-radius: 10px;
  position: relative;
  cursor: pointer;
  transition: all var(--transition-speed) ease;
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

.plugins-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.plugin-list-item {
  display: flex;
  align-items: center;
  padding: 15px;
  gap: 15px;
  transition: all var(--transition-speed) ease;
  position: relative;
  border-left: 3px solid transparent;
}

.plugin-list-item.inactive {
  border-left-color: var(--text-secondary);
  opacity: 0.8;
}

.plugin-list-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
}

.plugin-info {
  flex: 1;
  min-width: 0;
}

.plugin-status {
  padding-right: 15px;
}

.status-indicator {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
}

.status-indicator.active {
  background-color: rgba(5, 196, 107, 0.1);
  color: var(--success-color);
}

.status-indicator.inactive {
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
}

.action-fab {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 10;
}

.fab-btn {
  width: 56px;
  height: 56px;
  border-radius: 28px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 10px rgba(0, 168, 255, 0.4);
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.fab-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 168, 255, 0.5);
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
  z-index: 100;
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
  max-width: 700px;
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
  font-size: 20px;
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
  padding: 0;
}

.install-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
}

.install-tab {
  padding: 15px 20px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all var(--transition-speed) ease;
}

.install-tab:hover {
  background-color: var(--bg-tertiary);
}

.install-tab.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.market-container {
  padding: 20px;
}

.market-search {
  margin-bottom: 20px;
}

.market-list {
  max-height: 500px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.market-plugin-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  transition: all var(--transition-speed) ease;
}

.market-plugin-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
}

.market-plugin-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.market-plugin-info {
  flex: 1;
  min-width: 0;
}

.market-plugin-header {
  margin-bottom: 5px;
}

.market-plugin-name {
  font-size: 16px;
  margin-bottom: 3px;
}

.market-plugin-meta {
  display: flex;
  align-items: center;
  color: var(--text-secondary);
  font-size: 12px;
}

.market-plugin-dot {
  margin: 0 5px;
}

.market-plugin-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.5;
}

.market-plugin-stats {
  display: flex;
  gap: 15px;
  color: var(--text-secondary);
  font-size: 12px;
}

.market-plugin-downloads i,
.market-plugin-rating i {
  margin-right: 5px;
}

.market-plugin-rating {
  color: var(--warning-color);
}

.market-plugin-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 6px;
  background-color: var(--bg-color);
  border-radius: 10px;
  font-size: 11px;
}

.market-plugin-action {
  padding-left: 15px;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.url-install,
.upload-install {
  padding: 20px;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius);
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-speed) ease;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background-color: rgba(0, 168, 255, 0.05);
}

.upload-icon {
  font-size: 48px;
  color: var(--primary-color);
  margin-bottom: 20px;
}

.upload-text {
  font-size: 16px;
  margin-bottom: 10px;
}

.upload-hint {
  font-size: 12px;
  color: var(--text-secondary);
}

.selected-file {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-info i {
  font-size: 24px;
  color: var(--primary-color);
}

.file-details {
  display: flex;
  flex-direction: column;
}

.file-name {
  font-weight: 500;
  margin-bottom: 3px;
}

.file-size {
  font-size: 12px;
  color: var(--text-secondary);
}

.file-actions {
  display: flex;
  gap: 10px;
}

@keyframes modalSlideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .plugin-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-controls {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select {
    flex: 1;
  }
  
  .view-actions {
    align-self: flex-end;
  }
  
  .plugins-grid {
    grid-template-columns: 1fr;
  }
  
  .plugin-list-item {
    flex-wrap: wrap;
  }
  
  .plugin-info {
    width: 100%;
    order: 2;
  }
  
  .plugin-status {
    order: 3;
    padding: 10px 0 0 0;
  }
  
  .plugin-actions {
    margin-left: auto;
    order: 1;
  }
  
  .action-fab {
    bottom: 20px;
    right: 20px;
  }
  
  .fab-btn {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
}
</style>

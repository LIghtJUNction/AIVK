<template>
  <div class="logs-view">
    <h1 class="page-title">系统日志</h1>
    
    <div class="logs-header">
      <div class="filter-group">
        <div class="filter-item">
          <label>日志级别</label>
          <select v-model="logLevelFilter" class="input-field">
            <option value="all">全部级别</option>
            <option value="info">信息</option>
            <option value="warning">警告</option>
            <option value="error">错误</option>
            <option value="debug">调试</option>
          </select>
        </div>
        
        <div class="filter-item">
          <label>日期范围</label>
          <div class="date-range">
            <input type="date" v-model="startDate" class="input-field date-input">
            <span class="range-separator">-</span>
            <input type="date" v-model="endDate" class="input-field date-input">
          </div>
        </div>
        
        <div class="filter-item">
          <label>源</label>
          <select v-model="sourceFilter" class="input-field">
            <option value="all">全部来源</option>
            <option value="system">系统</option>
            <option value="plugin">插件</option>
            <option value="llm">LLM服务</option>
            <option value="user">用户</option>
          </select>
        </div>
      </div>
      
      <div class="search-group">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索日志内容..." 
            class="search-input"
          >
          <button v-if="searchQuery" class="clear-search" @click="searchQuery = ''">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="logs-actions">
          <button class="btn" @click="refreshLogs">
            <i class="fas fa-sync-alt"></i> 刷新
          </button>
          <button class="btn" @click="exportLogs">
            <i class="fas fa-file-export"></i> 导出
          </button>
          <button class="btn btn-danger" @click="showClearModal = true">
            <i class="fas fa-trash-alt"></i> 清空
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="loading-container">
      <div class="tech-loader"></div>
      <div class="loading-text">加载日志<span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></div>
    </div>
    
    <div v-else-if="filteredLogs.length === 0" class="no-logs card">
      <div class="no-logs-icon">
        <i class="fas fa-clipboard-list"></i>
      </div>
      <div class="no-logs-text">未找到日志记录</div>
      <p class="no-logs-description">
        没有与当前筛选条件匹配的日志记录。尝试更改筛选条件或清除搜索。
      </p>
    </div>
    
    <div v-else class="logs-container card">
      <div class="log-entries">
        <div class="log-headers">
          <div class="log-header time">时间</div>
          <div class="log-header level">级别</div>
          <div class="log-header source">来源</div>
          <div class="log-header message">消息</div>
          <div class="log-header actions">操作</div>
        </div>
        
        <div 
          v-for="(log, index) in filteredLogs" 
          :key="index" 
          class="log-entry" 
          :class="log.level"
          @click="toggleExpandLog(log)"
        >
          <div class="log-time">{{ formatDate(log.timestamp) }}</div>
          <div class="log-level">{{ formatLevel(log.level) }}</div>
          <div class="log-source">{{ log.source }}</div>
          <div class="log-message" :class="{ 'expanded': expandedLogs.includes(log.id) }">
            {{ log.message }}
          </div>
          <div class="log-actions">
            <button class="action-btn" @click.stop="copyLog(log)">
              <i class="fas fa-copy"></i>
            </button>
            <button class="action-btn" @click.stop="showLogDetails(log)">
              <i class="fas fa-search-plus"></i>
            </button>
          </div>
        </div>
      </div>
      
      <div class="logs-pagination">
        <button 
          class="pagination-btn" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <div class="pagination-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </div>
        
        <button 
          class="pagination-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
        
        <select v-model="pageSize" class="page-size">
          <option :value="10">10条/页</option>
          <option :value="20">20条/页</option>
          <option :value="50">50条/页</option>
          <option :value="100">100条/页</option>
        </select>
      </div>
    </div>
    
    <!-- 日志详情模态框 -->
    <div class="modal" v-if="showLogDetailModal">
      <div class="modal-backdrop" @click="showLogDetailModal = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>日志详情</h3>
          <button class="modal-close" @click="showLogDetailModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="log-detail-item">
            <div class="detail-label">时间</div>
            <div class="detail-value">{{ selectedLog?.timestamp }}</div>
          </div>
          
          <div class="log-detail-item">
            <div class="detail-label">级别</div>
            <div class="detail-value" :class="`level-${selectedLog?.level}`">
              {{ formatLevel(selectedLog?.level) }}
            </div>
          </div>
          
          <div class="log-detail-item">
            <div class="detail-label">来源</div>
            <div class="detail-value">{{ selectedLog?.source }}</div>
          </div>
          
          <div class="log-detail-item">
            <div class="detail-label">消息</div>
            <div class="detail-value log-message-detail">{{ selectedLog?.message }}</div>
          </div>
          
          <div class="log-detail-item" v-if="selectedLog?.metadata">
            <div class="detail-label">元数据</div>
            <pre class="detail-value log-metadata">{{ JSON.stringify(selectedLog?.metadata, null, 2) }}</pre>
          </div>
          
          <div class="log-detail-item" v-if="selectedLog?.stackTrace">
            <div class="detail-label">堆栈跟踪</div>
            <pre class="detail-value log-stack-trace">{{ selectedLog?.stackTrace }}</pre>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="copyLogDetail">
            <i class="fas fa-copy"></i> 复制
          </button>
          <button class="btn btn-primary" @click="showLogDetailModal = false">
            关闭
          </button>
        </div>
      </div>
    </div>
    
    <!-- 清空日志确认模态框 -->
    <div class="modal" v-if="showClearModal">
      <div class="modal-backdrop" @click="showClearModal = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>确认清空日志</h3>
          <button class="modal-close" @click="showClearModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>您确定要清空所有日志记录吗？此操作不可恢复。</p>
          
          <div class="clear-options">
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="clearOptions.all">
                <span>清空所有日志</span>
              </label>
            </div>
            
            <div class="form-group" v-if="!clearOptions.all">
              <label class="checkbox-label">
                <input type="checkbox" v-model="clearOptions.system">
                <span>系统日志</span>
              </label>
            </div>
            
            <div class="form-group" v-if="!clearOptions.all">
              <label class="checkbox-label">
                <input type="checkbox" v-model="clearOptions.plugin">
                <span>插件日志</span>
              </label>
            </div>
            
            <div class="form-group" v-if="!clearOptions.all">
              <label class="checkbox-label">
                <input type="checkbox" v-model="clearOptions.llm">
                <span>LLM服务日志</span>
              </label>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="clearOptions.exportFirst">
                <span>清空前导出日志</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showClearModal = false">取消</button>
          <button 
            class="btn btn-danger" 
            @click="clearLogs"
            :disabled="!isClearEnabled"
          >
            <i class="fas fa-trash-alt"></i> 确认清空
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMainStore } from '@/stores/main'

const store = useMainStore()

// 状态数据
const logs = ref([])
const loading = ref(true)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const logLevelFilter = ref('all')
const sourceFilter = ref('all')
const startDate = ref('')
const endDate = ref('')
const expandedLogs = ref([])
const showLogDetailModal = ref(false)
const selectedLog = ref(null)
const showClearModal = ref(false)
const clearOptions = ref({
  all: true,
  system: false,
  plugin: false,
  llm: false,
  exportFirst: true
})

// 过滤日志
const filteredLogs = computed(() => {
  let result = logs.value
  
  // 按级别过滤
  if (logLevelFilter.value !== 'all') {
    result = result.filter(log => log.level === logLevelFilter.value)
  }
  
  // 按来源过滤
  if (sourceFilter.value !== 'all') {
    result = result.filter(log => log.source === sourceFilter.value)
  }
  
  // 按日期范围过滤
  if (startDate.value) {
    const startDateObj = new Date(startDate.value)
    result = result.filter(log => new Date(log.timestamp) >= startDateObj)
  }
  
  if (endDate.value) {
    const endDateObj = new Date(endDate.value)
    endDateObj.setHours(23, 59, 59, 999) // 设置为一天的结束
    result = result.filter(log => new Date(log.timestamp) <= endDateObj)
  }
  
  // 按搜索查询过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(log => 
      log.message.toLowerCase().includes(query) || 
      log.source.toLowerCase().includes(query)
    )
  }
  
  return result
})

// 分页数据
const paginatedLogs = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  const endIndex = startIndex + pageSize.value
  return filteredLogs.value.slice(startIndex, endIndex)
})

const totalPages = computed(() => 
  Math.max(1, Math.ceil(filteredLogs.value.length / pageSize.value))
)

// 清空按钮是否启用
const isClearEnabled = computed(() => {
  if (clearOptions.value.all) return true
  return clearOptions.value.system || clearOptions.value.plugin || clearOptions.value.llm
})

// 监听过滤器变化以重置页码
watch([logLevelFilter, sourceFilter, searchQuery, startDate, endDate], () => {
  currentPage.value = 1
})

// 获取日志数据
async function fetchLogs() {
  loading.value = true
  
  try {
    // 在实际应用中，通过API获取日志
    // const response = await api.get('/logs')
    // logs.value = response.data
    
    // 模拟数据
    logs.value = generateSampleLogs(100)
  } catch (err) {
    console.error('获取日志失败:', err)
    store.addNotification({
      message: '获取日志失败',
      type: 'error'
    })
  } finally {
    loading.value = false
  }
}

// 刷新日志
function refreshLogs() {
  fetchLogs()
  store.addNotification({
    message: '日志已刷新',
    type: 'info'
  })
}

// 导出日志
function exportLogs() {
  // 确定要导出的日志
  const logsToExport = filteredLogs.value
  
  // 转换为CSV格式
  const headers = ['时间', '级别', '来源', '消息']
  const csvContent = [
    headers.join(','),
    ...logsToExport.map(log => [
      log.timestamp,
      formatLevel(log.level),
      log.source,
      `"${log.message.replace(/"/g, '""')}"`
    ].join(','))
  ].join('\n')
  
  // 创建Blob并下载
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `AIVK_Logs_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  store.addNotification({
    message: '日志导出成功',
    type: 'success'
  })
}

// 清空日志
function clearLogs() {
  // 如果需要先导出
  if (clearOptions.value.exportFirst) {
    exportLogs()
  }
  
  // 在实际应用中，调用API清空日志
  // const options = { ...clearOptions.value }
  // await api.post('/logs/clear', options)
  
  // 模拟清空
  if (clearOptions.value.all) {
    logs.value = []
  } else {
    const sourcesToClear = []
    if (clearOptions.value.system) sourcesToClear.push('system')
    if (clearOptions.value.plugin) sourcesToClear.push('plugin')
    if (clearOptions.value.llm) sourcesToClear.push('llm')
    
    logs.value = logs.value.filter(log => !sourcesToClear.includes(log.source))
  }
  
  showClearModal.value = false
  
  store.addNotification({
    message: '日志已清空',
    type: 'success'
  })
}

// 复制日志
function copyLog(log) {
  const content = `[${log.timestamp}] [${formatLevel(log.level)}] [${log.source}] ${log.message}`
  
  navigator.clipboard.writeText(content).then(() => {
    store.addNotification({
      message: '日志已复制到剪贴板',
      type: 'success'
    })
  }).catch(err => {
    console.error('复制失败:', err)
    store.addNotification({
      message: '复制失败',
      type: 'error'
    })
  })
}

// 复制日志详情
function copyLogDetail() {
  if (!selectedLog.value) return
  
  const log = selectedLog.value
  let content = `时间: ${log.timestamp}\n`
  content += `级别: ${formatLevel(log.level)}\n`
  content += `来源: ${log.source}\n`
  content += `消息: ${log.message}\n`
  
  if (log.metadata) {
    content += `元数据: ${JSON.stringify(log.metadata, null, 2)}\n`
  }
  
  if (log.stackTrace) {
    content += `堆栈跟踪:\n${log.stackTrace}\n`
  }
  
  navigator.clipboard.writeText(content).then(() => {
    store.addNotification({
      message: '日志详情已复制到剪贴板',
      type: 'success'
    })
  }).catch(err => {
    console.error('复制失败:', err)
    store.addNotification({
      message: '复制失败',
      type: 'error'
    })
  })
}

// 展开/折叠日志消息
function toggleExpandLog(log) {
  const index = expandedLogs.value.indexOf(log.id)
  if (index === -1) {
    expandedLogs.value.push(log.id)
  } else {
    expandedLogs.value.splice(index, 1)
  }
}

// 显示日志详情
function showLogDetails(log) {
  selectedLog.value = log
  showLogDetailModal.value = true
}

// 格式化日期
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString()
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

// 生成示例日志（仅用于演示）
function generateSampleLogs(count) {
  const levels = ['info', 'warning', 'error', 'debug']
  const sources = ['system', 'plugin', 'llm', 'user']
  const messages = [
    '系统启动完成',
    '用户已登录',
    'API请求成功',
    '配置已更新',
    '连接超时',
    '权限被拒绝',
    '内存使用率过高',
    'LLM模型加载完成',
    '插件已启用',
    '服务器响应延迟超过阈值',
    '数据同步完成',
    '网络连接已恢复'
  ]
  
  const sampleLogs = []
  
  for (let i = 0; i < count; i++) {
    const level = levels[Math.floor(Math.random() * levels.length)]
    const source = sources[Math.floor(Math.random() * sources.length)]
    const message = messages[Math.floor(Math.random() * messages.length)]
    
    // 生成过去30天内的随机时间
    const date = new Date()
    date.setDate(date.getDate() - Math.floor(Math.random() * 30))
    date.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60))
    
    // 添加一些随机元数据和堆栈跟踪
    let metadata = null
    let stackTrace = null
    
    if (Math.random() > 0.7) {
      metadata = {
        userId: Math.floor(Math.random() * 1000),
        requestId: `req-${Math.random().toString(36).substring(2, 10)}`,
        duration: Math.floor(Math.random() * 1000),
        status: Math.random() > 0.2 ? 'success' : 'failed'
      }
    }
    
    if (level === 'error' && Math.random() > 0.5) {
      stackTrace = `Error: ${message}\n    at processInput (core.js:24:12)\n    at async runTask (tasks.js:45:5)\n    at async main (index.js:12:3)`
    }
    
    sampleLogs.push({
      id: i + 1,
      timestamp: date.toISOString(),
      level,
      source,
      message: `${message} [${i + 1}]`,
      metadata,
      stackTrace
    })
  }
  
  // 按时间降序排序
  return sampleLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.logs-view {
  padding-bottom: 40px;
}

.logs-header {
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

.filter-item {
  flex: 1;
  min-width: 150px;
}

.filter-item label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 5px;
}

.date-input {
  flex: 1;
}

.range-separator {
  color: var(--text-secondary);
}

.search-group {
  display: flex;
  align-items: center;
  gap: 15px;
}

.search-box {
  position: relative;
  flex: 1;
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
  height: 42px;
  padding: 0 40px;
  border-radius: 21px;
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

.logs-actions {
  display: flex;
  gap: 10px;
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

.loading-dots span {
  animation: dotFade 1.4s infinite;
  opacity: 0;
}

.loading-dots span:nth-child(1) {
  animation-delay: 0s;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotFade {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

.no-logs {
  text-align: center;
  padding: 40px;
}

.no-logs-icon {
  font-size: 48px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.no-logs-text {
  font-size: 20px;
  margin-bottom: 10px;
}

.no-logs-description {
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto;
}

.logs-container {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.log-entries {
  overflow-y: auto;
  max-height: 60vh;
}

.log-headers {
  display: flex;
  padding: 12px 15px;
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
  font-weight: 500;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 2;
}

.log-entry {
  display: flex;
  padding: 12px 15px;
  border-bottom: 1px solid var(--border-color);
  transition: background-color var(--transition-speed) ease;
  cursor: pointer;
}

.log-entry:hover {
  background-color: var(--bg-tertiary);
}

.log-entry.info {
  border-left: 3px solid var(--primary-color);
}

.log-entry.warning {
  border-left: 3px solid var(--warning-color);
}

.log-entry.error {
  border-left: 3px solid var(--danger-color);
}

.log-entry.debug {
  border-left: 3px solid var(--accent-color);
}

.log-header,
.log-time,
.log-level,
.log-source,
.log-message,
.log-actions {
  padding: 0 5px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.log-header.time,
.log-time {
  width: 170px;
  flex-shrink: 0;
}

.log-header.level,
.log-level {
  width: 60px;
  flex-shrink: 0;
}

.log-header.source,
.log-source {
  width: 100px;
  flex-shrink: 0;
}

.log-header.message,
.log-message {
  flex: 1;
}

.log-header.actions,
.log-actions {
  width: 80px;
  flex-shrink: 0;
  text-align: right;
}

.log-level {
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

.log-message.expanded {
  white-space: normal;
  word-break: break-word;
}

.action-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  margin-left: 5px;
  font-size: 14px;
  transition: all var(--transition-speed) ease;
}

.action-btn:hover {
  color: var(--primary-color);
}

.logs-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  padding: 15px;
  border-top: 1px solid var(--border-color);
  margin-top: auto;
}

.pagination-btn {
  width: 32px;
  height: 32px;
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

.pagination-btn:hover:not(:disabled) {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.page-size {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  color: var(--text-color);
  padding: 5px 10px;
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
  -webkit-backdrop-filter: blur(5px);
}

.modal-content {
  position: relative;
  width: 100%;
  max-width: 600px;
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

@keyframes modalSlideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* 日志详情样式 */
.log-detail-item {
  margin-bottom: 15px;
}

.detail-label {
  font-weight: 500;
  margin-bottom: 5px;
  color: var(--text-secondary);
}

.detail-value {
  padding: 8px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  word-break: break-word;
}

.log-message-detail {
  white-space: pre-wrap;
}

.log-metadata,
.log-stack-trace {
  white-space: pre-wrap;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

.level-info {
  color: var(--primary-color);
}

.level-warning {
  color: var(--warning-color);
}

.level-error {
  color: var(--danger-color);
}

.level-debug {
  color: var(--accent-color);
}

/* 清空日志选项 */
.clear-options {
  margin-top: 15px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-bottom: 10px;
}

.checkbox-label input {
  margin-right: 10px;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .filter-group {
    flex-direction: column;
    gap: 10px;
  }
  
  .filter-item {
    width: 100%;
  }
  
  .search-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .logs-actions {
    margin-top: 10px;
  }
}

@media (max-width: 768px) {
  .log-entry {
    flex-wrap: wrap;
  }
  
  .log-header.time,
  .log-time {
    width: 110px;
  }
  
  .log-header.source,
  .log-source {
    width: 80px;
  }
  
  .log-message {
    width: 100%;
    margin-top: 5px;
  }
}
</style>

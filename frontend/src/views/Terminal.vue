<template>
  <div class="terminal-view">
    <h1 class="page-title">终端命令</h1>
    
    <div class="terminal-container card">
      <div class="terminal-header">
        <div class="terminal-controls">
          <div class="control red"></div>
          <div class="control yellow"></div>
          <div class="control green"></div>
        </div>
        <div class="terminal-title">AIVK 命令行界面</div>
        <div class="terminal-actions">
          <button class="action-btn" @click="clearTerminal" title="清空">
            <i class="fas fa-trash-alt"></i>
          </button>
          <button class="action-btn" @click="copyTerminalContent" title="复制">
            <i class="fas fa-copy"></i>
          </button>
        </div>
      </div>
      
      <div class="terminal-body" ref="terminalBody">
        <div class="welcome-message">
          <div class="ascii-logo">
            <pre>
   _    _____     ____  __ 
  /_\  /  _/ \   / /  \/  |
 //_\\ | || |\ \ / /| |\/| |
/  _  \| || | \ V / | |  | |
\_/ \_/___/_|  \_/  |_|  |_|
            </pre>
          </div>
          <div class="welcome-text">
            欢迎使用 AIVK 终端 v1.0.0
            <br>输入 'help' 获取可用命令列表
          </div>
        </div>
        
        <div v-for="(item, index) in terminalHistory" :key="index" class="history-item">
          <div v-if="item.type === 'command'" class="command-line">
            <span class="prompt">aivk@user:~$</span>
            <span class="command">{{ item.content }}</span>
          </div>
          <div v-else class="output" :class="item.style">
            <pre>{{ item.content }}</pre>
          </div>
        </div>
        
        <div class="input-line">
          <span class="prompt">aivk@user:~$</span>
          <input 
            type="text" 
            ref="commandInput" 
            v-model="currentCommand" 
            class="command-input"
            @keydown.enter="executeCommand"
            @keydown.up="navigateHistory(1)"
            @keydown.down="navigateHistory(-1)"
            @keydown.tab.prevent="autocompleteCommand"
            autofocus
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useMainStore } from '@/stores/main'

const store = useMainStore()

// 状态
const terminalHistory = ref([])
const currentCommand = ref('')
const commandHistory = ref([])
const historyIndex = ref(-1)
const terminalBody = ref(null)
const commandInput = ref(null)

// 可用命令列表
const commands = {
  help: {
    description: '显示帮助信息',
    execute: () => {
      const helpText = [
        '可用命令:',
        '',
        '  help                  显示此帮助信息',
        '  clear                 清除终端',
        '  version               显示当前版本',
        '  ls [目录]             列出目录内容',
        '  plugins               显示已安装的插件',
        '  plugin install <名称> 安装插件',
        '  plugin remove <名称>  移除插件',
        '  llm list              列出LLM服务',
        '  llm test <名称>       测试LLM连接',
        '  status                显示系统状态',
        '  exit                  退出终端会话',
        '',
        '提示: 使用Tab键自动补全命令'
      ].join('\n')
      
      addOutput(helpText)
    }
  },
  clear: {
    description: '清除终端',
    execute: () => {
      clearTerminal()
    }
  },
  version: {
    description: '显示当前版本',
    execute: () => {
      addOutput('AIVK 版本 1.0.0\n内核版本: 0.9.2\n构建日期: 2023-12-01')
    }
  },
  ls: {
    description: '列出目录内容',
    execute: (args) => {
      const directory = args[0] || '.'
      
      if (directory === '.') {
        addOutput('config/  data/  plugins/  logs/  models/\nREADME.md  LICENSE  .env')
      } else if (directory === 'plugins') {
        if (store.plugins.length > 0) {
          const pluginsList = store.plugins.map(p => p.name).join('\n')
          addOutput(pluginsList)
        } else {
          addOutput('没有安装任何插件。', 'warning')
        }
      } else {
        addOutput(`访问 ${directory} 权限被拒绝`, 'error')
      }
    }
  },
  plugins: {
    description: '显示已安装的插件',
    execute: () => {
      if (store.plugins.length > 0) {
        const pluginsTable = [
          '已安装的插件:',
          '--------------------------------------------------------------',
          '名称                   | 版本     | 状态       | 作者',
          '--------------------------------------------------------------'
        ]
        
        store.plugins.forEach(plugin => {
          pluginsTable.push(
            `${plugin.name.padEnd(23)} | ${(plugin.version || '1.0.0').padEnd(8)} | ${(plugin.active ? '已启用' : '已禁用').padEnd(10)} | ${plugin.author || '未知'}`
          )
        })
        
        addOutput(pluginsTable.join('\n'))
      } else {
        addOutput('没有安装任何插件。', 'warning')
      }
    }
  },
  plugin: {
    description: '插件管理命令',
    execute: (args) => {
      const subCommand = args[0]
      const pluginName = args[1]
      
      if (!subCommand) {
        addOutput('使用方法: plugin [install|remove|info] [插件名称]', 'warning')
        return
      }
      
      if (subCommand === 'install') {
        if (!pluginName) {
          addOutput('请指定要安装的插件名称', 'error')
          return
        }
        
        addOutput(`正在安装插件 "${pluginName}"...`)
        
        // 模拟安装延迟
        setTimeout(() => {
          addOutput(`插件 "${pluginName}" 安装成功！`, 'success')
          // 实际应用中会真正安装插件
        }, 1500)
      } else if (subCommand === 'remove') {
        if (!pluginName) {
          addOutput('请指定要移除的插件名称', 'error')
          return
        }
        
        const plugin = store.plugins.find(p => p.name.toLowerCase() === pluginName.toLowerCase())
        
        if (plugin) {
          addOutput(`正在移除插件 "${plugin.name}"...`)
          
          // 模拟移除延迟
          setTimeout(() => {
            addOutput(`插件 "${plugin.name}" 已成功移除`, 'success')
            // 实际应用中会真正移除插件
          }, 1000)
        } else {
          addOutput(`找不到名为 "${pluginName}" 的插件`, 'error')
        }
      } else {
        addOutput(`未知的子命令: ${subCommand}`, 'error')
      }
    }
  },
  llm: {
    description: '管理LLM服务',
    execute: (args) => {
      const subCommand = args[0]
      const serviceName = args[1]
      
      if (!subCommand) {
        addOutput('使用方法: llm [list|test|info] [服务名称]', 'warning')
        return
      }
      
      if (subCommand === 'list') {
        if (store.llmServices?.length > 0) {
          const servicesTable = [
            'LLM服务:',
            '--------------------------------------------------------------',
            '名称                  | 状态       | 模型             | API调用',
            '--------------------------------------------------------------'
          ]
          
          store.llmServices.forEach(service => {
            servicesTable.push(
              `${service.name.padEnd(21)} | ${(service.enabled ? '已启用' : '已禁用').padEnd(10)} | ${(service.model || 'default').padEnd(16)} | ${service.apiCalls || 0}`
            )
          })
          
          addOutput(servicesTable.join('\n'))
        } else {
          addOutput('没有配置任何LLM服务。', 'warning')
        }
      } else if (subCommand === 'test') {
        if (!serviceName) {
          addOutput('请指定要测试的服务名称', 'error')
          return
        }
        
        addOutput(`正在测试 "${serviceName}" 连接...`)
        
        // 模拟测试延迟
        setTimeout(() => {
          addOutput(`服务 "${serviceName}" 连接正常！延迟: 142ms`, 'success')
        }, 1200)
      } else {
        addOutput(`未知的子命令: ${subCommand}`, 'error')
      }
    }
  },
  status: {
    description: '显示系统状态',
    execute: () => {
      const statusInfo = [
        'AIVK 系统状态:',
        '--------------------------------------------------------------',
        `版本:     1.0.0`,
        `运行时间:  ${formatUptime(Math.floor(Math.random() * 500000))}`,
        `CPU占用:  ${Math.floor(Math.random() * 30)}%`,
        `内存占用:  ${Math.floor(Math.random() * 800) + 200}MB / 2GB`,
        `插件数量:  ${store.plugins.length}`,
        `LLM服务:  ${store.llmServices?.length || 0}`,
        `API调用:  ${Math.floor(Math.random() * 1000)}`,
        `系统状态:  正常运行中`,
        '--------------------------------------------------------------'
      ].join('\n')
      
      addOutput(statusInfo)
    }
  },
  exit: {
    description: '退出终端会话',
    execute: () => {
      addOutput('正在退出终端会话...')
      setTimeout(() => {
        addOutput('感谢使用AIVK终端！再见！', 'success')
      }, 500)
    }
  }
}

// 添加输出到终端
function addOutput(content, style = '') {
  terminalHistory.value.push({
    type: 'output',
    content,
    style
  })
  
  scrollToBottom()
}

// 执行命令
function executeCommand() {
  if (!currentCommand.value.trim()) return
  
  const command = currentCommand.value.trim()
  
  // 添加命令到历史记录
  terminalHistory.value.push({
    type: 'command',
    content: command
  })
  
  // 添加命令到命令历史
  commandHistory.value.unshift(command)
  if (commandHistory.value.length > 50) {
    commandHistory.value.pop()
  }
  historyIndex.value = -1
  
  // 解析命令
  const parts = command.split(' ')
  const mainCommand = parts[0].toLowerCase()
  const args = parts.slice(1)
  
  // 执行命令
  if (commands[mainCommand]) {
    commands[mainCommand].execute(args)
  } else {
    addOutput(`命令未找到: ${mainCommand}. 输入 'help' 获取可用命令列表`, 'error')
  }
  
  // 清空当前命令
  currentCommand.value = ''
  scrollToBottom()
}

// 清空终端
function clearTerminal() {
  terminalHistory.value = []
}

// 复制终端内容
function copyTerminalContent() {
  const content = terminalHistory.value.map(item => {
    if (item.type === 'command') {
      return `$ ${item.content}`
    } else {
      return item.content
    }
  }).join('\n')
  
  navigator.clipboard.writeText(content).then(() => {
    store.addNotification({
      message: '终端内容已复制到剪贴板',
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

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (terminalBody.value) {
      terminalBody.value.scrollTop = terminalBody.value.scrollHeight
    }
  })
}

// 历史命令导航
function navigateHistory(direction) {
  if (commandHistory.value.length === 0) return
  
  // 向上导航
  if (direction > 0) {
    if (historyIndex.value < commandHistory.value.length - 1) {
      historyIndex.value++
    }
  } 
  // 向下导航
  else if (direction < 0) {
    if (historyIndex.value > -1) {
      historyIndex.value--
    }
  }
  
  if (historyIndex.value === -1) {
    currentCommand.value = ''
  } else {
    currentCommand.value = commandHistory.value[historyIndex.value]
  }
}

// 命令自动补全
function autocompleteCommand() {
  const input = currentCommand.value.trim()
  
  if (!input) return
  
  // 仅对第一个词进行自动补全
  const parts = input.split(' ')
  const firstWord = parts[0].toLowerCase()
  
  // 找到匹配的命令
  const matchingCommands = Object.keys(commands).filter(cmd => 
    cmd.startsWith(firstWord) && cmd !== firstWord
  )
  
  if (matchingCommands.length === 1) {
    // 替换第一个词
    parts[0] = matchingCommands[0]
    currentCommand.value = parts.join(' ')
  } else if (matchingCommands.length > 1) {
    // 显示可能的补全
    addOutput(`可能的补全: ${matchingCommands.join(' ')}`)
  }
}

// 格式化运行时间
function formatUptime(seconds) {
  const days = Math.floor(seconds / 86400)
  seconds %= 86400
  const hours = Math.floor(seconds / 3600)
  seconds %= 3600
  const minutes = Math.floor(seconds / 60)
  seconds %= 60
  
  const parts = []
  if (days > 0) parts.push(`${days}天`)
  if (hours > 0) parts.push(`${hours}小时`)
  if (minutes > 0) parts.push(`${minutes}分钟`)
  parts.push(`${seconds}秒`)
  
  return parts.join(' ')
}

// 生命周期钩子
onMounted(() => {
  // 自动聚焦到输入框
  commandInput.value.focus()
  
  // 点击终端时聚焦输入框
  terminalBody.value.addEventListener('click', () => {
    commandInput.value.focus()
  })
})
</script>

<style scoped>
.terminal-view {
  padding-bottom: 40px;
}

.terminal-container {
  margin-top: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 70vh;
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
  border-bottom: 1px solid var(--border-color);
}

.terminal-controls {
  display: flex;
  gap: 8px;
}

.control {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.control.red {
  background-color: #ff5f57;
}

.control.yellow {
  background-color: #febc2e;
}

.control.green {
  background-color: #28c941;
}

.terminal-title {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.terminal-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  transition: color var(--transition-speed) ease;
}

.action-btn:hover {
  color: var(--text-color);
}

.terminal-body {
  padding: 15px;
  overflow-y: auto;
  flex: 1;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.welcome-message {
  margin-bottom: 20px;
  color: var(--primary-color);
}

.ascii-logo {
  color: var(--primary-color);
  font-size: 12px;
  line-height: 1.2;
  margin-bottom: 10px;
}

.welcome-text {
  color: var(--text-secondary);
}

.history-item {
  margin-bottom: 10px;
}

.command-line {
  display: flex;
}

.prompt {
  color: var(--primary-color);
  margin-right: 8px;
  white-space: nowrap;
}

.command {
  color: var(--text-color);
}

.output {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 5px 0 10px 0;
  padding-left: 24px;
}

.output.error {
  color: var(--danger-color);
}

.output.warning {
  color: var(--warning-color);
}

.output.success {
  color: var(--success-color);
}

.input-line {
  display: flex;
  align-items: flex-start;
}

.command-input {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-color);
  font-family: 'Fira Code', monospace;
  font-size: 14px;
  padding: 0;
  outline: none;
}

pre {
  margin: 0;
  font-family: 'Fira Code', monospace;
  font-size: 14px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .terminal-container {
    min-height: 50vh;
  }
  
  .terminal-body {
    font-size: 12px;
  }
  
  .command-input {
    font-size: 12px;
  }
  
  .ascii-logo {
    font-size: 8px;
  }
}
</style>

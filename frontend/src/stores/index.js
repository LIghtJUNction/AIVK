import { defineStore } from 'pinia'

// 系统状态存储
export const useSystemStore = defineStore('system', {
  state: () => ({
    status: 'stopped', // running, stopped, error
    uptime: 0,
    version: '0.1.0',
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchStatus() {
      this.loading = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500))
        this.status = 'running'
        this.uptime = 3600
        this.error = null
      } catch (error) {
        this.error = error.message || '获取系统状态失败'
        console.error('Error fetching system status:', error)
      } finally {
        this.loading = false
      }
    },
    
    setStatus(status) {
      this.status = status
    }
  },
  
  getters: {
    isRunning: state => state.status === 'running',
    formattedUptime: state => {
      const seconds = state.uptime
      if (seconds < 60) return `${seconds}秒`
      const minutes = Math.floor(seconds / 60)
      if (minutes < 60) return `${minutes}分钟`
      const hours = Math.floor(minutes / 60)
      return `${hours}小时${minutes % 60}分钟`
    }
  }
})

// 插件状态存储
export const usePluginStore = defineStore('plugin', {
  state: () => ({
    plugins: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchPlugins() {
      this.loading = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 800))
        this.plugins = [
          {
            id: 'openai-provider',
            name: 'OpenAI Provider',
            version: '1.0.0',
            description: '提供OpenAI API集成，支持GPT-3.5和GPT-4模型。',
            author: 'AIVK Team',
            type: 'LLM Provider',
            enabled: true
          },
          {
            id: 'postgres-data',
            name: 'PostgreSQL Data Source',
            version: '0.9.2',
            description: '连接PostgreSQL数据库的数据源插件。',
            author: 'Database Team',
            type: 'Data Source',
            enabled: false
          },
          {
            id: 'file-tools',
            name: 'File Management Tools',
            version: '1.2.1',
            description: '提供文件管理相关工具和命令。',
            author: 'Utility Devs',
            type: 'Tool',
            enabled: true
          }
        ]
        this.error = null
      } catch (error) {
        this.error = error.message || '获取插件列表失败'
        console.error('Error fetching plugins:', error)
      } finally {
        this.loading = false
      }
    },
    
    togglePlugin(pluginId) {
      const plugin = this.plugins.find(p => p.id === pluginId)
      if (plugin) {
        plugin.enabled = !plugin.enabled
      }
    }
  },
  
  getters: {
    enabledPlugins: state => state.plugins.filter(p => p.enabled),
    disabledPlugins: state => state.plugins.filter(p => !p.enabled),
    getPluginById: state => id => state.plugins.find(p => p.id === id)
  }
})

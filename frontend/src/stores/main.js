import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
  state: () => ({
    // 通知
    notifications: [],
    notificationId: 0,
    
    // 最近访问页面
    recentPages: [],
    
    // 插件分类
    pluginCategories: [
      { id: 'mcp', name: 'MCP服务插件', icon: 'fa-server' },
      { id: 'llm', name: 'LLM提供者插件', icon: 'fa-brain' },
      { id: 'tool', name: '工具插件', icon: 'fa-tools' },
      { id: 'extension', name: '扩展插件', icon: 'fa-puzzle-piece' }
    ],
    
    // 模拟插件数据
    plugins: [
      {
        id: 1,
        name: "文本分析插件",
        description: "提供高级文本分析功能，包括情感分析、实体识别等",
        version: "1.2.0",
        author: "数据科学团队",
        icon: "fa-comment-dots",
        color: "rgba(0, 168, 255, 0.2)",
        active: true,
        status: "正常运行中",
        category: "tool"
      },
      {
        id: 2,
        name: "PDF转换器",
        description: "将各种文档格式转换为PDF，支持批量处理",
        version: "2.1.0",
        author: "文档处理小组",
        icon: "fa-file-pdf",
        color: "rgba(255, 94, 87, 0.2)",
        active: false,
        status: "已停用",
        category: "tool"
      },
      {
        id: 3,
        name: "Claude集成",
        description: "集成Anthropic的Claude大型语言模型API",
        version: "1.0.5",
        author: "AI集成团队",
        icon: "fa-brain",
        color: "rgba(127, 17, 224, 0.2)",
        active: true,
        status: "正常运行中",
        category: "llm"
      },
      {
        id: 4,
        name: "MCP核心服务",
        description: "基础MCP服务插件，提供核心功能",
        version: "2.0.1",
        author: "核心团队",
        icon: "fa-microchip",
        color: "rgba(5, 196, 107, 0.2)",
        active: true,
        status: "正常运行中",
        category: "mcp"
      },
      {
        id: 5,
        name: "数据同步服务",
        description: "在多设备间同步用户数据和设置",
        version: "1.3.2",
        author: "云服务团队",
        icon: "fa-sync-alt",
        color: "rgba(255, 168, 1, 0.2)",
        active: true,
        status: "正常运行中",
        category: "mcp"
      },
      {
        id: 6,
        name: "Mistral AI接入",
        description: "连接到Mistral AI的语言模型API",
        version: "1.0.0",
        author: "AI集成团队",
        icon: "fa-robot",
        color: "rgba(0, 210, 255, 0.2)",
        active: false,
        status: "已停用",
        category: "llm"
      }
    ],
    
    // 模拟LLM服务数据
    llmServices: [
      {
        id: 1,
        name: "OpenAI",
        status: "connected",
        icon: "fa-robot",
        enabled: true,
        apiCalls: 1245,
        avgResponse: "320ms",
        model: "gpt-4",
        endpoint: "https://api.openai.com/v1"
      },
      {
        id: 2,
        name: "Anthropic",
        status: "connected",
        icon: "fa-comments",
        enabled: true,
        apiCalls: 856,
        avgResponse: "450ms",
        model: "claude-2",
        endpoint: "https://api.anthropic.com"
      },
      {
        id: 3,
        name: "Google Gemini",
        status: "disconnected",
        icon: "fa-lightbulb",
        enabled: false,
        apiCalls: 0,
        avgResponse: "0ms",
        model: "gemini-pro",
        endpoint: "https://generativelanguage.googleapis.com"
      }
    ],
    
    // 模拟活动数据
    activities: [
      {
        id: 1,
        type: "info",
        message: "系统启动完成",
        time: "2023-12-15 08:30:45"
      },
      {
        id: 2,
        type: "success",
        message: "成功连接到OpenAI API服务",
        time: "2023-12-15 08:31:12"
      },
      {
        id: 3,
        type: "warning",
        message: "API额度使用已达到80%，请考虑升级",
        time: "2023-12-15 10:15:30"
      },
      {
        id: 4,
        type: "error",
        message: "插件'图片生成器'加载失败，缺少依赖库",
        time: "2023-12-15 11:47:03"
      },
      {
        id: 5,
        type: "info",
        message: "系统更新可用 (v1.2.0)",
        time: "2023-12-15 14:22:10"
      }
    ]
  }),
  
  actions: {
    // 通知相关
    addNotification(notification) {
      const id = ++this.notificationId
      const newNotification = {
        id,
        type: notification.type || 'info',
        message: notification.message,
        duration: notification.duration || 5000
      }
      
      this.notifications.push(newNotification)
      
      // 自动移除通知
      if (newNotification.duration > 0) {
        setTimeout(() => {
          this.removeNotification(id)
        }, newNotification.duration)
      }
      
      return id
    },
    
    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index !== -1) {
        this.notifications.splice(index, 1)
      }
    },
    
    markAllNotificationsAsRead() {
      this.notifications.forEach(notification => {
        notification.read = true
      })
    },
    
    // 最近访问页面
    addRecentPage(route) {
      // 不记录隐藏页面
      if (route.meta.hidden) return
      
      // 删除已存在的相同页面
      this.recentPages = this.recentPages.filter(page => page.path !== route.path)
      
      // 添加到最前面
      this.recentPages.unshift({
        name: route.name,
        path: route.path,
        title: route.meta.title || route.name,
        icon: route.meta.icon || 'fa-link',
        timestamp: new Date().toISOString()
      })
      
      // 限制最大数量
      if (this.recentPages.length > 10) {
        this.recentPages = this.recentPages.slice(0, 10)
      }
      
      // 保存到本地存储
      localStorage.setItem('recentPages', JSON.stringify(this.recentPages))
    },
    
    loadRecentPages() {
      try {
        const stored = localStorage.getItem('recentPages')
        if (stored) {
          this.recentPages = JSON.parse(stored)
        }
      } catch (error) {
        console.error('加载最近页面失败:', error)
        this.recentPages = []
      }
    },
    
    // 插件相关
    fetchPlugins() {
      // 在实际应用中，这里会调用API获取插件列表
      console.log('Fetching plugins...')
      // 这里使用的是预设的模拟数据
    },
    
    togglePlugin(pluginId) {
      const plugin = this.plugins.find(p => p.id === pluginId)
      if (plugin) {
        plugin.active = !plugin.active
        plugin.status = plugin.active ? '正常运行中' : '已停用'
      }
    },
    
    getPluginsByCategory(category) {
      return this.plugins.filter(plugin => plugin.category === category)
    },
    
    getCategoryName(categoryId) {
      const category = this.pluginCategories.find(c => c.id === categoryId)
      return category ? category.name : '未分类'
    },
    
    getCategoryIcon(categoryId) {
      const category = this.pluginCategories.find(c => c.id === categoryId)
      return category ? category.icon : 'fa-question-circle'
    },
    
    // LLM服务相关
    fetchLLMServices() {
      // 在实际应用中，这里会调用API获取LLM服务列表
      console.log('Fetching LLM services...')
      // 这里使用的是预设的模拟数据
    },
    
    toggleLLMService(serviceId) {
      const service = this.llmServices.find(s => s.id === serviceId)
      if (service) {
        service.enabled = !service.enabled
        service.status = service.enabled ? 'connected' : 'disconnected'
      }
    },
    
    // 活动相关
    fetchActivities() {
      // 在实际应用中，这里会调用API获取活动记录
      console.log('Fetching activities...')
      // 这里使用的是预设的模拟数据
    }
  }
})

/**
 * 前端事件总线服务
 * 负责与后端WebSocket事件系统对接和前端组件间通信
 */
import { reactive } from 'vue'

// 事件类型常量
export const EventType = {
  // 系统事件
  SYSTEM_STATUS_CHANGE: 'system:status:change',
  SYSTEM_ERROR: 'system:error',
  
  // LLM服务事件
  LLM_CONNECTED: 'llm:connected',
  LLM_DISCONNECTED: 'llm:disconnected',
  LLM_ERROR: 'llm:error',
  LLM_RESPONSE: 'llm:response',
  
  // 插件事件
  PLUGIN_INSTALLED: 'plugin:installed',
  PLUGIN_UNINSTALLED: 'plugin:uninstalled',
  PLUGIN_ACTIVATED: 'plugin:activated',
  PLUGIN_DEACTIVATED: 'plugin:deactivated',
  PLUGIN_ERROR: 'plugin:error',
  
  // 用户界面事件
  UI_NOTIFICATION: 'ui:notification',
  UI_THEME_CHANGE: 'ui:theme:change',
  UI_LANGUAGE_CHANGE: 'ui:language:change'
}

class EventBus {
  constructor() {
    this.listeners = reactive({})
    this.socket = null
    this.connected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectTimeout = null
    this.reconnectDelay = 3000 // 初始重连延迟 (3秒)
  }
  
  /**
   * 初始化WebSocket连接
   * @param {string} url WebSocket服务器URL
   */
  connect(url = 'ws://localhost:8000/ws/events') {
    if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || 
                         this.socket.readyState === WebSocket.OPEN)) {
      console.log('WebSocket已连接或正在连接')
      return
    }
    
    this.socket = new WebSocket(url)
    
    this.socket.onopen = () => {
      console.log('WebSocket连接已建立')
      this.connected = true
      this.reconnectAttempts = 0
      this.emit(EventType.SYSTEM_STATUS_CHANGE, { connected: true })
    }
    
    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        console.log('收到WebSocket消息:', message)
        
        if (message.signal && message.data) {
          this.emit(message.signal, message.data)
        }
      } catch (error) {
        console.error('处理WebSocket消息时出错:', error)
      }
    }
    
    this.socket.onclose = (event) => {
      this.connected = false
      console.log(`WebSocket连接已关闭, 代码: ${event.code}, 原因: ${event.reason}`)
      this.emit(EventType.SYSTEM_STATUS_CHANGE, { connected: false })
      
      // 尝试重新连接
      this.attemptReconnect()
    }
    
    this.socket.onerror = (error) => {
      console.error('WebSocket错误:', error)
      this.emit(EventType.SYSTEM_ERROR, { 
        message: 'WebSocket连接错误', 
        error 
      })
    }
  }
  
  /**
   * 尝试重新连接WebSocket
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('已达到最大重连尝试次数')
      return
    }
    
    // 使用指数退避策略增加重连延迟时间
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts)
    
    console.log(`将在 ${delay}ms 后尝试重新连接 (尝试 ${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`)
    
    clearTimeout(this.reconnectTimeout)
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++
      this.connect()
    }, delay)
  }
  
  /**
   * 关闭WebSocket连接
   */
  disconnect() {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    
    clearTimeout(this.reconnectTimeout)
  }
  
  /**
   * 向后端发送事件
   * @param {string} signal 事件信号
   * @param {object} data 事件数据
   */
  send(signal, data = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket未连接')
      return
    }
    
    const message = {
      signal,
      data,
      sender: 'frontend'
    }
    
    this.socket.send(JSON.stringify(message))
  }
  
  /**
   * 发布前端事件（组件间通信）
   * @param {string} eventName 事件名称
   * @param {any} payload 事件数据
   */
  emit(eventName, payload) {
    if (!this.listeners[eventName]) {
      return
    }
    
    for (const callback of this.listeners[eventName]) {
      try {
        callback(payload)
      } catch (error) {
        console.error(`事件处理器错误 (${eventName}):`, error)
      }
    }
  }
  
  /**
   * 订阅前端事件
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   * @returns {Function} 取消订阅的函数
   */
  on(eventName, callback) {
    if (!this.listeners[eventName]) {
      this.listeners[eventName] = []
    }
    
    this.listeners[eventName].push(callback)
    
    // 返回取消订阅的函数
    return () => this.off(eventName, callback)
  }
  
  /**
   * 取消订阅前端事件
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   */
  off(eventName, callback) {
    if (!this.listeners[eventName]) {
      return
    }
    
    this.listeners[eventName] = this.listeners[eventName].filter(
      listener => listener !== callback
    )
  }
  
  /**
   * 订阅一次性事件
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   */
  once(eventName, callback) {
    const onceCallback = (payload) => {
      this.off(eventName, onceCallback)
      callback(payload)
    }
    
    this.on(eventName, onceCallback)
  }
}

// 创建单例实例
const eventBus = new EventBus()

export default eventBus

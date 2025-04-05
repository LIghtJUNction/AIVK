/**
 * 事件服务
 * 封装WebSocket和事件总线，提供更高级的事件处理功能
 */
import { onUnmounted } from 'vue'
import { useMainStore } from '@/stores/main'
import eventBus, { EventType } from './eventBus'

/**
 * 初始化事件服务
 * @param {string} url WebSocket服务器URL
 */
export function initEventService(url = 'ws://localhost:8000/ws/events') {
  const store = useMainStore()
  
  // 连接WebSocket
  eventBus.connect(url)
  
  // 订阅系统状态变化事件
  eventBus.on(EventType.SYSTEM_STATUS_CHANGE, (data) => {
    store.updateSystemStatus(data)
  })
  
  // 订阅系统错误事件
  eventBus.on(EventType.SYSTEM_ERROR, (data) => {
    console.error('系统错误:', data.message)
    store.addNotification({
      message: `系统错误: ${data.message}`,
      type: 'error'
    })
  })
  
  // 订阅LLM服务连接事件
  eventBus.on(EventType.LLM_CONNECTED, (data) => {
    store.updateLLMServiceStatus(data.serviceId, true)
    store.addNotification({
      message: `${data.serviceName} 服务已连接`,
      type: 'success'
    })
  })
  
  // 订阅LLM服务断开事件
  eventBus.on(EventType.LLM_DISCONNECTED, (data) => {
    store.updateLLMServiceStatus(data.serviceId, false)
    store.addNotification({
      message: `${data.serviceName} 服务已断开`,
      type: 'warning'
    })
  })
  
  // 订阅LLM服务错误事件
  eventBus.on(EventType.LLM_ERROR, (data) => {
    store.addNotification({
      message: `LLM服务错误: ${data.message}`,
      type: 'error'
    })
  })
  
  // 订阅插件安装事件
  eventBus.on(EventType.PLUGIN_INSTALLED, (data) => {
    store.addPlugin(data.plugin)
    store.addNotification({
      message: `插件 ${data.plugin.name} 已安装`,
      type: 'success'
    })
  })
  
  // 订阅插件卸载事件
  eventBus.on(EventType.PLUGIN_UNINSTALLED, (data) => {
    store.removePlugin(data.pluginId)
    store.addNotification({
      message: `插件已卸载`,
      type: 'info'
    })
  })
  
  // 订阅插件激活事件
  eventBus.on(EventType.PLUGIN_ACTIVATED, (data) => {
    store.updatePluginStatus(data.pluginId, true)
  })
  
  // 订阅插件停用事件
  eventBus.on(EventType.PLUGIN_DEACTIVATED, (data) => {
    store.updatePluginStatus(data.pluginId, false)
  })
  
  // 订阅插件错误事件
  eventBus.on(EventType.PLUGIN_ERROR, (data) => {
    store.addNotification({
      message: `插件错误: ${data.message}`,
      type: 'error'
    })
  })
  
  // 返回清理函数
  return () => {
    eventBus.disconnect()
  }
}

/**
 * 组合式函数: 使用事件服务
 * 在Vue组件中订阅事件并在组件卸载时自动清理
 * @param {string} eventName 事件名称
 * @param {Function} callback 回调函数
 */
export function useEvent(eventName, callback) {
  const unsubscribe = eventBus.on(eventName, callback)
  
  // 组件卸载时自动取消订阅
  onUnmounted(() => {
    unsubscribe()
  })
}

/**
 * 发送事件到后端
 * @param {string} signal 事件信号
 * @param {object} data 事件数据
 */
export function sendEvent(signal, data = {}) {
  eventBus.send(signal, data)
}

/**
 * 广播本地事件
 * @param {string} eventName 事件名称
 * @param {any} payload 事件数据
 */
export function emitEvent(eventName, payload) {
  eventBus.emit(eventName, payload)
}

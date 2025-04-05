<template>
  <div class="notifications-container">
    <TransitionGroup name="notification">
      <div 
        v-for="notification in notifications" 
        :key="notification.id" 
        class="notification"
        :class="notification.type"
      >
        <div class="notification-icon">
          <i :class="getNotificationIcon(notification.type)"></i>
        </div>
        
        <div class="notification-content">
          <div class="notification-message">{{ notification.message }}</div>
        </div>
        
        <button class="close-btn" @click="closeNotification(notification.id)">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useMainStore } from '@/stores/main'

const store = useMainStore()

// 通知列表
const notifications = computed(() => store.notifications)

// 获取通知类型图标
function getNotificationIcon(type) {
  const icons = {
    'success': 'fas fa-check-circle',
    'error': 'fas fa-times-circle',
    'warning': 'fas fa-exclamation-triangle',
    'info': 'fas fa-info-circle'
  }
  return icons[type] || icons.info
}

// 关闭通知
function closeNotification(id) {
  store.removeNotification(id)
}
</script>

<style scoped>
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  width: 350px;
  max-width: calc(100vw - 40px);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification {
  display: flex;
  align-items: flex-start;
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid var(--primary-color);
  overflow: hidden;
}

.notification-icon {
  margin-right: 12px;
  font-size: 20px;
  color: var(--primary-color);
}

.notification-content {
  flex: 1;
}

.notification-message {
  font-size: 14px;
  line-height: 1.4;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  opacity: 0.7;
  transition: opacity var(--transition-speed) ease;
  padding: 0;
  margin-left: 10px;
  font-size: 14px;
}

.close-btn:hover {
  opacity: 1;
}

/* 通知类型样式 */
.notification.success {
  border-left-color: var(--success-color);
}

.notification.success .notification-icon {
  color: var(--success-color);
}

.notification.error {
  border-left-color: var(--danger-color);
}

.notification.error .notification-icon {
  color: var(--danger-color);
}

.notification.warning {
  border-left-color: var(--warning-color);
}

.notification.warning .notification-icon {
  color: var(--warning-color);
}

.notification.info {
  border-left-color: var(--primary-color);
}

.notification.info .notification-icon {
  color: var(--primary-color);
}

/* 动画 */
.notification-enter-active, 
.notification-leave-active {
  transition: all 0.3s ease;
  max-height: 200px;
  opacity: 1;
  transform: translateY(0) scale(1);
}

.notification-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.9);
  max-height: 0;
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100px);
  max-height: 0;
}

@media (max-width: 480px) {
  .notifications-container {
    bottom: 10px;
    top: auto;
    right: 10px;
    left: 10px;
    width: auto;
  }
}
</style>

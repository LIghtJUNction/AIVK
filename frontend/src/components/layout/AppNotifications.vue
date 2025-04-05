<template>
  <div class="notifications-container">
    <Transition-group name="notification">
      <div 
        v-for="notification in notifications" 
        :key="notification.id" 
        class="notification" 
        :class="notification.type"
      >
        <div class="notification-icon">
          <i :class="getIconClass(notification.type)"></i>
        </div>
        <div class="notification-content">
          <div class="notification-message">{{ notification.message }}</div>
          <div class="notification-time">{{ notification.time }}</div>
        </div>
        <button class="notification-close" @click="removeNotification(notification.id)">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </Transition-group>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useMainStore } from '@/stores/main'

const store = useMainStore()

// 从store获取通知
const notifications = computed(() => store.notifications)

// 获取图标类名
function getIconClass(type) {
  const iconMap = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }
  return iconMap[type] || 'fas fa-bell'
}

// 移除通知
function removeNotification(id) {
  store.removeNotification(id)
}
</script>

<style scoped>
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: var(--z-index-notifications);
  max-width: 350px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notification {
  display: flex;
  align-items: center;
  padding: 15px;
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease;
  max-width: 100%;
}

.notification.success {
  border-left: 4px solid var(--success-color);
}

.notification.error {
  border-left: 4px solid var(--danger-color);
}

.notification.warning {
  border-left: 4px solid var(--warning-color);
}

.notification.info {
  border-left: 4px solid var(--primary-color);
}

.notification-icon {
  margin-right: 15px;
  font-size: 20px;
}

.notification.success .notification-icon {
  color: var(--success-color);
}

.notification.error .notification-icon {
  color: var(--danger-color);
}

.notification.warning .notification-icon {
  color: var(--warning-color);
}

.notification.info .notification-icon {
  color: var(--primary-color);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  font-size: 14px;
  color: var(--text-color);
  word-break: break-word;
}

.notification-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.notification-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 5px;
  margin-left: 10px;
  transition: color var(--transition-speed) ease;
}

.notification-close:hover {
  color: var(--text-color);
}

/* 通知动画 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式调整 */
@media (max-width: 576px) {
  .notifications-container {
    left: 10px;
    right: 10px;
    top: 10px;
  }
  
  .notification {
    padding: 10px;
  }
  
  .notification-icon {
    margin-right: 10px;
    font-size: 18px;
  }
}
</style>

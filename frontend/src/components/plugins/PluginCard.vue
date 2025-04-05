<template>
  <div class="plugin-card card" :class="{ disabled: !plugin.active }">
    <div class="plugin-header">
      <div class="plugin-icon" :style="{ backgroundColor: plugin.color || 'rgba(0, 168, 255, 0.2)' }">
        <i :class="`fas ${plugin.icon || 'fa-puzzle-piece'}`"></i>
      </div>
      <div class="plugin-title">
        <h3>{{ plugin.name }}</h3>
        <div class="plugin-badges">
          <span class="plugin-version" v-if="plugin.version">v{{ plugin.version }}</span>
          <span class="plugin-status" :class="{ active: plugin.active }">
            {{ plugin.active ? '已启用' : '已禁用' }}
          </span>
        </div>
      </div>
      <div class="plugin-toggle">
        <div class="toggle-switch" @click="$emit('toggle', plugin.id)">
          <div class="toggle-track" :class="{ active: plugin.active }">
            <div class="toggle-thumb"></div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="plugin-description">
      {{ plugin.description || '暂无描述' }}
    </div>
    
    <div class="plugin-footer">
      <div class="plugin-meta">
        <span v-if="plugin.author"><i class="fas fa-user"></i> {{ plugin.author }}</span>
        <span v-if="plugin.updatedAt"><i class="fas fa-calendar"></i> {{ formatDate(plugin.updatedAt) }}</span>
      </div>
      <div class="plugin-actions">
        <router-link :to="`/plugins/${plugin.id}`" class="btn-icon" title="详情">
          <i class="fas fa-info-circle"></i>
        </router-link>
        <button class="btn-icon" title="设置" @click="$emit('settings', plugin.id)">
          <i class="fas fa-cog"></i>
        </button>
        <button class="btn-icon danger" title="卸载" @click="$emit('uninstall', plugin.id)">
          <i class="fas fa-trash-alt"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// 接收属性
const props = defineProps({
  plugin: {
    type: Object,
    required: true
  }
})

// 定义事件
defineEmits(['toggle', 'settings', 'uninstall'])

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
}
</script>

<style scoped>
.plugin-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all var(--transition-speed) ease;
}

.plugin-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--glow-shadow);
}

.plugin-card.disabled {
  opacity: 0.7;
}

.plugin-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.plugin-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: var(--primary-color);
}

.plugin-title {
  flex: 1;
}

.plugin-title h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.plugin-badges {
  display: flex;
  gap: 8px;
}

.plugin-version {
  font-size: 12px;
  padding: 2px 6px;
  background-color: var(--bg-tertiary);
  border-radius: 10px;
  color: var(--text-secondary);
}

.plugin-status {
  font-size: 12px;
  padding: 2px 6px;
  background-color: var(--bg-tertiary);
  border-radius: 10px;
  color: var(--text-secondary);
}

.plugin-status.active {
  background-color: rgba(5, 196, 107, 0.2);
  color: var(--success-color);
}

.toggle-switch {
  cursor: pointer;
}

.toggle-track {
  width: 40px;
  height: 20px;
  background-color: var(--bg-tertiary);
  border-radius: 20px;
  position: relative;
  transition: all var(--transition-speed) ease;
}

.toggle-track.active {
  background-color: var(--primary-color);
}

.toggle-thumb {
  width: 16px;
  height: 16px;
  background-color: var(--text-color);
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: all var(--transition-speed) ease;
}

.toggle-track.active .toggle-thumb {
  left: 22px;
}

.plugin-description {
  margin-bottom: 15px;
  color: var(--text-secondary);
  font-size: 14px;
  flex: 1;
  line-height: 1.5;
}

.plugin-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  padding-top: 15px;
  margin-top: auto;
}

.plugin-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12px;
  color: var(--text-secondary);
}

.plugin-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.plugin-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
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

.btn-icon:hover {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn-icon.danger:hover {
  background-color: rgba(255, 94, 87, 0.1);
  color: var(--danger-color);
  border-color: var(--danger-color);
}

/* 响应式布局 */
@media (max-width: 768px) {
  .plugin-meta {
    display: none;
  }
}
</style>

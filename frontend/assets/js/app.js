// AIVK前端应用基础JS文件
(function() {
  'use strict';
  
  // 获取系统状态
  function getSystemStatus() {
    const statusElement = document.getElementById('status');
    if (!statusElement) return;
    
    fetch('/api/status')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        let statusHtml = `
          <div class="card">
            <h3>系统状态</h3>
            <p>状态: ${data.state === 'RUNNING' ? '运行中' : '已停止'}</p>
            <p>运行时间: ${formatUptime(data.uptime)}</p>
            <p>插件数量: ${data.plugins.total}</p>
            <p>已启用插件: ${data.plugins.enabled}</p>
          </div>
        `;
        statusElement.innerHTML = statusHtml;
      })
      .catch(error => {
        statusElement.innerHTML = `
          <div class="alert alert-error">
            获取系统状态失败: ${error.message}
          </div>
        `;
      });
  }
  
  // 获取插件列表
  function getPlugins() {
    const pluginsElement = document.getElementById('plugins');
    if (!pluginsElement) return;
    
    fetch('/api/plugins')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        if (Object.keys(data).length === 0) {
          pluginsElement.innerHTML = '<p>无已安装插件</p>';
          return;
        }
        
        let pluginsHtml = '<div class="plugin-list">';
        
        for (const [id, plugin] of Object.entries(data)) {
          pluginsHtml += `
            <div class="card">
              <h3>${plugin.name} <span class="version">v${plugin.version}</span></h3>
              <p>${plugin.description}</p>
              <div class="plugin-meta">
                <span class="status ${plugin.enabled ? 'enabled' : 'disabled'}">
                  ${plugin.enabled ? '已启用' : '已禁用'}
                </span>
                <span>状态: ${plugin.state}</span>
              </div>
            </div>
          `;
        }
        
        pluginsHtml += '</div>';
        pluginsElement.innerHTML = pluginsHtml;
      })
      .catch(error => {
        pluginsElement.innerHTML = `
          <div class="alert alert-error">
            获取插件列表失败: ${error.message}
          </div>
        `;
      });
  }
  
  // 格式化运行时间
  function formatUptime(seconds) {
    if (!seconds || seconds <= 0) return '0秒';
    
    if (seconds < 60) return `${seconds}秒`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}分钟`;
    const hours = Math.floor(minutes / 60);
    return `${hours}小时${minutes % 60}分钟`;
  }
  
  // 初始化
  function init() {
    // 获取系统状态和插件列表
    getSystemStatus();
    getPlugins();
  }
  
  // 页面加载完成后执行初始化
  document.addEventListener('DOMContentLoaded', init);
})();

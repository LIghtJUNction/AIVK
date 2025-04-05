<template>
  <div class="not-found-view">
    <div class="not-found-container card">
      <div class="not-found-content">
        <div class="error-code">404</div>
        <h1 class="error-title">页面未找到</h1>
        <p class="error-description">
          抱歉，您要查找的页面不存在或已被移动。请检查URL是否正确，或使用下面的按钮返回首页。
        </p>
        
        <div class="error-actions">
          <button class="btn" @click="goBack">
            <i class="fas fa-arrow-left"></i> 返回上一页
          </button>
          <router-link to="/" class="btn btn-primary">
            <i class="fas fa-home"></i> 返回首页
          </router-link>
        </div>
      </div>
      
      <div class="not-found-illustration">
        <div class="illustration-container">
          <div class="planet"></div>
          <div class="astronaut">
            <div class="astronaut-body"></div>
            <div class="astronaut-head"></div>
            <div class="astronaut-arm-left"></div>
            <div class="astronaut-arm-right"></div>
            <div class="astronaut-leg-left"></div>
            <div class="astronaut-leg-right"></div>
          </div>
          <div class="stars"></div>
        </div>
      </div>
    </div>
    
    <div class="suggestions card">
      <h2>您可能要查找：</h2>
      <div class="suggestion-links">
        <router-link to="/" class="suggestion-link">
          <i class="fas fa-chart-line"></i>
          <span>仪表盘</span>
        </router-link>
        <router-link to="/plugins" class="suggestion-link">
          <i class="fas fa-puzzle-piece"></i>
          <span>插件管理</span>
        </router-link>
        <router-link to="/llm-services" class="suggestion-link">
          <i class="fas fa-brain"></i>
          <span>LLM服务</span>
        </router-link>
        <router-link to="/settings" class="suggestion-link">
          <i class="fas fa-cog"></i>
          <span>系统设置</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

function goBack() {
  router.go(-1);
}
</script>

<style scoped>
.not-found-view {
  padding-bottom: 40px;
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.not-found-container {
  display: flex;
  align-items: center;
  padding: 40px;
  gap: 40px;
  overflow: hidden;
}

.not-found-content {
  flex: 1;
  max-width: 600px;
}

.error-code {
  font-family: 'Orbitron', sans-serif;
  font-size: 120px;
  font-weight: 700;
  line-height: 1;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 15px rgba(0, 168, 255, 0.5);
  margin-bottom: 10px;
}

.error-title {
  font-size: 36px;
  margin-bottom: 20px;
}

.error-description {
  color: var(--text-secondary);
  font-size: 18px;
  line-height: 1.6;
  margin-bottom: 30px;
}

.error-actions {
  display: flex;
  gap: 15px;
}

.not-found-illustration {
  position: relative;
  width: 300px;
  height: 300px;
  flex-shrink: 0;
}

/* 创建一个简单的太空场景 */
.illustration-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.planet {
  position: absolute;
  width: 150px;
  height: 150px;
  background: radial-gradient(circle at 30% 30%, var(--primary-color), var(--secondary-color));
  border-radius: 50%;
  bottom: 30px;
  right: 30px;
  box-shadow: 0 0 30px rgba(0, 168, 255, 0.5);
}

.astronaut {
  position: absolute;
  top: 50%;
  left: 40%;
  transform: translate(-50%, -50%);
  animation: float 6s ease-in-out infinite;
}

.astronaut-body {
  width: 50px;
  height: 70px;
  background-color: #f0f0f0;
  border-radius: 20px;
}

.astronaut-head {
  position: absolute;
  top: -30px;
  left: 10px;
  width: 30px;
  height: 30px;
  background-color: #f0f0f0;
  border-radius: 50%;
  border: 2px solid #ccc;
}

.astronaut-arm-left, .astronaut-arm-right {
  position: absolute;
  width: 12px;
  height: 35px;
  background-color: #f0f0f0;
  border-radius: 6px;
}

.astronaut-arm-left {
  top: 5px;
  left: -10px;
  transform: rotate(20deg);
}

.astronaut-arm-right {
  top: 5px;
  right: -10px;
  transform: rotate(-20deg);
}

.astronaut-leg-left, .astronaut-leg-right {
  position: absolute;
  width: 15px;
  height: 40px;
  background-color: #f0f0f0;
  border-radius: 7px;
  bottom: -40px;
}

.astronaut-leg-left {
  left: 10px;
}

.astronaut-leg-right {
  right: 10px;
}

.stars {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(2px 2px at 20px 30px, #fff, rgba(0, 0, 0, 0)),
                    radial-gradient(2px 2px at 40px 70px, #fff, rgba(0, 0, 0, 0)),
                    radial-gradient(2px 2px at 60px 110px, #fff, rgba(0, 0, 0, 0)),
                    radial-gradient(2px 2px at 80px 30px, #fff, rgba(0, 0, 0, 0)),
                    radial-gradient(2px 2px at 110px 90px, #fff, rgba(0, 0, 0, 0)),
                    radial-gradient(2px 2px at 140px 50px, #fff, rgba(0, 0, 0, 0)),
                    radial-gradient(2px 2px at 180px 70px, #fff, rgba(0, 0, 0, 0));
  background-repeat: repeat;
  animation: twinkle 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(-50%, -50%) translateY(0); }
  50% { transform: translate(-50%, -50%) translateY(-20px); }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.suggestions {
  padding: 30px;
}

.suggestions h2 {
  margin-bottom: 20px;
  font-size: 22px;
}

.suggestion-links {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.suggestion-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  color: var(--text-color);
  text-decoration: none;
  transition: all var(--transition-speed) ease;
}

.suggestion-link:hover {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
  transform: translateY(-2px);
}

@media (max-width: 992px) {
  .not-found-container {
    flex-direction: column-reverse;
    text-align: center;
  }
  
  .error-actions {
    justify-content: center;
  }
  
  .not-found-illustration {
    margin-bottom: 20px;
  }
}

@media (max-width: 576px) {
  .error-code {
    font-size: 80px;
  }
  
  .error-title {
    font-size: 28px;
  }
  
  .error-description {
    font-size: 16px;
  }
  
  .error-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .not-found-container {
    padding: 20px;
  }
  
  .suggestion-links {
    flex-direction: column;
  }
}
</style>

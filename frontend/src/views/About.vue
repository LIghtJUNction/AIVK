<template>
  <div class="about-view">
    <h1 class="page-title">关于AIVK</h1>
    
    <div class="about-container">
      <div class="about-card card">
        <div class="app-header">
          <div class="app-logo">
            <img src="../../assets/images/aivk-logo.svg" alt="AIVK Logo">
          </div>
          <div class="app-info">
            <h2 class="app-name">AIVK 平台</h2>
            <div class="app-version">版本 1.0.0</div>
            <div class="app-build">构建 #230115-1</div>
          </div>
        </div>
        
        <div class="app-description">
          <p>
            AIVK是一个强大的AI工作流集成平台，旨在为研究人员、开发者和AI爱好者提供一个统一的界面，以访问、管理和利用多种大型语言模型和AI工具。
          </p>
          <p>
            我们的目标是简化AI工作流程，使先进的AI技术更易于访问和应用，同时提供强大的扩展功能，让用户能够根据自己的需求定制平台。
          </p>
        </div>
        
        <div class="tech-stack">
          <h3>核心技术</h3>
          <div class="tech-items">
            <div class="tech-item">
              <i class="fab fa-vuejs"></i>
              <span>Vue 3</span>
            </div>
            <div class="tech-item">
              <i class="fab fa-python"></i>
              <span>Python</span>
            </div>
            <div class="tech-item">
              <i class="fas fa-brain"></i>
              <span>LLM集成</span>
            </div>
            <div class="tech-item">
              <i class="fas fa-database"></i>
              <span>向量数据库</span>
            </div>
            <div class="tech-item">
              <i class="fas fa-plug"></i>
              <span>插件系统</span>
            </div>
            <div class="tech-item">
              <i class="fas fa-lock"></i>
              <span>安全存储</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="features-card card">
        <h2 class="section-title">主要功能</h2>
        
        <div class="features-list">
          <div class="feature-item">
            <div class="feature-icon">
              <i class="fas fa-comments"></i>
            </div>
            <div class="feature-content">
              <h3>多模型接入</h3>
              <p>支持OpenAI、Anthropic、Google等多家LLM服务，一站式管理所有API密钥和设置。</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <i class="fas fa-puzzle-piece"></i>
            </div>
            <div class="feature-content">
              <h3>插件系统</h3>
              <p>丰富的插件生态系统，可轻松扩展平台功能，支持自定义插件开发。</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <i class="fas fa-project-diagram"></i>
            </div>
            <div class="feature-content">
              <h3>工作流自动化</h3>
              <p>通过直观的界面创建复杂的AI工作流，自动化处理日常任务。</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <i class="fas fa-shield-alt"></i>
            </div>
            <div class="feature-content">
              <h3>安全与隐私</h3>
              <p>所有敏感数据均经过加密存储，确保您的API密钥和个人信息安全。</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="team-resources card">
        <div class="team-section">
          <h2 class="section-title">开发团队</h2>
          
          <div class="team-members">
            <div class="team-member">
              <div class="member-avatar">JS</div>
              <div class="member-info">
                <div class="member-name">贾石</div>
                <div class="member-role">项目负责人</div>
              </div>
            </div>
            
            <div class="team-member">
              <div class="member-avatar">ZL</div>
              <div class="member-info">
                <div class="member-name">张亮</div>
                <div class="member-role">前端开发</div>
              </div>
            </div>
            
            <div class="team-member">
              <div class="member-avatar">WM</div>
              <div class="member-info">
                <div class="member-name">王明</div>
                <div class="member-role">后端开发</div>
              </div>
            </div>
            
            <div class="team-member">
              <div class="member-avatar">LY</div>
              <div class="member-info">
                <div class="member-name">李阳</div>
                <div class="member-role">AI工程师</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="resources-section">
          <h2 class="section-title">资源与链接</h2>
          
          <div class="resources-list">
            <a href="#" target="_blank" class="resource-link">
              <i class="fas fa-book"></i>
              <span>文档中心</span>
            </a>
            
            <a href="#" target="_blank" class="resource-link">
              <i class="fab fa-github"></i>
              <span>GitHub仓库</span>
            </a>
            
            <a href="#" target="_blank" class="resource-link">
              <i class="fas fa-graduation-cap"></i>
              <span>教程与示例</span>
            </a>
            
            <a href="#" target="_blank" class="resource-link">
              <i class="fas fa-bug"></i>
              <span>报告问题</span>
            </a>
            
            <a href="#" target="_blank" class="resource-link">
              <i class="fas fa-users"></i>
              <span>社区论坛</span>
            </a>
            
            <a href="#" target="_blank" class="resource-link">
              <i class="fas fa-heart"></i>
              <span>支持项目</span>
            </a>
          </div>
        </div>
      </div>
      
      <div class="license-card card">
        <h2 class="section-title">开源许可</h2>
        
        <div class="license-content">
          <div class="license-header">
            <div class="license-icon">
              <i class="fas fa-file-contract"></i>
            </div>
            <div class="license-info">
              <h3>MIT License</h3>
              <p>Copyright (c) 2023 AIVK Team</p>
            </div>
          </div>
          
          <div class="license-text">
            <p>
              Permission is hereby granted, free of charge, to any person obtaining a copy
              of this software and associated documentation files (the "Software"), to deal
              in the Software without restriction, including without limitation the rights
              to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
              copies of the Software, and to permit persons to whom the Software is
              furnished to do so, subject to the following conditions:
            </p>
            <p>
              The above copyright notice and this permission notice shall be included in all
              copies or substantial portions of the Software.
            </p>
            <p>
              THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
              IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
              FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
              AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
              LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
              OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
              SOFTWARE.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 无需额外逻辑
</script>

<style scoped>
.about-view {
  padding-bottom: 40px;
}

.about-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
}

.about-card {
  padding: 30px;
}

.app-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.app-logo {
  margin-right: 20px;
}

.app-logo img {
  width: 100px;
  height: 100px;
}

.app-name {
  font-size: 28px;
  margin-bottom: 5px;
}

.app-version, .app-build {
  color: var(--text-secondary);
}

.app-description {
  line-height: 1.6;
  margin-bottom: 30px;
}

.app-description p {
  margin-bottom: 15px;
}

.tech-stack h3 {
  margin-bottom: 15px;
}

.tech-items {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.tech-item {
  display: flex;
  align-items: center;
  background-color: var(--bg-tertiary);
  padding: 10px 15px;
  border-radius: var(--border-radius);
  gap: 10px;
}

.tech-item i {
  font-size: 20px;
  color: var(--primary-color);
}

.section-title {
  margin-bottom: 25px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.feature-item {
  display: flex;
  gap: 20px;
}

.feature-icon {
  width: 50px;
  height: 50px;
  min-width: 50px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
}

.feature-content h3 {
  margin-bottom: 10px;
}

.team-resources {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.team-members {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 15px;
}

.member-avatar {
  width: 50px;
  height: 50px;
  background: var(--bg-gradient);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  color: var(--text-color);
}

.member-role {
  font-size: 14px;
  color: var(--text-secondary);
}

.resources-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.resource-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background-color: var(--bg-tertiary);
  border-radius: var(--border-radius);
  color: var(--text-color);
  text-decoration: none;
  transition: all var(--transition-speed) ease;
}

.resource-link:hover {
  background-color: rgba(0, 168, 255, 0.1);
  color: var(--primary-color);
}

.license-card {
  padding: 30px;
}

.license-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.license-icon {
  width: 60px;
  height: 60px;
  background-color: rgba(0, 168, 255, 0.1);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: var(--primary-color);
}

.license-text {
  color: var(--text-secondary);
  white-space: pre-line;
  line-height: 1.6;
}

.license-text p {
  margin-bottom: 15px;
}

@media (max-width: 992px) {
  .team-resources {
    grid-template-columns: 1fr;
  }
  
  .resources-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .team-members {
    grid-template-columns: 1fr;
  }
  
  .feature-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .app-header {
    flex-direction: column;
    text-align: center;
  }
  
  .app-logo {
    margin-right: 0;
    margin-bottom: 15px;
  }
}
</style>

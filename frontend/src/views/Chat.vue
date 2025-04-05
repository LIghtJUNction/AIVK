<template>
  <div class="chat-view">
    <div class="chat-header card">
      <div class="model-selector">
        <label for="model-select">选择模型:</label>
        <select id="model-select" v-model="selectedModel" class="input-field">
          <option v-for="model in availableModels" :key="model.id" :value="model.id">
            {{ model.name }}
          </option>
        </select>
      </div>
      
      <div class="chat-actions">
        <button class="btn" @click="newChat">
          <i class="fas fa-plus"></i> 新对话
        </button>
        <button class="btn" :disabled="messages.length === 0" @click="clearChat">
          <i class="fas fa-trash-alt"></i> 清空对话
        </button>
      </div>
    </div>
    
    <div class="chat-container card" ref="chatContainer">
      <div v-if="messages.length === 0" class="empty-chat">
        <div class="empty-chat-icon">
          <i class="fas fa-comments"></i>
        </div>
        <h2>开始一个新对话</h2>
        <p>选择一个模型并输入您的问题以开始对话。</p>
        
        <div class="suggestions">
          <button 
            v-for="(suggestion, index) in chatSuggestions" 
            :key="index" 
            class="suggestion-btn"
            @click="sendMessage(suggestion)"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
      
      <template v-else>
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          class="message" 
          :class="msg.role"
        >
          <div class="message-avatar">
            <div v-if="msg.role === 'assistant'" class="ai-avatar">AI</div>
            <div v-else class="user-avatar">{{ userInitials }}</div>
          </div>
          
          <div class="message-content">
            <div class="message-header">
              <div class="message-sender">{{ msg.role === 'assistant' ? getModelName(selectedModel) : '您' }}</div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
            
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            
            <div class="message-actions" v-if="msg.role === 'assistant'">
              <button class="action-btn" @click="copyMessage(msg.content)">
                <i class="fas fa-copy"></i>
              </button>
              <button class="action-btn">
                <i class="fas fa-code"></i>
              </button>
              <button class="action-btn">
                <i class="fas fa-thumbs-up"></i>
              </button>
              <button class="action-btn">
                <i class="fas fa-thumbs-down"></i>
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="isLoading" class="loading-message">
          <div class="ai-avatar">AI</div>
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </template>
    </div>
    
    <div class="chat-input-container card">
      <div class="chat-input">
        <textarea 
          ref="inputField"
          v-model="userInput" 
          placeholder="输入消息..." 
          class="input-field"
          @keydown.enter.prevent="onEnterPress"
          @input="adjustHeight"
          rows="1"
        ></textarea>
        
        <div class="input-actions">
          <button class="action-btn" title="上传文件">
            <i class="fas fa-paperclip"></i>
          </button>
          <button 
            class="action-btn send-btn" 
            :disabled="!userInput.trim() || isLoading" 
            @click="sendMessage()"
            :class="{ active: userInput.trim() }"
          >
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
      
      <div class="input-info">
        使用 <kbd>Enter</kbd> 发送消息，使用 <kbd>Shift</kbd> + <kbd>Enter</kbd> 换行
      </div>
    </div>
    
    <!-- 清空对话确认框 -->
    <div class="modal" v-if="showClearModal">
      <div class="modal-backdrop" @click="showClearModal = false"></div>
      <div class="modal-content card">
        <div class="modal-header">
          <h3>确认清空对话</h3>
          <button class="modal-close" @click="showClearModal = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <p>确定要清空当前对话吗？此操作不可撤销。</p>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="showClearModal = false">取消</button>
          <button class="btn btn-danger" @click="confirmClearChat">
            <i class="fas fa-trash-alt"></i> 清空
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useMainStore } from '@/stores/main'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { liteLLMService } from '@/services/llm-service'

// 配置 marked 以使用 hljs 进行语法高亮
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true
})

const authStore = useAuthStore()
const mainStore = useMainStore()

// 状态和引用
const messages = ref([])
const userInput = ref('')
const isLoading = ref(false)
const selectedModel = ref('gpt-4')
const showClearModal = ref(false)
const chatContainer = ref(null)
const inputField = ref(null)

// 用户信息
const userInitials = computed(() => {
  const name = authStore.userFullName
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2)
})

// 可用模型列表
const availableModels = [
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
  { id: 'gpt-4', name: 'GPT-4' },
  { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
  { id: 'claude-3-opus', name: 'Claude 3 Opus' },
  { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet' }
]

// 获取模型显示名称
function getModelName(modelId) {
  const model = availableModels.find(m => m.id === modelId)
  return model ? model.name : modelId
}

// 聊天建议
const chatSuggestions = [
  '介绍一下你自己',
  '解释量子计算的基本原理',
  '帮我写一个Python脚本来分析CSV文件',
  '给我推荐几本科幻小说'
]

// 格式化时间
function formatTime(timestamp) {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 格式化消息（Markdown支持）
function formatMessage(text) {
  return marked(text)
}

// 自动调整输入框高度
function adjustHeight() {
  const textarea = inputField.value
  if (!textarea) return
  
  textarea.style.height = 'auto'
  textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
}

// 处理回车键
function onEnterPress(e) {
  if (!e.shiftKey && !e.ctrlKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 发送消息
async function sendMessage(text) {
  const messageText = text || userInput.value.trim()
  if (!messageText || isLoading.value) return
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: messageText,
    timestamp: new Date().toISOString()
  })
  
  // 清空输入框
  userInput.value = ''
  adjustHeight()
  
  // 滚动到底部
  await scrollToBottom()
  
  // 设置加载状态
  isLoading.value = true
  
  try {
    // 获取配置的设置
    const config = {
      host: 'http://localhost:8000',  // 应从设置中获取
      apiKey: '',                      // 应从设置中获取
      defaultModel: selectedModel.value
    }
    
    // 准备消息列表
    const messageList = messages.value.map(msg => ({
      role: msg.role,
      content: msg.content
    }))
    
    // 调用API
    setTimeout(async () => {
      try {
        // 在真实环境中，这里应该调用API
        // const response = await liteLLMService.chatCompletion(config, messageList)
        
        // 模拟API调用
        const modelResponses = {
          'gpt-3.5-turbo': '我是GPT-3.5 Turbo，一个由OpenAI训练的大型语言模型。我可以帮助回答问题、提供信息或进行对话。',
          'gpt-4': '我是GPT-4，OpenAI最先进的语言模型之一。我理解并生成类人的文本，可以协助完成各种任务。',
          'gpt-4-turbo': '我是GPT-4 Turbo，OpenAI的高性能模型。我拥有更广泛的知识和更快的响应速度。',
          'claude-3-opus': '我是Claude 3 Opus，Anthropic开发的对话AI助手。我旨在提供有用、无害且诚实的对话体验。',
          'claude-3-sonnet': '我是Claude 3 Sonnet，由Anthropic创建。我专注于提供平衡的响应，既有帮助性又有安全性。'
        }
        
        // 根据提问生成不同回复
        let response
        if (messageText.includes('介绍一下你自己')) {
          response = modelResponses[selectedModel.value]
        } else if (messageText.includes('量子计算')) {
          response = `量子计算是利用量子力学现象（如叠加和纠缠）来执行计算的计算机技术。

与传统计算机使用位（0或1）不同，量子计算机使用量子比特（qubit），可以同时存在于多个状态。这种特性使得量子计算机在特定领域（如密码学、优化问题和模拟量子系统）具有潜在的计算优势。

主要概念包括：
- **叠加**：量子比特可以同时处于0和1的状态
- **纠缠**：两个或多个量子比特可以关联，一个的状态会影响另一个
- **量子门**：操作量子比特的基本运算单位

目前量子计算仍处于早期发展阶段，面临着量子相干性、错误校正等挑战。`
        } else if (messageText.includes('Python') || messageText.includes('脚本')) {
          response = `以下是一个简单的Python脚本，用于分析CSV文件：

\`\`\`python
import pandas as pd
import matplotlib.pyplot as plt

def analyze_csv(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path)
    
    # 显示基本信息
    print("数据概览:")
    print(df.info())
    print("\\n统计摘要:")
    print(df.describe())
    
    # 检查缺失值
    print("\\n缺失值统计:")
    print(df.isnull().sum())
    
    # 简单可视化
    if len(df.columns) > 1:
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) >= 2:
            plt.figure(figsize=(10, 6))
            plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]])
            plt.xlabel(numeric_cols[0])
            plt.ylabel(numeric_cols[1])
            plt.title(f'{numeric_cols[0]} vs {numeric_cols[1]}')
            plt.show()
    
    return df

# 使用示例
if __name__ == "__main__":
    file_path = "your_data.csv"
    data = analyze_csv(file_path)
\`\`\`

使用此脚本时，只需将 \`your_data.csv\` 替换为您的CSV文件路径。这个脚本会：
1. 显示数据的基本信息和统计摘要
2. 检查缺失值
3. 如果有数值型列，创建一个简单的散点图

您可以根据需要扩展此脚本，添加更多分析功能。`
        } else if (messageText.includes('科幻小说')) {
          response = `以下是几本经典和现代科幻小说的推荐：

### 经典科幻作品：
1. **《基地》系列 - 艾萨克·阿西莫夫**  
   描绘了一个庞大的银河帝国衰落和重建的史诗。

2. **《三体》三部曲 - 刘慈欣**  
   中国科幻代表作，探讨了宇宙社会学和文明间的生存竞争。

3. **《银河系漫游指南》- 道格拉斯·亚当斯**  
   幽默讽刺的科幻经典，充满机智和想象力。

4. **《神经漫游者》- 威廉·吉布森**  
   赛博朋克开山之作，描绘了虚拟现实和人工智能的未来。

### 现代科幻佳作：
1. **《火星救援》- 安迪·威尔**  
   一个宇航员被困火星后求生的故事，科学细节精确。

2. **《异常》系列 - 彼得·沃茨**  
   探讨意识、进化和后人类主题的硬科幻作品。

3. **《睡美人》- 特德·姜**  
   短篇集，融合科学与哲学，探讨人类与技术的关系。

4. **《光明王国》- N.K.杰米辛**  
   结合科幻与奇幻元素，处理社会和环境主题。

这些作品涵盖了从太空探索到人工智能、从平行宇宙到未来社会等多种科幻主题，希望能找到您感兴趣的！`
        } else {
          response = `作为${getModelName(selectedModel.value)}，我收到了您的消息：

"${messageText}"

这是一个模拟响应，在实际应用中，我会通过LiteLLM代理连接到真实的API服务，为您提供有帮助的回答。您可以在系统设置中配置LiteLLM代理服务器的连接参数和选择默认模型。`
        }
        
        // 添加AI回复
        messages.value.push({
          role: 'assistant',
          content: response,
          timestamp: new Date().toISOString()
        })
        
        // 滚动到底部
        await scrollToBottom()
      } catch (error) {
        console.error('聊天请求失败:', error)
        mainStore.addNotification({
          type: 'error',
          message: '发送消息失败，请检查API设置或网络连接'
        })
      } finally {
        isLoading.value = false
      }
    }, 1500)
  } catch (error) {
    console.error('发送消息失败:', error)
    isLoading.value = false
  }
}

// 新对话
function newChat() {
  if (messages.value.length > 0) {
    showClearModal.value = true
  }
}

// 清空对话
function clearChat() {
  if (messages.value.length > 0) {
    showClearModal.value = true
  }
}

// 确认清空对话
function confirmClearChat() {
  messages.value = []
  showClearModal.value = false
}

// 复制消息
function copyMessage(text) {
  navigator.clipboard.writeText(text).then(() => {
    mainStore.addNotification({
      type: 'success',
      message: '消息已复制到剪贴板'
    })
  }).catch(err => {
    console.error('复制失败:', err)
    mainStore.addNotification({
      type: 'error',
      message: '复制失败，请重试'
    })
  })
}

// 滚动到底部
async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// 监听模型变化
watch(selectedModel, () => {
  if (messages.value.length > 0) {
    mainStore.addNotification({
      type: 'info',
      message: `已切换到${getModelName(selectedModel.value)}`
    })
  }
})

// 页面加载时
onMounted(() => {
  // 自动聚焦输入框
  if (inputField.value) {
    inputField.value.focus()
  }
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  gap: 15px;
  height: calc(100vh - 140px);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-selector select {
  min-width: 180px;
}

.chat-actions {
  display: flex;
  gap: 10px;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  text-align: center;
  padding: 20px;
}

.empty-chat-icon {
  font-size: 48px;
  margin-bottom: 20px;
  color: var(--primary-color);
}

.empty-chat h2 {
  margin-bottom: 10px;
  color: var(--text-color);
}

.empty-chat p {
  margin-bottom: 20px;
  max-width: 500px;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 600px;
}

.suggestion-btn {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 10px 15px;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggestion-btn:hover {
  background-color: rgba(0, 168, 255, 0.1);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.message {
  display: flex;
  gap: 15px;
  padding: 15px;
  border-radius: var(--border-radius);
  animation: fadeIn 0.3s ease;
}

.message.user {
  background-color: var(--bg-tertiary);
}

.message-avatar {
  flex-shrink: 0;
}

.ai-avatar, .user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.ai-avatar {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
}

.user-avatar {
  background-color: var(--primary-color);
  color: white;
}

.message-content {
  flex: 1;
  overflow-x: auto;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.message-sender {
  font-weight: 500;
}

.message-time {
  color: var(--text-secondary);
  font-size: 12px;
}

.message-text {
  line-height: 1.6;
}

.message-text :deep(p) {
  margin-bottom: 10px;
}

.message-text :deep(pre) {
  background-color: var(--bg-tertiary);
  padding: 15px;
  border-radius: var(--border-radius);
  overflow-x: auto;
  margin: 15px 0;
}

.message-text :deep(code) {
  font-family: 'Fira Code', monospace;
  background-color: var(--bg-tertiary);
  padding: 2px 4px;
  border-radius: 4px;
}

.message-text :deep(ul), .message-text :deep(ol) {
  margin-left: 20px;
  margin-bottom: 10px;
}

.message-text :deep(li) {
  margin-bottom: 5px;
}

.message-text :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
}

.message-text :deep(th), .message-text :deep(td) {
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  text-align: left;
}

.message-text :deep(th) {
  background-color: var(--bg-tertiary);
}

.message-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.action-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s ease;
  padding: 5px;
}

.action-btn:hover {
  color: var(--primary-color);
}

.loading-message {
  display: flex;
  gap: 15px;
  padding: 15px;
  animation: fadeIn 0.3s ease;
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 10px 15px;
  background-color: var(--bg-tertiary);
  border-radius: 15px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: var(--text-secondary);
  border-radius: 50%;
  display: inline-block;
  animation: typing 1.3s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.3s;
}

.chat-input-container {
  padding: 15px;
}

.chat-input {
  display: flex;
  position: relative;
}

.input-field {
  flex: 1;
  resize: none;
  max-height: 200px;
  padding: 15px;
  padding-right: 80px;
  border-radius: var(--border-radius);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
}

.input-field:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(0, 168, 255, 0.1);
}

.input-actions {
  position: absolute;
  right: 10px;
  bottom: 10px;
  display: flex;
  gap: 5px;
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  background-color: var(--bg-tertiary);
  cursor: not-allowed;
}

.send-btn.active {
  color: white;
  background-color: var(--primary-color);
  cursor: pointer;
}

.input-info {
  margin-top: 10px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 12px;
}

kbd {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 3px;
  box-shadow: 0 1px 0 rgba(0,0,0,0.2);
  color: var(--text-color);
  display: inline-block;
  font-size: 11px;
  font-family: sans-serif;
  line-height: 1.4;
  margin: 0 0.1em;
  padding: 0.1em 0.6em;
}

/* 动画 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes typing {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.5); }
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
}

.modal-content {
  position: relative;
  width: 400px;
  max-width: 90%;
  animation: modalSlideIn 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 18px;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid var(--border-color);
}

@keyframes modalSlideIn {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chat-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .model-selector {
    width: 100%;
  }
  
  .chat-actions {
    justify-content: space-between;
  }
  
  .message {
    padding: 10px;
  }
}
</style>

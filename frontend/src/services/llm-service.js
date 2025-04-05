import axios from 'axios'

/**
 * LiteLLM代理服务
 * 
 * 提供与LiteLLM代理服务器的交互功能，包括:
 * - 模型调用
 * - 模型列表获取
 * - 代理服务状态检查
 */
export const liteLLMService = {
  /**
   * 初始化LiteLLM客户端
   * @param {Object} config - 配置对象
   * @param {string} config.host - LiteLLM代理服务器地址
   * @param {string} config.apiKey - API密钥（可选）
   * @param {number} config.timeout - 请求超时时间（秒）
   * @returns {Object} - 初始化后的客户端实例
   */
  createClient(config) {
    const client = axios.create({
      baseURL: config.host,
      timeout: (config.timeout || 30) * 1000,
      headers: {
        'Content-Type': 'application/json',
        ...(config.apiKey ? { 'Authorization': `Bearer ${config.apiKey}` } : {})
      }
    })
    
    return client
  },
  
  /**
   * 测试与LiteLLM代理服务器的连接
   * @param {Object} config - 配置对象
   * @returns {Promise<Object>} - 测试结果
   */
  async testConnection(config) {
    try {
      const client = this.createClient(config)
      const response = await client.get('/health')
      
      return {
        success: response.data?.status === 'ok',
        message: '连接成功',
        data: response.data
      }
    } catch (error) {
      console.error('LiteLLM连接测试失败:', error)
      return {
        success: false,
        message: error.response?.data?.message || error.message || '连接失败',
        error
      }
    }
  },
  
  /**
   * 获取可用模型列表
   * @param {Object} config - 配置对象
   * @returns {Promise<Array>} - 模型列表
   */
  async getModels(config) {
    try {
      const client = this.createClient(config)
      const response = await client.get('/models')
      
      return {
        success: true,
        models: response.data.data || []
      }
    } catch (error) {
      console.error('获取模型列表失败:', error)
      return {
        success: false,
        models: [],
        error
      }
    }
  },
  
  /**
   * 发送聊天完成请求
   * @param {Object} config - 配置对象
   * @param {Array} messages - 消息数组
   * @param {Object} options - 其他选项
   * @returns {Promise<Object>} - 聊天完成结果
   */
  async chatCompletion(config, messages, options = {}) {
    try {
      const client = this.createClient(config)
      
      const payload = {
        model: options.model || config.defaultModel || 'gpt-3.5-turbo',
        messages,
        temperature: options.temperature ?? 0.7,
        max_tokens: options.maxTokens,
        stream: options.stream || false
      }
      
      if (options.stream) {
        const response = await client.post('/chat/completions', payload, {
          responseType: 'stream'
        })
        return {
          success: true,
          stream: response.data
        }
      } else {
        const response = await client.post('/chat/completions', payload)
        return {
          success: true,
          data: response.data
        }
      }
    } catch (error) {
      console.error('聊天完成请求失败:', error)
      return {
        success: false,
        error
      }
    }
  }
}

/**
 * OpenAI Agents服务
 * 
 * 封装与OpenAI Agents相关的操作，便于在前端使用
 */
export const agentsService = {
  /**
   * 创建一个新的Agent
   * @param {Object} config - Agent配置
   * @returns {Object} - 创建的Agent信息
   */
  createAgent(config) {
    // 在实际应用中，这里会调用后端API创建Agent
    // 前端只需要发送配置参数
    
    return {
      id: `agent-${Date.now()}`,
      name: config.name || 'New Agent',
      model: config.model || 'gpt-4-turbo',
      systemPrompt: config.systemPrompt,
      tools: config.tools || [],
      created: new Date().toISOString()
    }
  },
  
  /**
   * 执行Agent
   * @param {string} agentId - Agent ID
   * @param {string} input - 用户输入
   * @param {Object} options - 执行选项
   * @returns {Promise<Object>} - 执行结果
   */
  async runAgent(agentId, input, options = {}) {
    try {
      // 在实际应用中，这里会调用后端API执行Agent
      // 模拟执行
      await new Promise(r => setTimeout(r, 1000))
      
      return {
        success: true,
        output: `这是Agent ${agentId}的回复：\n\n您的输入是: "${input}"\n\n这是一个模拟回复，在实际应用中会返回真实的Agent输出。`,
        toolCalls: []
      }
    } catch (error) {
      console.error('执行Agent失败:', error)
      return {
        success: false,
        error
      }
    }
  },
  
  /**
   * 获取Agent历史记录
   * @param {string} agentId - Agent ID
   * @returns {Promise<Array>} - 历史记录列表
   */
  async getAgentHistory(agentId) {
    try {
      // 在实际应用中，这里会调用后端API获取历史记录
      // 模拟历史记录
      return {
        success: true,
        history: [
          {
            id: 'conv-1',
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            summary: '讨论了项目规划'
          },
          {
            id: 'conv-2',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            summary: '回答了编程问题'
          }
        ]
      }
    } catch (error) {
      console.error('获取Agent历史记录失败:', error)
      return {
        success: false,
        history: [],
        error
      }
    }
  }
}

export default {
  liteLLM: liteLLMService,
  agents: agentsService
}

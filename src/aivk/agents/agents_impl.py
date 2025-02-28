import functools
import json
import os
import importlib
from typing import Callable, Dict, Any, Optional, List

import inspect
from . import Base
from ..llms.llms_impl import Llms
from ..tools.tools_impl import Tools

class AgentBase(Base):
    """Agent基类，定义所有agent共同的属性和方法"""
    def __init__(self, llm: Llms, tools: Optional[Tools] = None):
        super().__init__()
        self.llm = llm
        self.tools = tools
        self.memory: List[Dict[str, str]] = []  # 存储对话历史
        
        # 获取Agent名称
        self.name = self._get_agent_name()
        
        # 从元数据加载配置
        self._load_config_from_meta()
        
    def _get_agent_name(self) -> str:
        """获取Agent类的名称（模块名）"""
        module = inspect.getmodule(self.__class__)
        if module:
            module_name = module.__name__.split('.')[-1]
            return module_name
        else:
            # 如果无法确定模块名，返回类名的小写形式
            return self.__class__.__name__.lower()
        
    def _load_config_from_meta(self) -> None:
        """从元数据加载Agent配置，支持模块配置与Meta.toml配置的合并"""
        try:
            # 首先从模块中加载配置（如果有）
            module = inspect.getmodule(self.__class__)
            module_config = {}
            if module and hasattr(module, 'config'):
                module_config = module.config
            
            # 获取Meta.toml中的配置
            meta_config = {}
            try:
                agents_config = self.meta.Metadata.agents()
                if self.name in agents_config:
                    meta_config = agents_config[self.name]
            except Exception as e:
                print(f"Meta.toml中获取配置失败: {str(e)}，使用模块默认配置")
            
            # 合并配置，Meta.toml优先级更高
            config = {**module_config, **meta_config}
            
            # 加载系统提示词
            self.system_prompt = config.get('system_prompt', 
                "你是一个AI助手，可以帮助用户完成各种任务。")
                
            # 加载模型ID
            self.model_id = config.get('model_id', "online_7bE6")
            
            # 加载工具列表
            tool_names = config.get('tools', [])
            if self.tools and tool_names:
                self.tool_specs = self.tools.get_tool_specs(tools=tool_names)
            else:
                self.tool_specs = []
                
        except Exception as e:
            # 如果加载配置失败，使用默认值
            print(f"加载Agent配置失败: {str(e)}，使用默认配置")
            self.system_prompt = "你是一个AI助手，可以帮助用户完成各种任务。"
            self.model_id = "online_7bE6"
            self.tool_specs = []
        
    def add_memory(self, role: str, content: str) -> None:
        """添加对话记录"""
        self.memory.append({"role": role, "content": content})
        
    def clear_memory(self) -> None:
        """清空对话历史"""
        self.memory.clear()
        
    def run(self, prompt: str) -> str:
        """运行agent（子类必须实现）"""
        raise NotImplementedError
    
    def process_tool_calls(self, response: Any) -> Optional[str]:
        """处理响应中的工具调用
        
        Args:
            response: LLM返回的响应对象
            
        Returns:
            Optional[str]: 如果有工具调用则返回工具执行结果，否则返回None
        """
        if not self.tools:
            return None
            
        # 检查是否为结构化对象并包含工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # 处理工具调用
            for tool_call in response.tool_calls:
                try:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # 执行工具并返回结果
                    result = self.tools.execute(tool_name, **tool_args)
                    return str(result)
                except Exception as e:
                    return f"工具调用失败: {str(e)}"
        
        return None
 
class Agents(Base):
    """Agents管理类"""
    def __init__(self):
        super().__init__()
        self.llm = Llms()
        self.tools = Tools()
        self._agents_cache: Dict[str, AgentBase] = {}
        self._load_agents()
    
    def _load_agents(self) -> None:
        """加载所有agent_开头的模块，并同步配置"""
        current_dir = os.path.dirname(__file__)
        
        # 重置模式，确保在批量操作时使用
        self.meta.wait()
        
        # 确保Meta.toml中有agents部分，要使用标准字典结构
        agents_config = {}
        if hasattr(self.meta.Metadata, 'agents'):
            existing_config = self.meta.Metadata.agents()
            if existing_config and isinstance(existing_config, dict):
                agents_config = existing_config
        
        for file in os.listdir(current_dir):
            if file.startswith('agent_') and file.endswith('.py'):
                module_name = file[:-3]
                try:
                    # 导入模块
                    module = importlib.import_module(f'.{module_name}', package='aivk.agents')
                    
                    # 检查并同步模块配置
                    module_config = {}
                    module_desc = ""
                    
                    # 安全获取模块配置和描述
                    if hasattr(module, 'config'):
                        module_config = module.config or {}
                    if hasattr(module, 'desc'):
                        module_desc = module.desc or ""
                    
                    # 同步到配置字典
                    if module_name not in agents_config:
                        agents_config[module_name] = {}
                    
                    # 更新配置，保持已有配置优先
                    for key, value in module_config.items():
                        if key not in agents_config[module_name]:
                            agents_config[module_name][key] = value
                    
                    # 更新描述
                    if 'description' not in agents_config[module_name]:
                        agents_config[module_name]['description'] = module_desc
                    
                    # 实例化Agent并缓存
                    if hasattr(module, 'Agent'):
                        self._agents_cache[module_name] = module.Agent(self.llm, self.tools)
                        
                except Exception as e:
                    print(f"加载agent {module_name} 失败: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
        
        # 在所有处理完成后，一次性更新并保存配置
        self.meta.Metadata.agents(agents_config)
        self.meta.save()
    
    def get_agent(self, name: str) -> AgentBase:
        """获取指定的agent实例"""
        if not name.startswith('agent_'):
            name = f'agent_{name}'
        
        if name not in self._agents_cache:
            raise ValueError(f"Agent {name} 不存在")
        return self._agents_cache[name]
    
    def run(self, agent_name: str, prompt: str) -> str:
        """运行指定的agent"""
        agent = self.get_agent(agent_name)
        return agent.run(prompt)
    
    def list_available_agents(self) -> List[Dict]:
        """列出所有可用的Agent及其描述"""
        result = []
        for name, agent in self._agents_cache.items():
            # 获取Agent描述
            desc = ""
            try:
                module = inspect.getmodule(agent.__class__)
                if module and hasattr(module, 'desc'):
                    desc = module.desc
            except:
                pass
                
            # 从Meta.toml获取描述
            try:
                meta_desc = self.meta.Metadata.agents()[name].get('description', '')
                if (meta_desc):
                    desc = meta_desc
            except:
                pass
                
            # 提取工具名称，修复格式不匹配问题
            tools = []
            if hasattr(agent, 'tool_specs') and agent.tool_specs:
                for tool in agent.tool_specs:
                    if isinstance(tool, dict):
                        # 处理OpenAI格式的工具规格
                        if 'function' in tool and 'name' in tool['function']:
                            tools.append(tool['function']['name'])
                        # 也处理可能的简单格式
                        elif 'name' in tool:
                            tools.append(tool['name'])
            
            result.append({
                "name": name,
                "description": desc,
                "tools": tools
            })
        
        return result

    async def async_run(self, agent_name: str, prompt: str) -> str:
        """异步运行指定的agent"""
        agent = self.get_agent(agent_name)
        # 检查run方法是否是异步的
        if inspect.iscoroutinefunction(agent.run):
            return await agent.run(prompt)
        else:
            # 如果是同步方法，包装为异步
            return agent.run(prompt)
    

   
def agent_run(func):
    """Agent运行装饰器，处理通用逻辑"""
    @functools.wraps(func)
    async def wrapper(self, prompt: str, *args, **kwargs) -> str:
        # 添加用户输入到记忆
        self.add_memory("user", prompt)
        
        # 构造完整的提示词
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            *self.memory
        ]
        
        # 确保工具规格和模型ID正确设置
        if hasattr(self, 'tools') and self.tools and not hasattr(self, 'tool_specs'):
            self.tool_specs = self.tools.get_tool_specs(use_all=True)
        
        if not hasattr(self, 'model_id') or not self.model_id:
            self.model_id = "online_7bE6"  # 默认模型
        
        # 调用实际的处理函数
        response = await func(self, prompt, *args, **kwargs)
        
        # 增强的工具调用检测
        tool_calls = []
        
        # 打印调试信息
        print(f"响应类型: {type(response)}")
        
        # 场景1: 直接有tool_calls属性
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_calls = response.tool_calls
            
        # 场景2: OpenAI标准结构 - response.choices[0].message.tool_calls
        elif hasattr(response, 'choices') and response.choices:
            message = response.choices[0].message
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = message.tool_calls
        
        # 处理找到的工具调用
        if tool_calls:
            print(f"检测到工具调用: {len(tool_calls)} 个")
            for tool_call in tool_calls:
                try:
                    # 处理不同格式的工具调用对象
                    if hasattr(tool_call, 'function'):
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                    elif isinstance(tool_call, dict) and 'function' in tool_call:
                        tool_name = tool_call['function']['name']
                        tool_args = json.loads(tool_call['function']['arguments'])
                    else:
                        print(f"未知的工具调用格式: {type(tool_call)}")
                        continue
                        
                    print(f"调用工具: {tool_name}")
                    print(f"工具参数: {tool_args}")
                    
                    # 执行工具
                    result = self.tools.execute(tool_name, **tool_args)
                    print(f"工具执行结果: {result}")
                    
                    # 添加系统消息记录工具执行结果
                    tool_msg = f"工具 {tool_name} 执行结果: {result}"
                    self.add_memory("system", tool_msg)
                    
                    # 返回工具执行结果
                    return tool_msg
                except Exception as e:
                    error_msg = f"工具调用失败: {str(e)}"
                    print(f"错误: {error_msg}")
                    import traceback
                    print(traceback.format_exc())
                    self.add_memory("system", error_msg)
                    return error_msg
        
        # 如果没有工具调用，添加回复到记忆并返回
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
        else:
            # 尝试其他方式获取内容
            content = getattr(response, 'content', str(response))
            
        self.add_memory("assistant", content)
        return content
        
    return wrapper

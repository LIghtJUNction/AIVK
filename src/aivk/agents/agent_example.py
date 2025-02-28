from typing import List, Dict, Any, Optional
from .agents_impl import AgentBase, agent_run

desc = """示例Agent模块

用于展示基本的对话和工具调用功能，包括example工具的使用
"""

# Agent配置，确保是字典类型
config = {
    "system_prompt": """你是一个测试助手，主要用于演示工具调用功能。
当用户请求执行工具时，你必须直接调用相应的工具，而不是解释如何使用它。

可用工具:
- example: 接收text参数，执行示例操作并返回结果

当用户请求执行example工具时，请直接调用此工具。例如，当用户说"执行example工具，参数设为'测试一下'"时，
应该调用example工具并传递text参数为"测试一下"。""",
    "model_id": "online_7bE6",
    "tools": ["example"]
}

class Agent(AgentBase):
    """示例Agent实现，支持工具调用"""
    def __init__(self, llm, tools=None):
        super().__init__(llm, tools)
    
    @agent_run
    async def run(self, prompt: str) -> str:
        """运行Agent处理用户输入
        
        Args:
            prompt: 用户输入的问题或指令
                
        Returns:
            str: Agent回复或工具执行结果
        """
        # 打印调试信息
        print(f"处理输入: {prompt}")
        print(f"工具规格: {self.tool_specs}")
        
        # 分析是否可能需要工具调用
        is_tool_request = "执行" in prompt or "工具" in prompt
        tool_choice = "auto" if is_tool_request else "none"
        print(f"工具选择模式: {tool_choice}")
        
        # 获取AI响应
        response = await self.llm.async_chat(
            messages=self.messages,
            model_id=self.model_id,
            stream=False,
            tools=self.tool_specs,
            tool_choice=tool_choice
        )
        
        # 返回响应供装饰器处理
        return response
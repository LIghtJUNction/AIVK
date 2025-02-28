from typing import List, Dict
from .agents_impl import AgentBase

class Agent(AgentBase):
    """示例Agent实现"""
    def __init__(self, llm, tools=None):
        super().__init__(llm, tools)

    
    def run(self, prompt: str) -> str:
        """运行agent"""
        
        
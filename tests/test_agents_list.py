import os
import sys
import asyncio
from aivk.agents.agents_impl import Agents

def print_header(title):
    """打印标题"""
    print(f"\n{'='*20} {title} {'='*20}\n")

async def main():
    """测试agents加载和列举"""
    print_header("初始化Agents")
    
    agents = Agents()
    
    print_header("可用的Agents")
    available_agents = agents.list_available_agents()
    print(f"找到 {len(available_agents)} 个Agent:")
    
    for agent_info in available_agents:
        print(f"\n- {agent_info['name']}")
        print(f"  描述: {agent_info['description']}")
        print(f"  使用工具: {', '.join(agent_info['tools']) if agent_info['tools'] else '无'}")
    
    # 测试所有Agent
    print_header("测试所有Agent")
    for agent_info in available_agents:
        agent_name = agent_info['name']
        print(f"\n测试 {agent_name}:")
        try:
            # 普通对话测试
            print("1. 基本对话测试:")
            response = await agents.async_run(agent_name, "你好，请介绍一下自己")
            print(f"回复: {response}")
            
            # 工具调用测试 (如果有工具)
            if agent_info['tools']:
                print("\n2. 工具调用测试:")
                tool_prompt = f"执行example工具，参数设为'通过{agent_name}测试'"
                response = await agents.async_run(agent_name, tool_prompt)
                print(f"回复: {response}")
        except Exception as e:
            print(f"测试失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        print("-" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被中断")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        print(traceback.format_exc())
import os
import sys
import asyncio
import argparse
from aivk.llms.llms_impl import Llms
from aivk.tools.tools_impl import Tools
from aivk.agents.agent_example import Agent as ExampleAgent

def clear_screen():
    """清理屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """打印标题"""
    print(f"\n{'='*20} {title} {'='*20}\n")

async def test_agent_example():
    """测试agent_example能否正常运行"""
    print_header("初始化组件")
    
    # 初始化必要组件
    print("初始化 LLMs...")
    llms = Llms()
    
    print("初始化 Tools...")
    tools = Tools()
    
    print("初始化 ExampleAgent...")
    agent = ExampleAgent(llms, tools)
    
    # 显示加载的配置信息
    print(f"\n加载的配置:")
    print(f"系统提示词: {agent.system_prompt[:50]}...")
    print(f"使用模型ID: {agent.model_id}")
    print(f"工具数量: {len(agent.tool_specs) if hasattr(agent, 'tool_specs') else 0}")
    
    try:
        print_header("开始Agent测试")
        
        # 准备测试提示词
        prompts = [
            "你好，请介绍一下自己",
            "执行example工具，参数设为'测试一下'",
            "计算3+5等于多少"
        ]
        
        # 依次测试每个提示词
        for i, prompt in enumerate(prompts):
            print(f"\n测试 {i+1}: {prompt}")
            print("-" * 40)
            
            # 调用agent
            try:
                response = await agent.run(prompt)
                print("\n回复:")
                print(response)
                
                # 检查是否包含预期内容
                if "example工具" in prompt and "示例工具执行结果" in response:
                    print("\n✓ 成功调用工具")
                else:
                    print("\n✓ 成功获取回复")
                    
            except Exception as e:
                print(f"\n✗ 调用失败: {str(e)}")
                
            input("\n按回车继续...")
            
        print_header("内存中的对话历史")
        for msg in agent.memory:
            role = msg['role']
            content_preview = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            print(f"{role}: {content_preview}")
            
    except Exception as e:
        print(f"\n测试过程发生错误: {str(e)}")
    
    print_header("测试完成")
    return True

def main():
    parser = argparse.ArgumentParser(description="测试Agent功能")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    args = parser.parse_args()

    if args.verbose:
        print("详细模式已启用")
    
    clear_screen()
    print("\n=== Agent测试程序 ===\n")
    
    try:
        # 运行异步测试
        asyncio.run(test_agent_example())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n测试过程发生严重错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
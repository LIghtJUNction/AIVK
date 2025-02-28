import os
import sys
import json
from aivk.tools.tools_impl import Tools

def print_header(title):
    """打印标题"""
    print(f"\n{'='*20} {title} {'='*20}\n")

def print_json(obj, indent=2):
    """格式化打印JSON对象"""
    print(json.dumps(obj, indent=indent, ensure_ascii=False))

def test_tools():
    """测试工具功能"""
    print_header("工具系统测试")
    
    # 创建工具管理器
    tools = Tools()
    
    # 获取所有工具描述
    print_header("所有可用工具")
    all_tools = tools.get_tools(use_all=True)
    print(f"找到 {len(all_tools)} 个工具:")
    
    for tool in all_tools:
        print(f"- {tool['name']}: {tool['description']}")
        if 'parameters' in tool and 'properties' in tool['parameters']:
            print("  参数:")
            for param_name, param_info in tool['parameters']['properties'].items():
                print(f"  - {param_name} ({param_info.get('type', 'any')}): {param_info.get('description', '无描述')}")
    
    # 测试工具描述能力
    print_header("工具描述测试")
    
    # 测试筛选特定工具
    print("1. 获取特定工具描述:")
    example_tool = tools.get_tools(tools=["example"])
    print(f"找到 {len(example_tool)} 个匹配工具:")
    if example_tool:
        print_json(example_tool[0])
    
    # 测试包含/排除过滤
    print("\n2. 测试包含/排除过滤:")
    included_tools = tools.get_tools(include=["example"])
    print(f"包含'example'的工具数量: {len(included_tools)}")
    
    excluded_tools = tools.get_tools(exclude=["example"], use_all=True)
    print(f"排除'example'后的工具数量: {len(excluded_tools)}")
    for tool in excluded_tools:
        print(f"- {tool['name']}")
    
    # 测试OpenAI格式的工具规格
    print("\n3. 测试OpenAI格式工具规格:")
    tool_specs = tools.get_tool_specs(tools=["calculator"])
    print("OpenAI格式的计算器工具规格:")
    print_json(tool_specs)
    
    # 测试执行工具
    print_header("执行工具测试")
    
    # 测试示例工具
    print("测试 example 工具:")
    result = tools.execute('example', text='测试参数')
    print(f"执行结果: {result}")
    
    # 测试计算器工具（如果已加载）
    try:
        print("\n测试 calculator 工具:")
        result = tools.execute('calculator', expression='1 + 2 * 3')
        print(f"执行结果: {result}")
    except ValueError:
        print("calculator 工具未加载或不可用")
    
    print_header("测试完成")
    return True

if __name__ == "__main__":
    test_tools()
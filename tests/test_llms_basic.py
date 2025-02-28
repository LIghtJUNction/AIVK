from aivk.llms.llms_impl import Llms
import os
import sys

def clear_screen():
    """清理屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_divider(title: str = ""):
    """打印带标题的分隔线"""
    print(f"\n{'='*20} {title} {'='*20}")

def test_models_loading():
    """测试模型加载"""
    llms = Llms()
    print_divider("模型加载测试")
    
    # 获取并显示所有模型
    local_models = llms.get_local_models()
    online_models = llms.get_online_models()
    
    print("本地模型:")
    for model in local_models:
        print(f"- {model[0]} ({model[1]})")
    
    print("\n在线模型:")
    for model in online_models:
        print(f"- {model[0]} ({model[1]})")
    
    return len(local_models) > 0 or len(online_models) > 0

def test_chat_basic():
    """测试基本聊天功能"""
    llms = Llms()
    print_divider("基本聊天测试")
    
    # 获取第一个可用的模型ID
    model = None
    for m in llms.models:
        model_id = llms.get_model_id_by_name(m[0])
        if model_id:
            model = (m[0], model_id)
            break
    
    if not model:
        print("未找到可用模型")
        return False
    
    print(f"使用模型: {model[0]} ({model[1]})")
    
    try:
        # 测试普通聊天
        response = llms.chat(
            messages=[{"role": "user", "content": "你好，请做个自我介绍"}],
            model_id=model[1],
            stream=False
        )
        print("\n普通聊天回复:")
        print(response)
        
        # 测试流式聊天
        print("\n流式聊天回复:")
        response = llms.chat(
            messages=[{"role": "user", "content": "请用一句话总结你的特点"}],
            model_id=model[1],
            stream=True
        )
        return True
        
    except Exception as e:
        print(f"聊天测试失败: {str(e)}")
        return False

def test_model_id_mapping():
    """测试模型ID映射功能"""
    llms = Llms()
    print_divider("ID映射测试")
    
    success = True
    for model in llms.models:
        model_name = model[0]
        # 测试ID生成和反查
        model_id = llms.get_model_id_by_name(model_name)
        retrieved_name = llms.get_model_name_by_id(model_id)
        
        print(f"模型名称: {model_name}")
        print(f"模型ID: {model_id}")
        print(f"反查名称: {retrieved_name}")
        print("-" * 40)
        
        if model_name != retrieved_name:
            print(f"错误: ID映射不一致")
            success = False
            
    return success

def main():
    """主测试函数"""
    clear_screen()
    print("\n=== LLMs 基础功能测试 ===\n")
    
    tests = [
        ("模型加载测试", test_models_loading),
        ("ID映射测试", test_model_id_mapping),
        ("聊天功能测试", test_chat_basic)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"测试出错: {str(e)}")
            results.append((name, False))
        input("\n按回车继续下一项测试...")
        clear_screen()
    
    # 显示测试结果汇总
    print("\n=== 测试结果汇总 ===")
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status} - {name}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n测试过程发生错误: {str(e)}")
        sys.exit(1)
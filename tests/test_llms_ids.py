from aivk.llms.llms_impl import Llms
import os
import sys

def clear_screen():
    """清理屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_divider():
    """打印分隔线"""
    print("\n" + "="*50 + "\n")

def main():
    """测试LLMs ID相关函数"""
    llms = Llms()
    
    while True:
        clear_screen()
        print("\n=== LLMs ID测试程序 ===")
        print("1. 显示所有本地模型")
        print("2. 显示所有在线模型")
        print("3. 根据模型名称获取本地模型ID")
        print("4. 根据模型名称获取在线模型ID")
        print("5. 根据ID获取模型名称")
        print("6. 根据名称获取模型ID")
        print("7. 退出")
        
        choice = input("\n请选择操作 (1-7): ")
        
        if choice == '1':
            models = llms.get_local_models()
            print("\n本地模型列表:")
            for model in models:
                print(f"- {model[0]}")
                
        elif choice == '2':
            models = llms.get_online_models()
            print("\n在线模型列表:")
            for model in models:
                print(f"- {model[0]}")
                
        elif choice == '3':
            model_name = input("\n请输入模型名称: ")
            result = llms.get_local_model_id(model_name)
            print("\n查询结果:")
            for name, ids in result.items():
                print(f"模型: {name}")
                print(f"ID列表: {', '.join(ids)}")
                
        elif choice == '4':
            model_name = input("\n请输入模型名称: ")
            result = llms.get_online_model_id(model_name)
            print("\n查询结果:")
            for name, ids in result.items():
                print(f"模型: {name}")
                print(f"ID列表: {', '.join(ids)}")
                
        elif choice == '5':
            model_id = input("\n请输入模型ID: ")
            name = llms.get_model_name_by_id(model_id)
            print(f"\n模型名称: {name if name else '未找到'}")
            
        elif choice == '6':
            model_name = input("\n请输入模型名称: ")
            model_id = llms.get_model_id_by_name(model_name)
            print(f"\n模型ID: {model_id if model_id else '未找到'}")
            
        elif choice == '7':
            print("\n再见！")
            sys.exit(0)
            
        else:
            print("\n无效的选择，请重试")
            
        input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序发生错误: {str(e)}")
        sys.exit(1)
desc = """计算器工具模块

提供基本的算术计算功能
"""

def main(expression: str) -> str:
    """计算数学表达式结果
    
    Args:
        expression: 要计算的数学表达式，支持基本运算符如 +, -, *, /, ** 和括号
        
    Returns:
        str: 计算结果或错误消息
    """
    try:
        # 安全评估表达式
        allowed_names = {"__builtins__": {}}
        allowed_symbols = {'+', '-', '*', '/', '**', '(', ')', '.', ' '}
        
        # 检查表达式是否只包含数字和允许的符号
        if any(c not in allowed_symbols and not c.isdigit() for c in expression):
            return "表达式包含不允许的字符"
        
        result = eval(expression, allowed_names)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"
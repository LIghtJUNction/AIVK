import os
import importlib
import inspect
from typing import Dict, List, Any, Callable, Optional
from . import Base

class Tools(Base):
    """工具管理类，负责工具的注册、查询和执行"""
    
    def __init__(self):
        super().__init__()
        # 工具函数缓存
        self._tool_funcs = {}
        # 工具描述缓存
        self._tools_cache = {}
        
        # 加载所有模块化工具（不再有硬编码）
        self.load_tool_modules()
    
    def register_tool(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None) -> Callable:
        """工具注册函数"""
        # 获取工具名称和函数签名
        func_name = name or func.__name__
        sig = inspect.signature(func)
        doc = description or func.__doc__ or "无描述"
        
        # 构建工具描述
        tool_desc = {
            "name": func_name,
            "description": doc.strip(),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        # 解析文档字符串，提取参数描述
        param_descriptions = self._extract_param_descriptions(func.__doc__ or "")
        
        # 处理参数
        for param_name, param in sig.parameters.items():
            # 获取参数描述，如果无法从文档中提取则使用默认描述
            param_desc = param_descriptions.get(param_name, f"{param_name} 参数")
            
            if param.annotation != inspect.Parameter.empty:
                param_type = self._get_param_type(param.annotation)
                tool_desc["parameters"]["properties"][param_name] = {
                    "type": param_type,
                    "description": param_desc
                }
                
                # 添加必需参数
                if param.default == inspect.Parameter.empty:
                    tool_desc["parameters"]["required"].append(param_name)
        
        # 保存工具
        self._tool_funcs[func_name] = func
        self._tools_cache[func_name] = tool_desc
        
        print(f"注册工具: {func_name}")
        return func

    def _extract_param_descriptions(self, docstring: str) -> Dict[str, str]:
        """从文档字符串中提取参数描述
        
        支持以下格式的文档字符串:
        
        Args:
            param1: 参数1的描述
            param2: 参数2的描述
                可以是多行
            
        或者:
        
        Parameters:
            param1 (type): 参数1的描述
            param2 (type): 参数2的描述
        """
        if not docstring:
            return {}
        
        param_desc = {}
        lines = docstring.split('\n')
        
        # 寻找参数部分
        in_params = False
        current_param = None
        current_desc = []
        
        for line in lines:
            line = line.strip()
            
            # 检测参数部分的开始
            if not in_params and (line == "Args:" or line == "Parameters:"):
                in_params = True
                continue
            
            # 如果在参数部分，处理每一行
            if in_params:
                # 检测是否是参数定义行
                if line and (line[0].isalnum() or line[0] == '_'):
                    # 保存前一个参数的描述
                    if current_param:
                        param_desc[current_param] = ' '.join(current_desc).strip()
                    
                    # 解析新参数
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        # 处理可能的类型标注，如 "param (type):"
                        param_name = parts[0].split('(')[0].strip()
                        current_param = param_name
                        current_desc = [parts[1].strip()]
                    else:
                        # 如果格式不是 "param: desc"，可能是类似 "param"
                        # 这种情况下，视为参数名，描述为空
                        current_param = line
                        current_desc = []
                elif line and line[0].isspace():
                    # 缩进行，继续当前参数的描述
                    if current_param:
                        current_desc.append(line.strip())
                elif not line:
                    # 空行，继续
                    continue
                else:
                    # 非缩进行，参数部分结束
                    in_params = False
        
        # 处理最后一个参数
        if current_param:
            param_desc[current_param] = ' '.join(current_desc).strip()
        
        return param_desc
    
    def _get_param_type(self, annotation) -> str:
        """将Python类型转换为JSON Schema类型"""
        if annotation == str:
            return "string"
        elif annotation == int:
            return "integer"
        elif annotation == float:
            return "number"
        elif annotation == bool:
            return "boolean"
        elif annotation == list or annotation == List:
            return "array"
        elif annotation == dict or annotation == Dict:
            return "object"
        else:
            return "string"  # 默认类型
    
    def load_tool_modules(self):
        """加载tool_开头的模块文件中的工具"""
        try:
            # 获取当前包目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 查找所有tool_开头的Python文件
            for file in os.listdir(current_dir):
                if file.startswith("tool_") and file.endswith(".py"):
                    module_name = file[:-3]  # 去除.py后缀
                    tool_name = module_name[5:]  # 从文件名派生工具名称（去掉tool_前缀）
                    
                    try:
                        # 导入模块
                        module_path = f"aivk.tools.{module_name}"
                        module = importlib.import_module(module_path)
                        
                        # 获取模块描述
                        module_desc = getattr(module, "desc", None)
                        
                        # 检查模块是否有main函数
                        if hasattr(module, "main") and callable(module.main):
                            # 注册为工具，使用文件名作为工具名称
                            self.register_tool(
                                func=module.main,
                                name=tool_name,
                                description=module_desc
                            )
                        else:
                            print(f"警告: 模块 {module_name} 中没有找到main函数")
                            
                    except Exception as e:
                        print(f"加载工具模块 {module_name} 失败: {str(e)}")
        except Exception as e:
            print(f"加载工具模块失败: {str(e)}")

    def execute(self, tool_name: str, **kwargs) -> Any:
        """执行指定工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            Any: 工具执行结果
        """
        # 处理工具名称前缀
        full_name = tool_name if tool_name.startswith('tool_') else f'tool_{tool_name}'
        short_name = tool_name[5:] if tool_name.startswith('tool_') else tool_name
        
        # 尝试以各种形式查找工具
        if full_name in self._tool_funcs:
            return self._tool_funcs[full_name](**kwargs)
        elif short_name in self._tool_funcs:
            return self._tool_funcs[short_name](**kwargs)
        elif tool_name in self._tool_funcs:
            return self._tool_funcs[tool_name](**kwargs)
        else:
            raise ValueError(f"未找到工具: {tool_name}")
    
    def get_tools(self, tools: Optional[List[str]] = None,
                  include: Optional[List[str]] = None,
                  exclude: Optional[List[str]] = None,
                  use_all: bool = False) -> List[Dict]:
        """获取工具描述列表
        
        Args:
            tools: 工具名称列表，如果指定，将只返回这些工具的描述
            include: 要包含的工具名称列表，如果同时指定tools和include，将取并集
            exclude: 要排除的工具名称列表，优先级高于tools和include
            use_all: 是否使用所有工具，当为True时忽略tools和include参数
            
        Returns:
            List[Dict]: 工具描述列表
        """
        result = []
        tool_names_to_include = set()
        
        # 确定要包含哪些工具
        if use_all:
            # 使用所有工具
            tool_names_to_include = set(self._tools_cache.keys())
        else:
            # 处理tools参数
            if tools:
                for name in tools:
                    # 处理工具名前缀
                    full_name = name if name.startswith('tool_') else f'tool_{name}'
                    if full_name in self._tools_cache:
                        tool_names_to_include.add(full_name)
                    elif name in self._tools_cache:
                        tool_names_to_include.add(name)
            
            # 处理include参数
            if include:
                for name in include:
                    full_name = name if name.startswith('tool_') else f'tool_{name}'
                    if full_name in self._tools_cache:
                        tool_names_to_include.add(full_name)
                    elif name in self._tools_cache:
                        tool_names_to_include.add(name)
        
        # 处理exclude参数
        if exclude:
            exclude_names = set()
            for name in exclude:
                full_name = name if name.startswith('tool_') else f'tool_{name}'
                if full_name in self._tools_cache:
                    exclude_names.add(full_name)
                elif name in self._tools_cache:
                    exclude_names.add(name)
            
            # 从包含列表中移除排除的工具
            tool_names_to_include -= exclude_names
        
        # 构建结果列表
        for name in tool_names_to_include:
            if name in self._tools_cache:
                result.append(self._tools_cache[name])
        
        return result
    
    def get_tool_specs(self, tools: Optional[List[str]] = None, 
                       include: Optional[List[str]] = None,
                       exclude: Optional[List[str]] = None, 
                       use_all: bool = False) -> List[Dict]:
        """获取符合OpenAI格式的工具规范
        
        Args:
            tools: 工具名称列表，如果指定，将只返回这些工具的描述
            include: 要包含的工具名称列表
            exclude: 要排除的工具名称列表
            use_all: 是否使用所有工具
            
        Returns:
            List[Dict]: 符合OpenAI API格式的工具规范列表
        """
        tool_descs = self.get_tools(tools, include, exclude, use_all)
        return [{"type": "function", "function": desc} for desc in tool_descs]
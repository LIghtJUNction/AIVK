from __future__ import annotations
import functools
from typing import Callable, Any, Protocol, TypeVar, cast, Type

class FSFunction(Protocol):
    """函数协议"""
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

F = TypeVar('F', bound=FSFunction)
T = TypeVar('T')  # 添加类型变量用于类装饰器

class FastAIVK:
    meta: dict[str, Any] = {}
    
    @classmethod
    def aivk_context(
        cls, 
        id: str = "aivk", 
        create_venv: bool = True, 
        venv_name: str | None = None
    ) -> Callable[[F], F]:
        """
        AIVK 虚拟环境上下文装饰器
        
        :param id: AIVK 项目 ID
        :param create_venv: 是否创建虚拟环境
        :param venv_name: 虚拟环境名称
        :return: 装饰器函数
        """        
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                from .context import AivkContext
                import inspect
                
                ctx = AivkContext.getContext()
                actual_id = id or kwargs.pop('id', 'aivk')
                
                with ctx.env(actual_id, create_venv, venv_name) as fs:
                    # 检查函数签名是否有 fs 参数
                    sig = inspect.signature(func)
                    if 'fs' in sig.parameters:
                        # 如果函数有 fs 参数但调用时没有传递，则自动注入
                        if 'fs' not in kwargs and len(args) < len([p for p in sig.parameters.values() if p.name == 'fs' or p.default == inspect.Parameter.empty]):
                            kwargs['fs'] = fs
                    
                    return func(*args, **kwargs)
            return cast(F, wrapper)
        return decorator

    @classmethod
    def aivk_metadata(cls, target_class: Type[T]) -> Type[T]:
        """
        元数据注册装饰器
        
        :param target_class: 要注册的目标类
        :return: 原始类（不修改）
        """
        # 获取类的所有属性
        class_attrs: dict[str, Any] = {}
        
        # 遍历类的所有属性
        for attr_name in dir(target_class):
            # 跳过私有属性、方法和特殊属性
            if not attr_name.startswith('_') and not callable(getattr(target_class, attr_name)):
                attr_value = getattr(target_class, attr_name)
                class_attrs[attr_name] = attr_value
        
        # 检查是否存在 id 属性
        if 'id' not in class_attrs:
            raise ValueError(f"类 {target_class.__name__} 必须包含 'id' 属性")
        
        # 以 id 为键注册到 meta 字典
        metadata_id: str = str(class_attrs.pop('id'))  # 移除 id，避免重复
        cls.meta[metadata_id] = class_attrs
        
        return target_class
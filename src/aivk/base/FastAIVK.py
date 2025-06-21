from __future__ import annotations
from collections.abc import Callable
import functools
from typing import Any, Protocol, TypeVar, cast
from .loader import AivkLoader
from .aivk import AivkMod
from box import Box

class FSFunction(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

F = TypeVar('F', bound=FSFunction)
T = TypeVar('T')

class FastAIVK:

    @classmethod
    def aivk_context(
        cls, 
        id: str = "aivk", 
        create_venv: bool = True, 
        venv_name: str | None = None
    ) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                from .context import AivkContext
                import inspect
                ctx = AivkContext.getContext()
                actual_id = id or kwargs.pop('id', 'aivk')
                async with ctx.env(actual_id, create_venv, venv_name) as fs:
                    sig = inspect.signature(func)
                    if 'fs' in sig.parameters and 'fs' not in kwargs:
                        kwargs['fs'] = fs
                    return await func(*args, **kwargs)
            return cast(F, wrapper)
        return decorator

    @classmethod
    def aivk_metadata(cls, target_class: type[T]) -> AivkMod:
        # 获取类的所有属性
        class_attrs: dict[str, Any] = {}
        for attr_name in dir(target_class):
            if not attr_name.startswith('_') and not callable(getattr(target_class, attr_name)):
                attr_value = getattr(target_class, attr_name)
                class_attrs[attr_name] = attr_value

        if 'id' not in class_attrs:
            raise ValueError(f"类 {target_class.__name__} 必须包含 'id' 属性")
        metadata_id: str = str(class_attrs.pop('id'))
        AivkLoader.aivk_box.merge_update(Box({metadata_id: class_attrs})) #type: ignore

        return AivkMod(id = metadata_id)


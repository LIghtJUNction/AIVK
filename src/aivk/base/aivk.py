import inspect
from click import Group
from collections.abc import Awaitable, Callable
from typing import Any
import asyncio
import atexit
import click

class AivkMod(Group):
    _onload_registry: dict[str, Callable[..., Awaitable[Any]]] = {}
    _onunload_registry: dict[str, Callable[..., Awaitable[Any]]] = {}
    _send_registry: dict[tuple[str, str], dict[str, Any]] = {}
    _rec_registry: dict[tuple[str, str], tuple[Callable[..., Awaitable[Any]], str]] = {}
    _mod_registry: dict[str, 'AivkMod'] = {}
    _msg_queues: dict[tuple[str, str], asyncio.Queue[dict[str, Any]]] = {}

    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.id = id
        AivkMod._mod_registry[id] = self

    def onLoad(self, func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        """AIVK 模块加载时调用"""
        self._onload_registry[self.id] = func
        return func

    def onUnload(self, func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        """AIVK 模块卸载时调用"""
        self._onunload_registry[self.id] = func
        def _run_onunload() -> None:
            result = func()
            if inspect.iscoroutine(result):
                asyncio.run(result)
            else:
                # 不是协程对象，不能用 asyncio.run
                raise TypeError("onUnload handler 必须返回协程对象")
        atexit.register(_run_onunload)
        return func

    def onSend(
        self,
        channel: str | None = None,
        msg_schema: dict[str, Any] | None = None,
        desc: str | None = None,
    ):
        def decorator(func: Callable[..., Awaitable[Any]]) -> click.Command:
            ch_name = channel or func.__name__
            ch_desc = desc or func.__doc__
            key = (self.id, ch_name)
            # 包一层同步 wrapper，命令行和 send 都能自动 await
            def sync_wrapper(*args: object, **kwargs: object) -> Any:
                coro = func(*args, **kwargs)
                if asyncio.iscoroutine(coro):
                    try:
                        asyncio.get_running_loop()
                        return coro  # pytest/已有loop环境直接返回协程对象
                    except RuntimeError:
                        return asyncio.run(coro)  # CLI下无loop自动run
                return coro
            cmd = click.Command(ch_name, params=getattr(func, "__click_params__", []), callback=sync_wrapper)
            self._send_registry[key] = {
                "func": func,
                "cmd": cmd,
                "schema": msg_schema or {},
                "desc": ch_desc,
            }
            self.add_command(cmd)  # 注册时自动加入命令组
            return cmd
        return decorator

    def onReceive(self,
            channel: str,
            param: str,
            id: str | None = None
        ):
        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            key = ((id or self.id), channel)
            self._rec_registry[key] = (func, param)
            return func
        return decorator

    async def send(self, channel: str, params: dict[str, Any]) -> Any:
        key = (self.id, channel)
        entry = self._send_registry.get(key)
        if not entry:
            raise ValueError(f"No send function registered for {self.id}:{channel}")
        # 检查是否有接收者
        if key not in self._rec_registry:
            # 没有接收者，消息入队
            if key not in self._msg_queues:
                self._msg_queues[key] = asyncio.Queue()
            await self._msg_queues[key].put(params)
            return None
        # 有接收者，正常异步并发处理
        func = entry["func"]
        cmd: click.Command = entry["cmd"]
        args: list[str] = []
        for param in cmd.params:
            if isinstance(param, click.Option):
                pname = param.name
                if pname in params:
                    args.append(f"--{pname}")
                    args.append(str(params[pname]))
        try:
            asyncio.get_running_loop()
            # 并发处理：直接创建任务，不 await，返回 task
            task = asyncio.create_task(func(**params))
            return await task
        except RuntimeError:
            ctx = cmd.make_context(channel, args)
            cmd.invoke(ctx)
            return await func(**params)

    @classmethod
    def getMod(cls, id: str) -> 'AivkMod':
        if id not in cls._mod_registry:
            raise ValueError(f"No AivkMod instance registered for id: {id}")
        return cls._mod_registry[id]

    @classmethod
    async def exec(cls, id: str, action: str, *args: object, **kwargs: object):
        """
        执行指定模块的 onLoad/onUnload 协程，支持任意参数
        :param id: 模块 id
        :param action: "onLoad" 或 "onUnload"
        :param args: 位置参数
        :param kwargs: 关键字参数
        """
        if action == "onLoad":
            func = cls._onload_registry.get(id)
        elif action == "onUnload":
            func = cls._onunload_registry.get(id)
        else:
            raise ValueError("action 只能为 'onLoad' 或 'onUnload'")
        if func:
            await func(*args, **kwargs)
        else:
            raise ValueError(f"{action} 未注册: {id}")
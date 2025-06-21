import pytest
import click
from aivk.base.aivk import AivkMod
from typing import Dict, Any

@pytest.mark.asyncio
async def test_send_and_receive():
    mod = AivkMod("mod1")
    received: Dict[str, Any] = {}

    # 注册发送通道，参数校验和注入由 click.option 负责
    @mod.onSend("foo")
    @click.option("--bar", type=int)
    @click.option("--baz", type=str)
    async def send_foo(bar: int, baz: str) -> dict[str, Any]:
        bar = int(bar)  # 强制类型转换，类型错误时抛 ValueError
        return {"bar": bar, "baz": baz}

    # 注册接收通道
    @mod.onReceive("mod1", "foo", "msg")
    async def handle_foo(msg: dict[str, Any]) -> str:
        received.update(msg)
        return "ok"

    # 注册接收通道（省略 id，默认 self.id）
    @mod.onReceive("foo", "msg")
    async def handle_foo2(msg: dict[str, Any]) -> str:
        received.update(msg)
        return "ok2"

    # 发送消息
    msg = await mod.send("foo", {"bar": 123, "baz": "hello"})
    assert msg == {"bar": 123, "baz": "hello"}

    # 模拟分发到接收方
    func, _ = mod.get_receive_handler("foo")
    result = await func(msg)
    assert result in ("ok", "ok2")
    assert received == {"bar": 123, "baz": "hello"}

    # 发送消息到新 handler
    msg2 = await mod.send("foo", {"bar": 456, "baz": "world"})
    func2, _ = mod.get_receive_handler("foo")
    result2 = await func2(msg2)
    assert result2 in ("ok", "ok2")
    assert received == {"bar": 456, "baz": "world"}

    # 校验参数校验机制
    with pytest.raises((click.BadParameter, TypeError, ValueError)):
        await mod.send("foo", {"bar": "notint", "baz": "hello"})

    # 校验未注册通道
    with pytest.raises(ValueError):
        await mod.send("not_exist", {"bar": 1})

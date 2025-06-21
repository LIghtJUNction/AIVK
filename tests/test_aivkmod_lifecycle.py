import pytest
from aivk.base.aivk import AivkMod
import click

@pytest.mark.asyncio
async def test_onload_onunload_registration_and_call(monkeypatch):
    logs = []
    mod = AivkMod("testmod")

    @mod.onLoad
    async def onload(ctx=None):
        msg = f"onload called ctx={getattr(ctx, 'obj', None)}"
        print(msg)
        logs.append(msg)
        return "loaded"

    @mod.onUnload
    async def onunload(ctx=None):
        msg = f"onunload called ctx={getattr(ctx, 'obj', None)}"
        print(msg)
        logs.append(msg)
        return "unloaded"

    # 检查注册表
    print("onload func:", AivkMod.get_onload("testmod"))
    print("onunload func:", AivkMod.get_onunload("testmod"))
    assert AivkMod.get_onload("testmod") is onload
    assert AivkMod.get_onunload("testmod") is onunload

    # 模拟 click.Context 传递
    ctx = click.Context(mod)
    ctx.obj = {"user": "tester"}
    result_load = await AivkMod.get_onload("testmod")(ctx)
    print("result_load:", result_load)
    result_unload = await AivkMod.get_onunload("testmod")(ctx)
    print("result_unload:", result_unload)
    print("logs:", logs)
    assert result_load == "loaded"
    assert result_unload == "unloaded"
    assert logs == [
        "onload called ctx={'user': 'tester'}",
        "onunload called ctx={'user': 'tester'}"
    ]

@pytest.mark.asyncio
async def test_unregistered_hooks_return_none():
    assert AivkMod.get_onload("not_exist") is None
    assert AivkMod.get_onunload("not_exist") is None

@pytest.mark.asyncio
async def test_multiple_mods_isolation():
    mod1 = AivkMod("mod1")
    mod2 = AivkMod("mod2")
    called = []
    @mod1.onLoad
    async def load1(ctx=None):
        called.append("mod1")
    @mod2.onLoad
    async def load2(ctx=None):
        called.append("mod2")
    await AivkMod.get_onload("mod1")()
    await AivkMod.get_onload("mod2")()
    assert called == ["mod1", "mod2"]

@pytest.mark.asyncio
async def test_hook_exception_propagation():
    mod = AivkMod("errmod")
    @mod.onLoad
    async def bad(ctx=None):
        raise RuntimeError("fail hook")
    with pytest.raises(RuntimeError, match="fail hook"):
        await AivkMod.get_onload("errmod")()

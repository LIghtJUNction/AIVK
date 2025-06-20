import sys
import types
import pytest
from unittest import mock
from aivk.base.context import AivkContext

@pytest.fixture(autouse=True)
def reset_context():
    # 确保每个测试用例前后都重置单例
    if hasattr(AivkContext, "_instance"):
        delattr(AivkContext, "_instance")
    yield
    if hasattr(AivkContext, "_instance"):
        delattr(AivkContext, "_instance")

@pytest.fixture
def context():
    return AivkContext.getContext()

@pytest.fixture
def fake_packages():
    # 构造虚拟包列表
    return [
        {"name": "aivk_foo", "version": "1.0.0"},
        {"name": "aivk-bar", "version": "2.0.0"},
        {"name": "aivkcore", "version": "3.0.0"},
        {"name": "otherpkg", "version": "0.1.0"},
    ]

def test_get_aivk_modules_basic(context, fake_packages):
    modules = context.get_aivk_modules(fake_packages)
    names = [m["name"] for m in modules]
    assert "aivk_foo" in names
    assert "aivk-bar" in names
    assert "aivkcore" not in names
    assert "otherpkg" not in names

def test_get_aivk_modules_show_all(context, fake_packages):
    modules = context.get_aivk_modules(fake_packages, show_all_packages=True)
    names = [m["name"] for m in modules]
    assert "aivk_foo" in names
    assert "aivk-bar" in names
    # show_all_packages 只会 log 其他 aivk*，不会加入 modules
    assert "aivkcore" not in names
    assert "otherpkg" not in names

def test_load_single_module_success(context):
    # 构造一个可导入的虚拟模块
    mod = types.ModuleType("aivk_foo")
    mod.onLoad = lambda: setattr(mod, "loaded", True)
    sys.modules["aivk_foo"] = mod
    assert context.load_single_module("aivk-foo", in_env=True)
    assert getattr(mod, "loaded", False)
    del sys.modules["aivk_foo"]

def test_load_single_module_importerror(context):
    if "aivk_bar" in sys.modules:
        del sys.modules["aivk_bar"]
    assert not context.load_single_module("aivk-bar", in_env=True)

def test_unload_single_module_success(context):
    mod = types.ModuleType("aivk_foo")
    mod.onUnload = lambda: setattr(mod, "unloaded", True)
    sys.modules["aivk_foo"] = mod
    assert context.unload_single_module("aivk-foo", in_env=True)
    assert getattr(mod, "unloaded", False)
    assert "aivk_foo" not in sys.modules

def test_unload_single_module_not_loaded(context):
    if "aivk_bar" in sys.modules:
        del sys.modules["aivk_bar"]
    assert context.unload_single_module("aivk-bar", in_env=True)

def test_unload_aivk_modules_idempotent(context, fake_packages):
    # 模拟 list_packages 和 get_aivk_modules
    context.list_packages = lambda env_id=None: fake_packages
    context.get_aivk_modules = lambda pkgs, show_all_packages=False: [
        {"name": "aivk_foo"}, {"name": "aivk-bar"}
    ]
    context.unload_single_module = mock.Mock(return_value=True)
    context._unloaded = False
    context.unload_aivk_modules(verbose_level=1)
    assert context._unloaded
    # 再次调用不会重复卸载
    context.unload_single_module.reset_mock()
    context.unload_aivk_modules(verbose_level=1)
    context.unload_single_module.assert_not_called()

def test_atexit_hook(context, fake_packages):
    # 验证 atexit 钩子不会递归
    context.list_packages = lambda env_id=None: fake_packages
    context.get_aivk_modules = lambda pkgs, show_all_packages=False: [
        {"name": "aivk_foo"}
    ]
    context.unload_single_module = mock.Mock(return_value=True)
    context._unloaded = False
    # allow_atexit=True 时每次都应执行一次
    context.unload_aivk_modules(verbose_level=1, allow_atexit=True)
    assert context._unloaded
    context.unload_single_module.assert_called_once_with("aivk_foo", "aivk", 1, in_env=True)
    # 再次调用会再卸载一次
    context.unload_single_module.reset_mock()
    context._unloaded = False  # 模拟 atexit 场景
    context.unload_aivk_modules(verbose_level=1, allow_atexit=True)
    context.unload_single_module.assert_called_once_with("aivk_foo", "aivk", 1, in_env=True)

def test_get_package_details_default(context):
    # 没有虚拟环境时返回默认
    context.active_venvs.clear()
    author, desc = context._get_package_details("aivk_foo")
    assert author == "未知"
    assert desc == "无描述"

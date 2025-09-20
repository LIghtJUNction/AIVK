"""
测试 AivkConfig 配置类
不使用 mock，直接调用实际的类进行测试
"""
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Optional
import json
import toml

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from sqlmodel import SQLModel, Field, select

from aivk.config.models import AivkConfig
from aivk.config.v1 import AivkConfigV1
from aivk.base import AivkFS

from logging import getLogger
logger = getLogger("test_aivk_config")


# 定义测试用的SQLModel模型
class TestTable(SQLModel, table=True):
    """测试表模型"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    value: int

class TestAivkConfig:
    """AivkConfig 配置类测试"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """设置测试环境和清理"""
        # 创建临时目录作为测试根目录
        self.temp_root = Path(tempfile.mkdtemp())
        self.original_root = AivkFS.root
        
        # 替换 AivkFS.root 为临时目录
        AivkFS.root = self.temp_root
        
        # 清空缓存
        AivkFS.fs.clear()
        AivkConfig.config_dict.clear()
        
        yield
        
        # 清理测试环境
        AivkFS.root = self.original_root
        AivkFS.fs.clear()
        AivkConfig.config_dict.clear()
        
        # 删除临时目录 - 处理Windows文件锁定问题
        if self.temp_root.exists():
            import time
            import gc
            import sys
            
            # 强制垃圾回收
            gc.collect()
            
            # 等待更长时间让文件句柄释放
            time.sleep(0.2)
            
            # 尝试多次删除
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    shutil.rmtree(self.temp_root)
                    break  # 成功删除，退出循环
                except (PermissionError, OSError) as e:
                    if attempt < max_attempts - 1:  # 不是最后一次尝试
                        gc.collect()
                        time.sleep(0.5)  # 等待更长时间
                    else:
                        # 最后一次尝试失败，只记录调试信息而不是警告
                        import warnings
                        if sys.platform.startswith('win'):
                            # Windows 下这是常见问题，降低警告级别
                            import logging
                            logging.getLogger("test_aivk_config").debug(
                                f"Windows下无法删除临时目录（正常现象）: {self.temp_root}"
                            )
                        else:
                            warnings.warn(f"无法删除临时目录: {self.temp_root}")

    def test_validate_tree_valid_cases(self):
        """测试配置树格式验证 - 有效情况"""
        valid_trees = [
            "aivk.meta",
            "load.config",
            "test.myfile",
            "app.settings.config",
            "service.db.connection"
        ]
        
        for tree in valid_trees:
            assert AivkConfig._validate_tree(tree), f"应该接受有效的树格式: {tree}"

    def test_validate_tree_invalid_cases(self):
        """测试配置树格式验证 - 无效情况"""
        invalid_trees = [
            "aivk",  # 没有点分隔
            "aivk_test.meta",  # id部分包含下划线
            ".meta",  # id部分为空
            "aivk.",  # 文件名部分为空
            "aivk.123invalid",  # 文件名不是有效标识符
            "aivk.my-file",  # 文件名包含连字符
            "",  # 空字符串
            "aivk..meta"  # 连续的点
        ]
        
        for tree in invalid_trees:
            assert not AivkConfig._validate_tree(tree), f"应该拒绝无效的树格式: {tree}"

    @pytest.mark.asyncio
    async def test_get_config_json_format(self):
        """测试获取 JSON 格式配置"""
        tree = "testapp.settings"
        default_config = {
            "app_name": "TestApp",
            "version": "1.0.0",
            "debug": True
        }
        
        # 第一次获取配置（应该创建新文件）
        config = await AivkConfig.getConfig(
            tree=tree,
            default=default_config,
            format="json",
            base=AivkConfigV1
        )
        
        assert isinstance(config, AivkConfigV1)
        config_data = config.model_dump()
        
        # 验证默认配置已加载
        assert config_data['app_name'] == "TestApp"
        assert config_data['version'] == "1.0.0"
        assert config_data['debug'] is True
        
        # 验证文件是否创建
        fs = AivkFS.getFS("testapp")
        config_path = fs.etc / "settings.json"
        assert config_path.exists()
        
        # 验证文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
            
        assert file_content['app_name'] == "TestApp"
        assert file_content['version'] == "1.0.0"
        assert file_content['debug'] is True

    @pytest.mark.asyncio
    async def test_get_config_toml_format(self):
        """测试获取 TOML 格式配置"""
        tree = "webapp.database"
        default_config = {
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
            "username": "testuser"
        }
        
        config = await AivkConfig.getConfig(
            tree=tree,
            default=default_config,
            format="toml",
            base=AivkConfigV1
        )
        
        assert isinstance(config, AivkConfigV1)
        
        # 验证文件创建
        fs = AivkFS.getFS("webapp")
        config_path = fs.etc / "database.toml"
        assert config_path.exists()
        
        # 验证文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            file_content = toml.load(f)
            
        assert file_content['host'] == "localhost"
        assert file_content['port'] == 5432
        assert file_content['database'] == "testdb"

    @pytest.mark.asyncio
    async def test_get_config_sqlite_format(self):
        """测试获取 SQLite 格式配置"""
        tree = "dbapp.main"
        
        engine = await AivkConfig.getConfig(
            tree=tree,
            format="sqlite"
        )
        
        assert isinstance(engine, AsyncEngine)
        
        # 验证数据库文件创建 - SQLite数据库在AivkFS.root下
        db_path = AivkFS.root / "aivk.db"
        # SQLite引擎可能是延迟创建文件的，先执行一个查询来确保文件创建
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            assert row[0] == 1
        
        # 现在验证数据库文件是否存在
        assert db_path.exists()

    @pytest.mark.asyncio
    async def test_config_caching(self):
        """测试配置缓存机制"""
        tree = "cachetest.config"
        default_config = {"cached": True}
        
        # 第一次获取
        config1 = await AivkConfig.getConfig(
            tree=tree,
            default=default_config,
            format="json"
        )
        
        # 第二次获取相同配置
        config2 = await AivkConfig.getConfig(
            tree=tree,
            default=default_config,
            format="json"
        )
        
        # 应该返回缓存的相同实例
        assert config1 is config2
        
        # 测试 SQLite 缓存
        engine1 = await AivkConfig.getConfig(
            tree="dbtest.cache",
            format="sqlite"
        )
        
        engine2 = await AivkConfig.getConfig(
            tree="dbtest.cache",
            format="sqlite"
        )
        
        assert engine1 is engine2

    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """测试并发访问配置"""
        tree = "concurrent.test"
        default_config = {"concurrent": True, "counter": 0}
        
        async def get_config():
            return await AivkConfig.getConfig(
                tree=tree,
                default=default_config.copy(),
                format="json"
            )
        
        # 并发获取配置
        tasks = [get_config() for _ in range(10)]
        configs = await asyncio.gather(*tasks)
        
        # 所有配置应该是同一个实例（由于缓存）
        first_config = configs[0]
        for config in configs[1:]:
            assert config is first_config

    @pytest.mark.asyncio
    async def test_different_formats_different_caches(self):
        """测试不同格式使用不同缓存"""
        tree = "multiformat.config"
        default_config = {"format_test": True}
        
        # 获取 JSON 格式
        json_config = await AivkConfig.getConfig(
            tree=tree,
            default=default_config,
            format="json"
        )
        
        # 获取 TOML 格式  
        toml_config = await AivkConfig.getConfig(
            tree=tree,
            default=default_config,
            format="toml"
        )
        
        # 获取 SQLite 格式
        sqlite_engine = await AivkConfig.getConfig(
            tree=tree,
            format="sqlite"
        )
        
        # 应该是不同的实例
        assert json_config is not toml_config
        assert json_config is not sqlite_engine
        assert toml_config is not sqlite_engine
        
        # 类型检查
        assert isinstance(json_config, AivkConfigV1)
        assert isinstance(toml_config, AivkConfigV1)
        assert isinstance(sqlite_engine, AsyncEngine)

    @pytest.mark.asyncio
    async def test_invalid_tree_format(self):
        """测试无效的配置树格式"""
        invalid_trees = ["invalid", "test_app.config", ""]
        
        for tree in invalid_trees:
            with pytest.raises(ValueError, match="Invalid tree format"):
                await AivkConfig.getConfig(tree=tree)

    @pytest.mark.asyncio
    async def test_unsupported_format(self):
        """测试不支持的配置格式"""
        with pytest.raises(ValueError, match="Unsupported format"):
            await AivkConfig.getConfig(
                tree="test.config",
                format="yaml"  # 不支持的格式
            )

    @pytest.mark.asyncio
    async def test_config_persistence(self):
        """测试配置持久化"""
        tree = "persist.config"
        default_config = {
            "name": "PersistTest",
            "value": 42,
            "enabled": False
        }
        
        # 创建配置
        config = await AivkConfig.getConfig(
            tree=tree,
            default=default_config,
            format="json"
        )
        
        # 验证配置文件存在并包含正确内容
        fs = AivkFS.getFS("persist")
        config_path = fs.etc / "config.json"
        
        assert config_path.exists()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data['name'] == "PersistTest"
        assert saved_data['value'] == 42
        assert saved_data['enabled'] is False

    @pytest.mark.asyncio
    async def test_filesystem_structure(self):
        """测试文件系统结构正确性"""
        tree = "fstest.subdir.config"
        default_config = {"fs_test": True}
        
        config = await AivkConfig.getConfig(
            tree=tree,
            default=default_config,
            format="json"
        )
        
        # 验证目录结构
        fs = AivkFS.getFS("fstest")
        expected_path = fs.etc / "subdir" / "config.json"
        
        assert expected_path.exists()
        assert expected_path.parent.name == "subdir"
        assert expected_path.parent.parent.name == "etc"

    @pytest.mark.asyncio  
    async def test_sqlite_engine_functionality(self):
        """测试 SQLite 引擎功能"""
        tree = "sqltest.engine"
        
        engine = await AivkConfig.getConfig(
            tree=tree,
            format="sqlite"
        )
        
        # 使用 SQLModel 创建表
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        # 使用 SQLModel 插入测试数据
        from sqlalchemy.ext.asyncio import AsyncSession
        
        async with AsyncSession(engine) as session:
            test_record = TestTable(name="test", value=123)
            session.add(test_record)
            await session.commit()
            
            # 查询测试数据
            stmt = select(TestTable).where(TestTable.name == "test")
            result = await session.execute(stmt)
            retrieved_record = result.scalar_one_or_none()
            
            assert retrieved_record is not None
            assert retrieved_record.name == "test"
            assert retrieved_record.value == 123

    @pytest.mark.asyncio
    async def test_default_values_handling(self):
        """测试默认值处理"""
        tree = "default.test"
        
        # 测试空默认值
        config1 = await AivkConfig.getConfig(tree=tree, default={})
        
        # 验证自动添加的默认值（由于传入的default为空，会有id和created_at）
        config_data = config1.model_dump()
        assert 'id' in config_data
        assert 'created_at' in config_data
        
        # 测试自定义默认值
        custom_default = {"custom": "value", "number": 999}
        config2 = await AivkConfig.getConfig(
            tree="default.custom",
            default=custom_default
        )
        
        config2_data = config2.model_dump()
        assert config2_data['custom'] == "value"
        assert config2_data['number'] == 999


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

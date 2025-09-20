"""
演示为什么需要重写AivkConfigV1的load方法
"""
import asyncio
import tempfile
from pathlib import Path
import json

from aivk.config.v1 import AivkConfigV1
from aivk.base import AivkFS

async def demo_original_problem():
    """演示原始AivkConfigV1的问题"""
    
    # 创建临时目录
    temp_root = Path(tempfile.mkdtemp())
    original_root = AivkFS.root
    AivkFS.root = temp_root
    
    try:
        # 创建测试配置文件
        config_path = temp_root / "test_config.json"
        test_data = {
            "app_name": "TestApp",
            "version": "1.0.0", 
            "debug": True
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_data, f)
        
        print("原始配置文件内容:")
        print(json.dumps(test_data, indent=2))
        
        # 使用原始AivkConfigV1加载
        original_config = await AivkConfigV1.load(config_path, test_data)
        
        print("\n使用原始AivkConfigV1.load()的结果:")
        print("配置对象内容:", original_config.model_dump())
        
        # 尝试访问我们期望的字段
        try:
            print(f"app_name: {original_config.app_name}")
        except AttributeError:
            print("❌ 无法访问 app_name 字段!")
            
        try:
            print(f"version: {original_config.version}")
        except AttributeError:
            print("❌ 无法访问 version 字段!")
            
        # 但是可以访问DEFAULT字段
        print(f"DEFAULT: {original_config.DEFAULT}")
        
    finally:
        AivkFS.root = original_root
        import shutil
        shutil.rmtree(temp_root)

if __name__ == "__main__":
    asyncio.run(demo_original_problem())

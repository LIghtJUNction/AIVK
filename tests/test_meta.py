import unittest
import os
from pathlib import Path
from aivk.meta.meta_impl import MetaLoader

class TestMetaOperations(unittest.TestCase):
    def setUp(self):
        """每个测试前运行"""
        self.test_file = Path(__file__).parent / "test_meta.toml"
        
        # 创建初始测,数据
        initial_data = """[Metadata]
__name__ = "test"

[Metadata.test]
models = [
    ["model1", "url1", "key1", "local", "None"],
    ["model2", "url2", "key2", "online", "None"]
]"""
        
        # 写入测试文件
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(initial_data)
            
        # 初始化 MetaLoader
        self.meta = MetaLoader(self.test_file)

    def tearDown(self):
        """每个测试后运行"""
        if self.test_file.exists():
            os.remove(self.test_file)

    def test_basic_perations(self):
        """测试基本操作"""
        # 读取测试
        models = self.meta.Metadata.test.models()
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0][0], "model1")

        # 添加测试
        new_model = ["model3", "url3", "key3", "local", "None"]
        self.meta.Metadata.test.models.append(new_model)
        models = self.meta.Metadata.test.models()
        self.assertEqual(len(models), 3)
        self.assertEqual(models[-1], new_model)

    def test_wait_operations(self):
        """测试延迟保存"""
        print("\n=== 延迟保存测试 ===")
        meta1 = MetaLoader(self.test_file)
        
        print("1. 初始值:", meta1.Metadata.test.models())
        
        models_node = meta1.Metadata.test.models
        models_node.append(["model4", "url4", "key4", "local", "None"]).wait()
        
        print("2. 添加后(原实例):", models_node())
        print("3. 原始值:", models_node._original_value)
        print("4. 修改值:", models_node._modified_value)
        
        meta2 = MetaLoader(self.test_file)
        print("5. 新实例读取:", meta2.Metadata.test.models())
        
        models_node.save()
        print("6. 保存后:", meta2.Metadata.test.models())

    def test_error_handling(self):
        """测试错误处理"""
        # 测试访问不存在的路径
        with self.assertRaises(KeyError):
            _ = self.meta.Metadata.nonexist.value
        
        # 测试列表操作
        initial_length = len(self.meta.Metadata.test.models())
        self.meta.Metadata.test.models.remove(0)
        current_length = len(self.meta.Metadata.test.models())
        self.assertEqual(current_length, initial_length - 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
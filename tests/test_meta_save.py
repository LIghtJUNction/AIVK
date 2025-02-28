from aivk.agents.agents_impl import Agents

def test_meta_save():
    """测试Meta.toml保存功能"""
    # 初始化Agents管理器
    agents = Agents()
    
    # 手动添加一个测试配置
    if not hasattr(agents.meta.Metadata, 'agents'):
        agents.meta.Metadata.agents({})
    
    # 示例配置
    test_config = {
        "description": "测试添加",
        "system_prompt": "这是一个测试"
    }
    
    # 更新配置 - 尝试函数式调用
    agents_config = agents.meta.Metadata.agents() or {}
    agents_config["test_agent"] = test_config
    agents.meta.Metadata.agents(agents_config)
    
    # 显式保存
    print("尝试保存配置...")
    agents.meta.save()
    print("保存完成")
    
if __name__ == "__main__":
    test_meta_save()
# AIVK 开发指南 | Development Guide | 開発ガイド

## 开发环境 | Development Environment | 開発環境

### 推荐工具 | Recommended Tools | 推奨ツール

- Python 3.8+ | Python 3.8以上 | Python 3.8以上
- Visual Studio Code | VS Code
- Git | Git | Git
- Docker (可选) | Docker (optional) | Docker (オプション)

### 开发依赖 | Development Dependencies | 開発依存関係

```toml
# pyproject.toml
[tool.poetry.dev-dependencies]
pytest = "^7.0.0"             # 测试框架 | Test framework | テストフレームワーク
black = "^22.0.0"            # 代码格式化 | Code formatter | コードフォーマッタ
mypy = "^0.960"              # 类型检查 | Type checker | 型チェッカー
pylint = "^2.14.0"           # 代码分析 | Code analyzer | コード分析
sphinx = "^5.0.0"            # 文档生成 | Doc generator | ドキュメント生成
```

## 模块开发 | Module Development | モジュール開発

### 目录结构 | Directory Structure | ディレクトリ構造

```
aivk-mymodule/             # 模块包名 (例如 aivk-fs)
├── pyproject.toml           # 项目配置 | Project config | プロジェクト設定
├── README.md               # 文档 | Documentation | ドキュメント
├── tests/                 # 测试 | Tests | テスト
└── src/
    └── aivk_mymodule/     # Python 包名 (例如 aivk_fs)
        ├── __init__.py
        ├── onCli/         # (可选) 提供 CLI 子命令 | (Optional) Provides CLI subcommand | (オプション) CLIサブコマンドを提供
        │   └── __main__.py # 定义 click.Group/Command
        ├── onLoad/        # (可选) 加载处理 | (Optional) Load handling | (オプション) ロード処理
        │   └── __main__.py # 定义 async def load(...)
        ├── onUnload/      # (可选) 卸载处理 | (Optional) Unload handling | (オプション) アンロード処理
        │   └── __main__.py # 定义 async def unload(...)
        ├── onInstall/     # (可选) 安装处理 | (Optional) Install handling | (オプション) インストール処理
        │   └── __main__.py # 定义 async def install(...)
        ├── onUninstall/   # (可选) 卸载处理 | (Optional) Uninstall handling | (オプション) アンインストール処理
        │   └── __main__.py # 定义 async def uninstall(...)
        ├── onUpdate/      # (可选) 更新处理 | (Optional) Update handling | (オプション) 更新処理
        │   └── __main__.py # 定义 async def update(...)
        └── core/          # (可选) 核心代码 | (Optional) Core code | (オプション) コアコード
```

### 命令行集成 | Command Line Integration | コマンドライン統合

AIVK 使用 `click` 库构建命令行界面。核心 CLI (`aivk`) 可以动态加载其他模块提供的子命令。

- **动态加载**: `AivkCLI.AivkGroup` 类在 `get_command` 方法中尝试加载未知的命令。它会调用 `AivkCLI.on(action="cli", id=cmd_name)`。
- **模块实现**: 如果你的模块 (例如 `aivk-mymodule`) 需要提供一个子命令 `aivk mymodule ...`，你需要在 `aivk_mymodule/onCli/__main__.py` 文件中定义一个名为 `cli` 的 `click.Group` 或 `click.Command` 对象。

```python
# src/aivk_mymodule/onCli/__main__.py
import click

@click.group()
def cli():
    """MyModule's CLI commands."""
    pass

@cli.command()
@click.option('--name', default='World', help='Who to greet.')
def greet(name):
    """Greets the user."""
    click.echo(f"Hello from MyModule, {name}!")

# AivkGroup 会尝试导入 aivk-mymodule.onCli 并获取 cli 对象
```

### 模块基类 | Module Base Class | モジュール基底クラス

```python
from aivk.base import AivkModule, AivkException

class MyModule(AivkModule):
    """自定义模块 | Custom module | カスタムモジュール"""
    
    async def on_load(self) -> None:
        """
        加载时调用 | Called on load | ロード時に呼び出し
        """
        pass
        
    async def on_unload(self) -> None:
        """
        卸载时调用 | Called on unload | アンロード時に呼び出し
        """
        pass
        
    async def on_update(self) -> None:
        """
        更新时调用 | Called on update | 更新時に呼び出し
        """
        pass
```

### 事件处理 | Event Handling | イベント処理

```python
from aivk.base import on_event, AivkEventType

@on_event(AivkEventType.MODULE_LOAD)
async def handle_module_load(event_data: Dict[str, Any]) -> None:
    """
    模块加载事件处理 | Module load event handler | モジュールロードイベントハンドラー
    """
    module_id = event_data["module_id"]
    # 处理逻辑 | Handling logic | 処理ロジック
```

## 测试指南 | Testing Guide | テストガイド

### 单元测试 | Unit Tests | ユニットテスト

```python
# test_mymodule.py
import pytest
from aivk_mymodule import MyModule

@pytest.fixture
def module():
    return MyModule()

async def test_load(module):
    """测试加载 | Test loading | ロードのテスト"""
    await module.on_load()
    assert module.is_loaded

async def test_unload(module):
    """测试卸载 | Test unloading | アンロードのテスト"""
    await module.on_unload()
    assert not module.is_loaded
```

### 集成测试 | Integration Tests | 統合テスト

```python
# test_integration.py
import pytest
# 假设 aivk_cli 是 AivkCLI 的实例
# from aivk.onCli.__main__ import aivk as aivk_cli

async def test_module_lifecycle():
    """
    测试模块生命周期 | Test module lifecycle | モジュールのライフサイクルをテスト
    """
    # 获取操作函数
    install_func = aivk_cli.on("install", "aivk") # 使用 aivk 作为示例 ID
    load_func = aivk_cli.on("load", "aivk")
    unload_func = aivk_cli.on("unload", "aivk")
    uninstall_func = aivk_cli.on("uninstall", "aivk")

    # 安装 (假设 install 函数接受 id)
    await install_func(id="mymodule")

    # 加载 (假设 load 函数接受 path)
    await load_func(path="~/.aivk") # 示例路径

    # 卸载 (假设 unload 函数接受 path)
    await unload_func(path="~/.aivk") # 示例路径

    # 卸载 (假设 uninstall 函数接受 id)
    await uninstall_func(id="mymodule")
```

## 发布流程 | Release Process | リリースプロセス

### 版本管理 | Version Management | バージョン管理

```toml
# pyproject.toml
[tool.poetry]
name = "aivk-mymodule"
version = "0.1.0"     # 遵循语义化版本 | Follow SemVer | セマンティックバージョニング
```

### 发布清单 | Release Checklist | リリースチェックリスト

1. 更新版本 | Update version | バージョンの更新
2. 运行测试 | Run tests | テストの実行
3. 更新文档 | Update docs | ドキュメントの更新
4. 创建变更日志 | Create changelog | 変更履歴の作成
5. 构建包 | Build package | パッケージのビルド
6. 发布到 PyPI | Publish to PyPI | PyPIに公開

### 自动化发布 | Automated Release | 自動リリース

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and publish
        run: |
          poetry build
          poetry publish
```

## 最佳实践 | Best Practices | ベストプラクティス

### 代码风格 | Code Style | コードスタイル

1. 遵循 PEP 8 | Follow PEP 8 | PEP 8に従う
2. 使用类型注解 | Use type hints | 型ヒントを使用
3. 编写文档字符串 | Write docstrings | ドキュメント文字列を書く

### 性能优化 | Performance Optimization | パフォーマンス最適化

1. 使用异步操作 | Use async operations | 非同期操作を使用
2. 实现缓存 | Implement caching | キャッシュを実装
3. 优化资源使用 | Optimize resource usage | リソース使用を最適化

### 安全性 | Security | セキュリティ

1. 验证输入 | Validate input | 入力を検証
2. 安全存储凭证 | Store credentials safely | 認証情報を安全に保存
3. 限制权限 | Limit permissions | 権限を制限

## 故障排除 | Troubleshooting | トラブルシューティング

### 常见问题 | Common Issues | よくある問題

1. 模块加载失败 | Module load failure | モジュールロード失敗
   - 检查依赖 | Check dependencies | 依存関係を確認
   - 验证路径 | Verify paths | パスを確認
   - 查看日志 | Check logs | ログを確認

2. 测试失败 | Test failures | テスト失敗
   - 隔离环境 | Isolate environment | 環境を分離
   - 清理缓存 | Clean cache | キャッシュをクリア
   - 更新依赖 | Update dependencies | 依存関係を更新

### 调试技巧 | Debugging Tips | デバッグのコツ

```python
# 启用调试日志 | Enable debug logging | デバッグログを有効化
import logging
logging.getLogger("aivk").setLevel(logging.DEBUG)

# 使用调试器 | Use debugger | デバッガーを使用
import pdb; pdb.set_trace()
```

## 社区贡献 | Community Contribution | コミュニティ貢献

### 贡献指南 | Contribution Guidelines | 貢献ガイドライン

1. 创建分支 | Create branch | ブランチを作成
2. 编写代码 | Write code | コードを書く
3. 添加测试 | Add tests | テストを追加
4. 提交 PR | Submit PR | PRを提出

### 代码评审 | Code Review | コードレビュー

- 遵循清单 | Follow checklist | チェックリストに従う
- 编写说明 | Write descriptions | 説明を書く
- 及时响应 | Respond timely | 迅速に対応

### 文档贡献 | Documentation Contribution | ドキュメント貢献

1. 改进现有文档 | Improve existing docs | 既存のドキュメントを改善
2. 添加示例 | Add examples | 例を追加
3. 修复错误 | Fix errors | エラーを修正
4. 翻译文档 | Translate documentation | ドキュメントを翻訳
# AIVK CLI Module | AIVK 命令行模块 | AIVK CLIモジュール

## Overview | 概述 | 概要

AIVK 的命令行接口模块，提供命令行工具和交互功能。  
Command line interface module for AIVK, providing CLI tools and interaction.  
AIVK のコマンドラインインターフェースモジュール。CLIツールと対話機能を提供。

## Commands | 命令 | コマンド

### Core Commands | 核心命令 | コアコマンド

```bash
# Show help | 显示帮助 | ヘルプを表示
aivk --help
aivk help <command>

# Show version | 显示版本 | バージョンを表示
aivk version
```

### Module Management | 模块管理 | モジュール管理

```bash
# Install module | 安装模块 | モジュールをインストール
aivk install <module_id>
aivk install <module_id>@<version>

# Update module | 更新模块 | モジュールを更新
aivk update <module_id>
aivk update --all

# Uninstall module | 卸载模块 | モジュールをアンインストール
aivk uninstall <module_id>
```

### Runtime Operations | 运行时操作 | ランタイム操作

```bash
# Load module | 加载模块 | モジュールをロード
aivk load [--path <path>] [--module <module_id>]

# Unload module | 卸载模块 | モジュールをアンロード
aivk unload [--module <module_id>] [--force]

# List modules | 列出模块 | モジュールを一覧表示
aivk list [--installed] [--enabled] [--verbose]
```

## Configuration | 配置 | 設定

### Environment Variables | 环境变量 | 環境変数

| Variable | Description | 描述 | 説明 |
|----------|-------------|------|------|
| AIVK_ROOT | Root directory | 根目录 | ルートディレクトリ |
| AIVK_CONFIG | Config file path | 配置文件路径 | 設定ファイルパス |
| AIVK_LOG_LEVEL | Log level | 日志级别 | ログレベル |

### Config File | 配置文件 | 設定ファイル

```toml
[cli]
color = true          # Enable colors | 启用颜色 | カラー有効化
verbose = false       # Verbose output | 详细输出 | 詳細出力
confirm = true        # Confirm actions | 确认操作 | 操作確認

[cli.logging]
format = "detailed"   # Log format | 日志格式 | ログ形式
level = "info"        # Log level | 日志级别 | ログレベル
```

## Error Handling | 错误处理 | エラー処理

### Exit Codes | 退出代码 | 終了コード

| Code | Description | 描述 | 説明 |
|------|-------------|------|------|
| 0 | Success | 成功 | 成功 |
| 1 | General error | 一般错误 | 一般エラー |
| 2 | Invalid usage | 无效用法 | 無効な使用法 |
| 3 | Module error | 模块错误 | モジュールエラー |

### Error Messages | 错误消息 | エラーメッセージ

Errors are displayed in following format:  
错误按以下格式显示：  
エラーは以下の形式で表示されます：

```
Error [CODE]: MESSAGE
Details: DETAILS
Suggestion: SUGGESTION
```

## Development | 开发 | 開発

### Adding Commands | 添加命令 | コマンドの追加

```python
@cli.command()
@click.argument("arg")
@click.option("--opt")
def new_command(arg, opt):
    """Command description | 命令描述 | コマンドの説明"""
    pass
```

### Command Structure | 命令结构 | コマンド構造

```
cli/
├── __init__.py
├── __main__.py      # Entry point | 入口点 | エントリーポイント
├── commands/        # Command implementations | 命令实现 | コマンド実装
└── utils/          # CLI utilities | CLI工具 | CLIユーティリティ
```

## Best Practices | 最佳实践 | ベストプラクティス

### Command Design | 命令设计 | コマンド設計

1. Consistent Format | 一致的格式 | 一貫した形式
   - Use verb-noun style | 使用动词-名词风格 | 動詞-名詞スタイルを使用
   - Keep names clear | 保持名称清晰 | 名前を明確に
   - Follow conventions | 遵循约定 | 規約に従う

2. User Experience | 用户体验 | ユーザー体験
   - Provide feedback | 提供反馈 | フィードバックを提供
   - Show progress | 显示进度 | 進捗を表示
   - Clear errors | 清晰的错误 | 明確なエラー

3. Documentation | 文档 | ドキュメント
   - Detailed help | 详细帮助 | 詳細なヘルプ
   - Examples | 示例 | 例
   - Error solutions | 错误解决方案 | エラー解決策

### Testing | 测试 | テスト

```python
# Command test example | 命令测试示例 | コマンドテスト例
def test_command():
    result = runner.invoke(cli, ["command", "--option"])
    assert result.exit_code == 0
    assert "Expected output" in result.output
```

### Security | 安全性 | セキュリティ

- Input validation | 输入验证 | 入力検証
- Permission checks | 权限检查 | 権限チェック
- Safe defaults | 安全的默认值 | 安全なデフォルト値


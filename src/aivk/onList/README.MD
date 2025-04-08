# AIVK List Module | AIVK 列表模块 | AIVK リストモジュール

## Description | 描述 | 説明

Display and manage AIVK modules information.  
显示和管理 AIVK 模块信息。  
AIVK モジュールの情報を表示、管理します。

## Commands | 命令 | コマンド

```bash
# List all modules | 列出所有模块 | すべてのモジュールを表示
aivk list

# List installed modules | 列出已安装模块 | インストール済みモジュールを表示
aivk list --installed

# List enabled modules | 列出已启用模块 | 有効なモジュールを表示
aivk list --enabled

# List with details | 列出详细信息 | 詳細情報を表示
aivk list --verbose

# Filter by type | 按类型过滤 | タイプでフィルター
aivk list --type core
```

## Output Format | 输出格式 | 出力形式

### Basic Format | 基本格式 | 基本形式
```
ID      VERSION    STATUS     TYPE
fs      0.1.0     enabled    core
ai      0.2.0     disabled   extra
webui   1.0.0     enabled    ui
```

### Detail Format | 详细格式 | 詳細形式
```
Module: fs (File System)
  Version: 0.1.0
  Status: enabled
  Type: core
  Path: /path/to/module
  Dependencies: []
  Description: File system module
```

## Configuration | 配置 | 設定

```toml
[list]
format = "table"        # Output format | 输出格式 | 出力形式
show_hidden = false    # Show hidden modules | 显示隐藏模块 | 隠しモジュールを表示
sort_by = "name"      # Sort criteria | 排序条件 | ソート条件
```

## API | 接口 | API

```python
async def list_modules(
    installed: bool = False,    # Only installed | 仅已安装 | インストール済みのみ
    enabled: bool = False,      # Only enabled | 仅已启用 | 有効なもののみ
    type: str = None,          # Filter by type | 按类型过滤 | タイプでフィルター
    verbose: bool = False      # Show details | 显示详情 | 詳細表示
) -> List[Dict]:
    """
    List modules | 列出模块 | モジュールを一覧表示
    """
    pass
```

## Module Types | 模块类型 | モジュールタイプ

| Type | Description | 描述 | 説明 |
|------|-------------|------|------|
| core | Core modules | 核心模块 | コアモジュール |
| extra | Extra modules | 扩展模块 | 拡張モジュール |
| ui | UI modules | 界面模块 | UIモジュール |
| tool | Tool modules | 工具模块 | ツールモジュール |

## Development | 开发 | 開発

### Custom List Handler | 自定义列表处理器 | カスタムリストハンドラー

```python
class ListHandler:
    """
    Custom list logic | 自定义列表逻辑 | カスタムリストロジック
    """
    def format_output(self, modules: List[Dict]) -> str:
        """Format output | 格式化输出 | 出力フォーマット"""
        pass
        
    def filter_modules(self, modules: List[Dict]) -> List[Dict]:
        """Filter modules | 过滤模块 | モジュールフィルター"""
        pass
```

### Output Formats | 输出格式 | 出力形式

- table: Table format | 表格格式 | テーブル形式
- json: JSON format | JSON格式 | JSON形式
- yaml: YAML format | YAML格式 | YAML形式
- tree: Tree format | 树形格式 | ツリー形式
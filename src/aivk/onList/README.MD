# AIVK List Module | AIVK 列表模块 | AIVK リストモジュール

## Description | 描述 | 説明

Display installed AIVK related modules.
显示已安装的 AIVK 相关模块。
インストールされている AIVK 関連モジュールを表示します。

## Commands | 命令 | コマンド

```bash
# List installed modules | 列出已安装模块 | インストール済みモジュールを表示
aivk list
```
*注意：* 当前 CLI 实现不支持 `--installed`, `--enabled`, `--verbose`, `--type` 等参数。

## Output Format | 输出格式 | 出力形式

### Basic Format | 基本格式 | 基本形式
当前实现通过日志输出找到的模块名列表。
The current implementation outputs the list of found module names via logging.
現在の実装では、見つかったモジュール名のリストがログ経由で出力されます。

```
INFO    Found aivk modules: aivk, fs, net, ...
```
或 (如果未找到)
Or (if none found)
または（見つからない場合）
```
WARNING No aivk modules found.
```

### Detail Format | 详细格式 | 詳細形式
当前未实现。
Not currently implemented.
現在実装されていません。

## Configuration | 配置 | 設定
当前模块无特定配置。
No specific configuration for this module currently.
現在、このモジュールに固有の設定はありません。

## API | 接口 | API

```python
# 定义在 src/aivk/onList/__main__.py
async def list(
    **kwargs: Dict[str, Any] # 当前未使用 kwargs | kwargs currently unused
) -> List[str]:
    """
    List installed AIVK modules by scanning package metadata.
    通过扫描包元数据列出已安装的 AIVK 模块。
    パッケージメタデータをスキャンして、インストールされている AIVK モジュールを一覧表示します。
    """
    pass
```

## Module Types | 模块类型 | モジュールタイプ
当前实现不区分模块类型。
The current implementation does not differentiate module types.
現在の実装ではモジュールタイプを区別しません。

## Development | 开发 | 開発
当前模块实现较为简单，主要依赖 `importlib.metadata`。
The current module implementation is relatively simple, mainly relying on `importlib.metadata`.
現在のモジュールの実装は比較的単純で、主に `importlib.metadata` に依存しています。
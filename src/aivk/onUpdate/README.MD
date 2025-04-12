# AIVK Update Module | AIVK 更新模块 | AIVK アップデートモジュール

## Overview | 概述 | 概要

This module handles AIVK package updates.  
此模块处理 AIVK 包的更新操作。  
このモジュールは AIVK パッケージの更新を処理します。

## Features | 功能特性 | 機能

- Automatic version check | 自动版本检查 | 自動バージョンチェック
- Dependencies update | 依赖项更新 | 依存関係の更新
- Configuration migration | 配置迁移 | 設定の移行
- Rollback support | 回滚支持 | ロールバックサポート

## Usage | 使用方法 | 使用方法

```bash
# Update all modules (当前实现) | Update all modules (current implementation) | すべてのモジュールを更新 (現在の実装)
aivk update
```
*注意：* 当前 CLI 实现不支持 `<module_id>`, `--all`, `--check`, `--rollback` 等参数。文档中的其他用法可能代表预期功能而非当前实现。

## Configuration | 配置说明 | 設定

### Environment Variables | 环境变量 | 環境変数

- `AIVK_UPDATE_CHANNEL`: Update channel (stable/beta) | 更新通道（稳定版/测试版） | 更新チャネル（安定版/ベータ版）
- `AIVK_AUTO_UPDATE`: Enable auto update (true/false) | 启用自动更新（是/否） | 自動更新の有効化（はい/いいえ）

### Config File | 配置文件 | 設定ファイル

```toml
[update]
channel = "stable"    # Update channel | 更新通道 | 更新チャネル
auto = false         # Auto update | 自动更新 | 自動更新
check_interval = 24  # Hours | 小时 | 時間
```

## Error Handling | 错误处理 | エラー処理

| Code | English | 中文 | 日本語 |
|------|----------|------|---------|
| E001 | Network Error | 网络错误 | ネットワークエラー |
| E002 | Version Conflict | 版本冲突 | バージョン競合 |
| E003 | Permission Denied | 权限不足 | 権限不足 |
| E004 | Update Failed | 更新失败 | 更新失敗 |
| E005 | Rollback Failed | 回滚失败 | ロールバック失敗 |

## Development | 开发指南 | 開発ガイド

### API | 接口 | API

实际的 `update` 函数由 `aivk.on("update", "aivk")` 动态加载。根据 `onCli/__main__.py` 中的调用，其当前签名不接受参数。
The actual `update` function is dynamically loaded via `aivk.on("update", "aivk")`. Based on the call in `onCli/__main__.py`, its current signature accepts no arguments.
実際の `update` 関数は `aivk.on("update", "aivk")` を介して動的にロードされます。`onCli/__main__.py` での呼び出しに基づくと、現在のシグネチャは引数を受け入れません。

```python
# 预期的签名 (基于 CLI) | Expected signature (based on CLI)
async def update(
    **kwargs: Dict[str, Any] # 捕获其他可能的参数 | Capture other possible args
) -> Any: # 返回类型未知 | Return type unknown
    """
    Update module(s) | 更新模块 | モジュールを更新
    """
    pass
```
*注意：* README 中原有的 API 签名 (`module_id`, `version`, `force`) 可能代表预期功能或更底层的 API，而非当前 CLI 调用的函数。

### Events | 事件 | イベント

- `pre_update`: Before update | 更新前 | 更新前
- `post_update`: After update | 更新后 | 更新後
- `update_failed`: Update failed | 更新失败 | 更新失敗
- `rollback_start`: Start rollback | 开始回滚 | ロールバック開始

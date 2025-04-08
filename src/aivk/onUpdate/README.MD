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
# Update specific module | 更新指定模块 | 特定のモジュールを更新
aivk update <module_id>

# Update all modules | 更新所有模块 | すべてのモジュールを更新
aivk update --all

# Check for updates | 检查更新 | 更新を確認
aivk update --check

# Rollback to previous version | 回滚到之前版本 | 以前のバージョンにロールバック
aivk update --rollback <module_id>
```

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

```python
async def update(
    module_id: str,      # Module ID | 模块ID | モジュールID
    version: str = None, # Target version | 目标版本 | 対象バージョン
    force: bool = False  # Force update | 强制更新 | 強制更新
) -> bool:
    """
    Update module | 更新模块 | モジュールを更新
    """
    pass
```

### Events | 事件 | イベント

- `pre_update`: Before update | 更新前 | 更新前
- `post_update`: After update | 更新后 | 更新後
- `update_failed`: Update failed | 更新失败 | 更新失敗
- `rollback_start`: Start rollback | 开始回滚 | ロールバック開始

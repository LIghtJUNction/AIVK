# AIVK Uninstall Module | AIVK 卸载模块 | AIVK アンインストールモジュール

## Overview | 概述 | 概要

Module for managing AIVK package uninstallation process.  
管理 AIVK 包卸载过程的模块。  
AIVK パッケージのアンインストールプロセスを管理するモジュール。

## Features | 功能特性 | 機能

- Safe removal | 安全移除 | 安全な削除
- Dependency handling | 依赖处理 | 依存関係処理
- Configuration backup | 配置备份 | 設定バックアップ
- Data preservation | 数据保留 | データ保持

## Commands | 命令 | コマンド

```bash
# Basic uninstall | 基本卸载 | 基本アンインストール
aivk uninstall <module_id>

# Force uninstall | 强制卸载 | 強制アンインストール
aivk uninstall <module_id> --force

# Uninstall with config removal | 卸载并删除配置 | 設定も含めてアンインストール
aivk uninstall <module_id> --purge

# Batch uninstall | 批量卸载 | バッチアンインストール
aivk uninstall <module_id_1> <module_id_2>
```

## Configuration | 配置 | 設定

### Environment Variables | 环境变量 | 環境変数

- `AIVK_KEEP_CONFIG`: Keep configuration (true/false) | 保留配置（是/否） | 設定保持（はい/いいえ）
- `AIVK_BACKUP_PATH`: Backup location | 备份位置 | バックアップ場所

### Settings | 设置 | 設定

```toml
[uninstall]
backup = true           # Create backup | 创建备份 | バックアップ作成
keep_data = true       # Keep user data | 保留用户数据 | ユーザーデータ保持
clean_deps = false     # Remove dependencies | 移除依赖 | 依存関係削除
```

## Process | 处理流程 | プロセス

1. Pre-uninstall checks | 卸载前检查 | アンインストール前チェック
2. Backup creation | 创建备份 | バックアップ作成
3. Dependency resolution | 依赖解析 | 依存関係解決
4. Package removal | 包移除 | パッケージ削除
5. Cleanup | 清理 | クリーンアップ

## Error Handling | 错误处理 | エラー処理

| Error Code | Description | 描述 | 説明 |
|------------|-------------|------|------|
| U001 | Module in use | 模块使用中 | モジュール使用中 |
| U002 | Dependency conflict | 依赖冲突 | 依存関係の競合 |
| U003 | Permission error | 权限错误 | 権限エラー |

## API Reference | API 参考 | API リファレンス

```python
async def uninstall(
    module_id: str,         # Module ID | 模块ID | モジュールID
    force: bool = False,    # Force uninstall | 强制卸载 | 強制アンインストール
    purge: bool = False,    # Remove config | 删除配置 | 設定削除
    backup: bool = True     # Create backup | 创建备份 | バックアップ作成
) -> bool:
    """
    Uninstall module | 卸载模块 | モジュールをアンインストール
    """
    pass
```

## Recovery | 恢复 | リカバリー

### Backup Restoration | 备份恢复 | バックアップ復元

```bash
# Restore from backup | 从备份恢复 | バックアップから復元
aivk restore <module_id> --backup <backup_id>

# List backups | 列出备份 | バックアップ一覧
aivk backup list <module_id>
```

## Development | 开发 | 開発

### Event Hooks | 事件钩子 | イベントフック

- `pre_uninstall`: Before uninstall | 卸载前 | アンインストール前
- `post_uninstall`: After uninstall | 卸载后 | アンインストール後
- `cleanup`: During cleanup | 清理时 | クリーンアップ中

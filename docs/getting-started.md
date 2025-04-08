# AIVK 入门指南 | Getting Started | 入門ガイド

## 系统要求 | System Requirements | システム要件

### 基本要求 | Basic Requirements | 基本要件

- Python 3.8+ | Python 3.8以上 | Python 3.8以上
- pip 20.0+ | pip 20.0以上 | pip 20.0以上
- Git (可选) | Git (optional) | Git (オプション)

### 推荐配置 | Recommended Setup | 推奨設定

- 操作系统 | Operating System | オペレーティングシステム
  - Linux (Ubuntu 20.04+, CentOS 8+)
  - Windows 10/11
  - macOS 11+
- 内存 | Memory | メモリ: 4GB+
- 磁盘空间 | Disk Space | ディスク容量: 1GB+

## 安装步骤 | Installation Steps | インストール手順

### 1. 环境准备 | Environment Preparation | 環境準備

```bash
# 创建虚拟环境 | Create virtual environment | 仮想環境の作成
python -m venv aivk-env

# 激活虚拟环境 | Activate virtual environment | 仮想環境の有効化
# Windows:
aivk-env\\Scripts\\activate
# Linux/macOS:
source aivk-env/bin/activate
```

### 2. 安装 AIVK | Install AIVK | AIVKのインストール

```bash
# 通过 pip 安装 | Install via pip | pipでインストール
pip install aivk

# 验证安装 | Verify installation | インストールの確認
aivk version
```

### 3. 初始配置 | Initial Setup | 初期設定

```bash
# 初始化配置 | Initialize configuration | 設定の初期化
aivk init

# 配置环境变量 | Configure environment variables | 環境変数の設定
# Windows:
set AIVK_ROOT=C:\\Users\\username\\.aivk
# Linux/macOS:
export AIVK_ROOT=~/.aivk
```

## 基础使用 | Basic Usage | 基本的な使用方法

### 模块管理 | Module Management | モジュール管理

```bash
# 列出可用模块 | List available modules | 利用可能なモジュールを一覧表示
aivk list

# 安装核心模块 | Install core modules | コアモジュールをインストール
aivk install fs
aivk install net
aivk install ai

# 查看模块状态 | Check module status | モジュールの状態を確認
aivk list --installed
```

### 加载模块 | Loading Modules | モジュールのロード

```bash
# 加载所有模块 | Load all modules | すべてのモジュールをロード
aivk load

# 加载特定模块 | Load specific module | 特定のモジュールをロード
aivk load --module fs

# 检查加载状态 | Check load status | ロード状態を確認
aivk list --enabled
```

### 基本操作 | Basic Operations | 基本操作

```bash
# 显示帮助 | Show help | ヘルプを表示
aivk help
aivk help <command>

# 检查版本 | Check version | バージョンを確認
aivk version

# 查看状态 | Check status | 状態を確認
aivk status
```

## 配置指南 | Configuration Guide | 設定ガイド

### 配置文件 | Configuration Files | 設定ファイル

```toml
# ~/.aivk/config.toml

[aivk]
# 基本设置 | Basic settings | 基本設定
root = "~/.aivk"
log_level = "info"

[modules]
# 自动加载 | Auto load | 自動ロード
autoload = ["fs", "net"]

[logging]
# 日志设置 | Logging settings | ログ設定
format = "detailed"
output = "file"
```

### 环境变量 | Environment Variables | 環境変数

| 变量 | Variable | 変数 | 说明 | Description | 説明 |
|------|----------|------|------|-------------|------|
| AIVK_ROOT | AIVK根目录 | Root directory | ルートディレクトリ |
| AIVK_CONFIG | 配置文件路径 | Config file path | 設定ファイルパス |
| AIVK_LOG_LEVEL | 日志级别 | Log level | ログレベル |

## 常见问题 | Common Issues | よくある問題

### 1. 安装问题 | Installation Issues | インストールの問題

#### 问题 | Issue | 問題
pip 安装失败  
pip installation fails  
pipインストールが失敗

#### 解决方案 | Solution | 解決策
```bash
# 更新 pip | Update pip | pipの更新
python -m pip install --upgrade pip

# 使用镜像源 | Use mirror | ミラーを使用
pip install aivk -i https://mirrors.aliyun.com/pypi/simple/
```

### 2. 权限问题 | Permission Issues | 権限の問題

#### 问题 | Issue | 問題
无法访问配置目录  
Cannot access config directory  
設定ディレクトリにアクセスできない

#### 解决方案 | Solution | 解決策
```bash
# 检查权限 | Check permissions | 権限を確認
ls -la ~/.aivk

# 修复权限 | Fix permissions | 権限を修正
chmod -R 755 ~/.aivk
```

## 下一步 | Next Steps | 次のステップ

1. 查看示例 | Check Examples | 例を確認
   - [基础示例](../examples/basic)
   - [进阶示例](../examples/advanced)

2. 阅读文档 | Read Documentation | ドキュメントを読む
   - [API参考](./api-reference.md)
   - [开发指南](./development.md)

3. 参与社区 | Join Community | コミュニティに参加
   - [GitHub讨论](https://github.com/yourusername/aivk/discussions)
   - [问题追踪](https://github.com/yourusername/aivk/issues)
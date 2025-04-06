# AIVK

AIVK 是一个模块化的 AI 开发框架。
AIVK is a modular AI development framework.

## 核心模块 | Core Modules

AIVK 包含以下核心模块：
AIVK includes the following core modules:

| 模块 ID | 描述 | Description |
|---------|------|-------------|
| `aivk` | 核心框架 | Core Framework |
| `aivk-fs` | 文件系统模块 | File System Module |
| `aivk-loader` | 模块加载器 | Module Loader |
| `aivk-messenger` | 消息通信模块 | Message Communication Module |
| `aivk-scheduler` | 调度器模块 | Scheduler Module |
| `aivk-ai` | AI 功能模块 | AI Functionality Module |

### 特殊模块 | Special Modules

| 模块 ID | 描述 | Description |
|---------|------|-------------|
| `aivk-webui` | Web 界面模块 | Web Interface Module |

## 快速开始 | Quick Start

### 1. 安装 AIVK | Install AIVK

```bash
# 使用 pip 安装 | Install using pip
pip install aivk

# 或使用 uv 安装 | Or install using uv
uv pip install aivk
```

### 2. 安装核心模块 | Install Core Modules

```bash
# 使用默认配置 | Using default configuration
aivk install core

# 或指定配置文件 | Or specify configuration file
aivk install core --config <path/to/config.toml>
```

默认配置文件位于 `src/aivk/config.toml`
Default configuration file is located at `src/aivk/config.toml`

### 3. 初始化 AIVK 根目录 | Initialize AIVK Root Directory

AIVK 根目录可以通过以下方式设置：
AIVK root directory can be set through:

- 使用环境变量 `AIVK_ROOT`（可选）| Using environment variable `AIVK_ROOT` (optional)
- 默认路径 | Default path: `~/.aivk`

以下命令都是等价的初始化命令：
The following initialization commands are equivalent:

```bash
# 使用默认路径 | Using default path
aivk fs init

# 使用环境变量 | Using environment variable
aivk fs init AIVK_ROOT

# 指定自定义路径 | Specify custom path
aivk fs init --path <path/to/aivk_root_dir>    # 方式 1 | Method 1
aivk-fs init --path <path/to/aivk_root_dir>    # 方式 2 | Method 2
aivk-fs-init --path <path/to/aivk_root_dir>    # 方式 3 | Method 3
```

### 4. 加载框架 | Load Framework

以下加载命令是等价的：
The following load commands are equivalent:

```bash
# 使用指定路径 | Using specified path
aivk load --path <path/to/aivk_root_dir>       # 方式 1 | Method 1
aivk-load --path <path/to/aivk_root_dir>       # 方式 2 | Method 2

# 使用环境变量 | Using environment variable
aivk load --path AIVK_ROOT
```

## CLI 命令参考 | CLI Command Reference

### 基础命令 | Basic Commands

以下帮助命令是等价的：
The following help commands are equivalent:

```bash
# 查看帮助 | View help
aivk -h
aivk --h
aivk help
```

模块管理命令：
Module management commands:

```bash
# 模块管理 | Module Management
aivk install <moduleID>     # 安装模块 | Install module
aivk uninstall <moduleID>   # 卸载模块 | Uninstall module
aivk update <moduleID>      # 更新模块 | Update module
aivk load --path <path>     # 加载框架 | Load framework
```

### 模块命令格式 | Module Command Format

每个模块都支持以下等价的命令格式：
Each module supports the following equivalent command formats:

```bash
# 模块命令格式 | Module Command Format
aivk-<moduleID> [command]           # 模块主命令 | Module main command
aivk-<moduleID>-load                # 加载模块 | Load module
aivk-<moduleID>-unload              # 卸载模块 | Unload module
aivk-<moduleID>-install             # 安装模块 | Install module
aivk-<moduleID>-uninstall           # 卸载模块 | Uninstall module
aivk-<moduleID>-update              # 更新模块 | Update module
```

所有命令都支持以下等价的帮助参数：
All commands support the following equivalent help parameters:

```bash
# 查看特定命令帮助 | View specific command help
aivk-<moduleID> -h
aivk <moduleID> load -h
aivk <moduleID> unload -h
aivk <moduleID> install -h
aivk <moduleID> uninstall -h
aivk <moduleID> update -h
```

## 许可证 | License

[许可证信息 | License Information]




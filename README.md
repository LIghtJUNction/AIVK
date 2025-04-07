# AIVK

AIVK 是一个模块化的 AI 开发框架。
AIVK is a modular AI development framework.

## 特性 | Features

- 🚀 模块化设计 | Modular Design
- 🔌 插件系统 | Plugin System
- 🛠️ CLI 工具 | CLI Tools
- 📦 包管理 | Package Management
- 🔄 热重载 | Hot Reload
- 🌐 多语言支持 | Multi-language Support

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

## 安装 | Installation

### 使用 pip 安装 | Install with pip

```bash
pip install aivk
```

### 使用 uv 安装 | Install with uv

```bash
uv pip install aivk
```

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

# 使用环境变量 | Using environment variable
aivk load --path AIVK_ROOT
```

## CLI 命令 | CLI Commands

### 核心命令 | Core Commands

```bash
# 查看帮助 | View help
aivk --help

# 加载框架 | Load framework
aivk load [--path PATH] [--config CONFIG]

# 卸载框架 | Unload framework
aivk unload [--path PATH] [--config CONFIG]

# 安装模块 | Install module
aivk install [MODULE_ID] [--config CONFIG]

# 卸载模块 | Uninstall module
aivk uninstall [MODULE_ID] [--config CONFIG]

# 更新模块 | Update module
aivk update [MODULE_ID] [--config CONFIG]
```

### 模块命令 | Module Commands

AIVK 支持两种等效的模块命令调用方式：

1. 通过主命令调用 | Via main command:
```bash
aivk <module_id> <command> [options]
```

2. 通过独立命令调用 | Via standalone command:
```bash
aivk-<module_id> <command> [options]
```

例如 | For example:
```bash
# 这两个命令是等效的 | These two commands are equivalent
aivk webui start --port 8080
aivk-webui start --port 8080
```

## 模块开发 | Module Development

### 创建新模块 | Create New Module

1. 初始化模块项目 | Initialize module project
```bash
mkdir aivk-<module_id>
cd aivk-<module_id>

uv init --package .
```

2. 创建项目结构 | Create project structure
```
...
src
└── aivk-<module_id>
    ├...

```

3. 配置 pyproject.toml | Configure pyproject.toml
```toml
[project]
name = "aivk-<module_id>"
version = "0.1.0"
description = "AIVK module description"
requires-python = ">=3.13"
dependencies = [
    "aivk>=0.2.0",
]

[project.scripts]
aivk-<module_id> = "aivk_<module_id>.cli.__main__:main" # avoid name conflict

```

### 实现模块 CLI | Implement Module CLI

在 `cli.py` 中实现命令行接口 | Implement CLI in `cli.py`:

```python
import click

@click.group()
def module():
    """模块命令组"""
    pass

@module.command()
def command1():
    """Command 1 description"""
    pass

@module.command()
def command2():
    """Command 2 description"""
    pass

def main():
    """入口点"""
    module()
```

### 发布模块 | Publish Module

1. 构建项目 | Build project
```bash
uv build
```

2. 发布到 PyPI | Publish to PyPI
```bash
uv publish
```

## 配置 | Configuration

### 环境变量 | Environment Variables

- `AIVK_ROOT`: AIVK 根目录 | AIVK root directory
- `AIVK_CONFIG`: 配置文件路径 | Configuration file path

### 配置文件 | Configuration Files

默认配置文件位置 | Default configuration file locations:
- `src/aivk/config.toml`: 全局配置 | Global configuration
- `~/.aivk/config.toml`: 用户配置 | User configuration
- `./config.toml`: 项目配置 | Project configuration

## 示例 | Examples

### 创建并运行 WebUI 模块 | Create and Run WebUI Module

```bash
# 安装模块 | Install module
aivk install webui

# 启动服务 | Start service
aivk webui start --port 8080
# 或 | or
aivk-webui start --port 8080

# 停止服务 | Stop service
aivk webui stop
# 或 | or
aivk-webui stop
```

## 贡献指南 | Contributing

1. Fork 项目 | Fork the project
2. 创建特性分支 | Create feature branch
3. 提交变更 | Commit changes
4. 推送到分支 | Push to branch
5. 创建 Pull Request | Create Pull Request

## 许可证 | License

[MIT License](LICENSE)




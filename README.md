# AIVK - AI Virtual Kernel

AIVK (AI Virtual Kernel) 是一个高度模块化的AI应用框架，提供插件化架构和事件驱动设计，支持多种AI模型和服务集成。

# 语言 / Languages

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md)

## 核心特性

- **模块化设计**：基于LKM（可加载内核模块）的架构，支持动态加载和卸载功能模块
- **完整的生命周期管理**：提供初始化、挂载、卸载和更新等完整生命周期控制
- **插件系统**：支持多种插件类型，包括LLM提供者、数据源、UI组件、工具和扩展
- **事件驱动架构**：基于发布-订阅模式的事件总线，实现组件间的松耦合通信
- **统一的配置管理**：灵活的配置和目录结构管理，支持多环境配置
- **灵活的模块管理方式**：aivk本身即为一种特殊模块
- **其他核心模块开发中**
  
## 安装

### 使用uv安装（推荐）

#### Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Linux/MacOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或
wget -qO- https://astral.sh/uv/install.sh | sh
```

更多安装选项请参考 [uv安装文档](https://hellowac.github.io/uv-zh-cn/getting-started/installation/)

### 安装AIVK

#### 安装命令行工具:

```bash
uv tool install aivk
```

#### 安装Python包:

```bash
uv pip install aivk
```

#### 为项目添加AIVK依赖:

```bash
uv add aivk
```

AIVK本身是一个特殊的AIVK模块，提供基础功能与命令行工具，核心功能由AIVK核心模块提供。

## 快速开始

### 初始化AIVK环境
AIVK_ROOT 替换为aivk根目录路径（空目录或不存在：自动新建）
如果不替换，将使用AIVK_ROOT环境变量
tip：
  修改AIVK_ROOT环境变量为指定目录
  可以新建文件夹后将该文件夹拖动至终端快捷填入路径
 
初始化：
```bash
aivk -i AIVK_ROOT
```

### 挂载AIVK目录
挂载即启动aivk元模块 元模块启动后将立即加载加载器loader
```bash
aivk -m AIVK_ROOT
```

### 运行AIVK CLI界面
菜单：
```bash
aivk
```

## 目录结构

AIVK创建的标准目录结构如下:

```
aivk_root/
├── .aivk           # AIVK初始化标记文件
├── meta.toml       # 元数据文件
├── cache/          # 缓存数据
├── data/           # 持久化数据
├── logs/           # 日志文件
├── modules/        # 模块目录
├── modules_bak/    # 模块备份
├── modules_update/ # 模块更新
└── tmp/            # 临时文件
```

## 开发文档

更详细的开发文档请参考 `docs/` 目录下的文档:

- [项目蓝图](docs/project_blueprint.md)
- [文件结构](docs/file_structure.md)
- [插件开发指南](docs/plugins/README.md)
- [API参考](docs/api_reference.md)
- [快捷模块开发模板](https://github.com/LIghtJUNction/aivk-module-sample)

## 贡献指南

欢迎贡献代码、报告问题或提供建议。请参阅 [贡献指南](CONTRIBUTING.md) 了解更多信息。

## 许可证

MIT

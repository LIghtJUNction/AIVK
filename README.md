# AIVK - AI Virtual Kernel
[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)
AIVK 是一个面向 AI 的虚拟内核（AI Virtual Kernel），支持模块化扩展、MCP 协议、命令行交互和自动化管理。

## 项目简介

- **AIVK** 提供统一的 AI 虚拟根目录管理、配置与元数据管理、模块注册与发现、MCP 服务器能力。
- 支持通过命令行（CLI）和 MCP 协议进行交互。
- 适合 AI Agent、AI 工具链、自动化脚本等场景。
.
## 主要特性

- AIVK 根目录初始化与挂载
- 配置与元数据（TOML）管理
- 交互式 Shell（支持常用文件系统命令）
- MCP 服务器（支持 stdio / SSE 传输）
- 模块注册与发现
- 同步/异步系统命令执行
- 类型检查支持（py.typed）

## 安装
基于πthon ，推荐使用 uv



```bash
pip install aivk
# 或使用 uv
uv pip install aivk
```

## 快速上手

### 初始化 AIVK 根目录

```bash
aivk init --path ./aivk_root
```

### 挂载根目录并进入交互式 Shell

```bash
aivk mount -p ./aivk_root -i
```

### 查看状态

```bash
aivk status
```

### 启动 MCP 服务器

```bash
aivk mcp --transport stdio
# 或
aivk mcp --transport sse --host 0.0.0.0 --port 10140
```

## 目录结构说明

```
AIVK/
├── src/aivk/           # 主包目录
│   ├── base/           # IO、FS、工具等基础模块
│   ├── cli/            # 命令行入口
│   ├── mcp/            # MCP 服务器实现
│   ├── api/            # API 汇总
│   └── ...
├── aivk_root/          # 初始化后的根目录示例
│   ├── etc/aivk/       # 配置与元数据
│   ├── src/aivk_agent/ # 示例模块
│   └── ...
├── pyproject.toml      # 构建配置
├── uv.lock             # 依赖锁定
├── README.md           # 项目说明
└── ...
```

## 命令行用法

- `aivk init [--force] [--path PATH]`  初始化根目录
- `aivk mount [--path PATH] [-i]`      挂载根目录并可进入交互式 Shell
- `aivk shell [--path PATH]`           进入交互式 Shell
- `aivk status`                        查看状态
- `aivk mcp [--transport stdio|sse] [--host HOST] [--port PORT] [--save-config]`  启动 MCP 服务器
- `aivk help [COMMAND]`                查看帮助

### 交互式 Shell 支持命令

- help, exit, clear, status, version
- ls, cd, pwd, cat, mkdir
- !<系统命令>（如 !ls, !dir）

## MCP 服务器

- 支持 stdio / SSE 传输
- 资源接口：
  - `aivk://status`  获取状态
  - `aivk://root`    获取根目录
- 工具接口：
  - `init_aivk_root_dir`  初始化根目录
  - `mount_aivk_root_dir` 挂载根目录
  - `set_aivk_root_dir`   设置根目录
  - `get_config`、`get_meta`、`get_module_ids`  获取配置/元数据/模块列表
  - `ping`  测试连接

## AIVK MODULE 规范

1. AIVK MODULE 是一个 PyPI 包。
2. 基于 MCP 协议。
3. 命名规则：
   - PyPI 包名: `aivk_{id}`（如 `aivk_fs`）
   - 导入名称: `aivk_{id}`（如 `import aivk_fs`）

## 常见问题

- **Q: 如何自定义根目录？**
  A: 使用 `aivk init --path <路径>` 或 `aivk mount --path <路径>`。
- **Q: 如何开发自定义模块？**
  A: 遵循“模块规范”开发 PyPI 包，参考 `src/aivk_agent`。
- **Q: 如何与 MCP 服务器交互？**
  A: 可用 mcp 客户端、curl、httpx 等工具访问。

## 贡献与协议

- 开源协议：MIT
- GitHub: https://github.com/LIghtJUNction/AIVK
- 欢迎 issue、PR 与建议！

---

> © 2025 LIghtJUNction. Powered by AIVK.

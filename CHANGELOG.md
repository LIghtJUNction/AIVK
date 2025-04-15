# 更新日志

所有此项目的显著变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且此项目遵循 [语义化版本](https://semver.org/lang/zh-CN/spec/v2.0.0.html)。

## [0.3.3.0] - 2025-04-16

### 新增
(Wow)
*   **核心 IO (`AivkIO`)**:
    *   实现 AIVK 根目录的初始化 (`fs_init`) 和挂载 (`fs_mount`) 功能。
    *   提供设置 (`set_aivk_root`) 和获取 (`get_aivk_root`) AIVK 根目录的方法。
    *   支持读取 (`get_config`, `get_meta`) 和保存 (`save_config`, `save_meta`) TOML 格式的配置文件和元数据文件。
    *   在 `.aivk` 标记文件中添加和读取模块 ID (`add_module_id`, `get_module_ids`)。
*   **文件系统 (`AivkFS`)**:
    *   提供在 AIVK 根目录下获取和创建目录 (`dir`) 和文件 (`file`) 的基本方法。
    *   提供获取特定模块配置文件 (`config_file`) 和元数据文件 (`meta_file`) 路径的方法。
*   **命令行接口 (`cli`)**:
    *   实现 `aivk` 主命令。
    *   添加 `init` 子命令用于初始化 AIVK 根目录，支持 `--force` 和 `--path` 选项。
    *   添加 `mount` 子命令用于挂载 AIVK 根目录，支持 `--path` 和 `--interactive` (`-i`) 选项。
    *   添加 `shell` 子命令进入交互式 AIVK Shell。
    *   添加 `status` 子命令显示 AIVK 状态。
    *   添加 `mcp` 子命令启动 MCP 服务器，支持 `--transport` (stdio/sse), `--host`, `--port`, `--path`, `--save-config` 选项。
    *   添加 `help` 子命令显示帮助信息。
*   **交互式 Shell**:
    *   提供基本的交互式命令行环境。
    *   内置命令: `help`, `exit`, `clear`, `status`, `version`。
    *   文件系统命令: `ls`, `cd`, `pwd`, `cat`, `mkdir`。
    *   支持通过 `!` 前缀执行系统命令。
*   **MCP 服务器 (`mcp`)**:
    *   基于 `FastMCP` 实现，可通过 stdio 或 SSE 传输。
    *   提供 `aivk://status` 资源获取 AIVK 状态。
    *   提供 `aivk://root` 资源获取根目录路径。
    *   提供 `init_aivk_root_dir` 工具进行初始化。
    *   提供 `mount_aivk_root_dir` 工具进行挂载。
    *   提供 `ping` 工具测试连接。
    *   提供 `set_aivk_root_dir` 工具设置根目录。
    *   提供 `get_config`, `get_meta`, `get_module_ids` 工具访问配置、元数据和模块列表。
*   **工具类 (`utils.AivkExecuter`)**:
    *   提供同步 (`exec`) 和异步 (`aexec`) 执行系统命令的方法。
*   **构建与发布**:
    *   使用 `hatchling` 和 `uv` 进行构建。
    *   添加 GitHub Actions 工作流 (`python-publish.yml`) 用于自动发布到 PyPI。
    *   添加 `py.typed` 文件以支持类型检查。




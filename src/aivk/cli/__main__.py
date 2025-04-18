import asyncio
import click
import logging
from pathlib import Path
import sys
import os
from typing import TypeVar, Literal

from collections.abc import Callable
from collections.abc import Sequence

try:
    from ..__about__ import __version__, __github__ , __WELCOME__, __BYE__
    from ..base.aivkio import AivkIO
except ImportError:
    from aivk.__about__ import __version__, __github__, __WELCOME__, __BYE__
    from aivk.base.aivkio import AivkIO

logger = logging.getLogger("aivk.cli")

T = TypeVar('T')  # 定义泛型类型变量

# 定义可用的命令
COMMANDS: dict[str, Callable[..., bool | tuple[bool, Path | None]]] = {}
HELP_TEXT: dict[str, str] = {}
ALIASES: dict[str, str] = {}

def register_command(name: str, func: Callable[..., bool | tuple[bool, Path | None]], help_text: str, aliases: Sequence[str] | None = None) -> None:
    """注册一个命令到交互式界面"""
    COMMANDS[name] = func
    HELP_TEXT[name] = help_text
    if aliases:
        for alias in aliases:
            ALIASES[alias] = name

@click.group(name="aivk")
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
@click.version_option(version=__version__, prog_name="AIVK")
def cli(debug: bool) -> None:
    """AIVK CLI"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@cli.command(name="init")
@click.option("--force", "-f", is_flag=True, help="Force overwrite the existing aivk root directory")
@click.option("--path", "-p", help="Path to the aivk root directory")
def init(path: str | None, force: bool) -> None:
    """Initialize the AIVK root directory"""

    # 增加更多调试日志
    logger.debug(f"开始初始化 AIVK 根目录，参数: path={path}, force={force}")
    
    path_obj = Path(path) if path else None
    # 如果指定了路径，先设置到 AivkIO 中
    if path_obj and path_obj != AivkIO.get_aivk_root():
        original_path = AivkIO.get_aivk_root()
        logger.debug(f"设置 AIVK 根目录: {original_path} -> {path_obj.absolute()}")
        AivkIO.set_aivk_root(path_obj.absolute())
        logger.info(f" {original_path} —> {path_obj.absolute()}")
    
    # 显示当前设置的根目录
    logger.debug(f"当前 AIVK_ROOT = {AivkIO.get_aivk_root()}")
    
    # 使用 asyncio.run 来运行异步函数
    logger.debug(f"正在调用 AivkIO.fs_init(force={force})")
    _ = asyncio.run(AivkIO.fs_init(force=force))



@cli.command(name="mount")
@click.option("--path", "-p", help="Path to the aivk root directory")
@click.option("--interactive", "-i", is_flag=True, help="Enter interactive shell after mounting (default: True)")
def mount(path: str | None, interactive: bool) -> None:
    """Mount the AIVK root directory"""

    # 增加更多调试日志
    logger.debug(f"开始挂载 AIVK 根目录，参数: path={path}")
    
    path_obj = Path(path) if path else None
    # 如果指定了路径
    if path_obj and path_obj.absolute() != AivkIO.get_aivk_root():
        original_path = AivkIO.get_aivk_root()
        logger.debug(f"设置 AIVK 根目录: {original_path} -> {path_obj.absolute()}")
        AivkIO.set_aivk_root(path_obj.absolute())
        logger.info(f" {original_path} —> {path_obj.absolute()}")
    
    # 显示当前设置的根目录
    logger.debug(f"当前 AIVK_ROOT = {AivkIO.get_aivk_root()}")
    
    # 使用 asyncio.run 运行异步函数
    logger.debug("正在调用 AivkIO.fs_mount()")

    _ = asyncio.run(AivkIO.fs_mount())
    logger.info("You can use aivk mount -i / aivk shell to enter interactive shell")
    
    if interactive:
        # 进入交互式界面
        interactive_shell()

@cli.command(name="shell")
@click.option("--path", "-p", type=click.Path(), envvar="AIVK_ROOT", help="Path to the aivk root directory")
def shell(path: str | None) -> None:
    """Enter the interactive AIVK shell"""
    path_obj = Path(path) if path else None
    
    # 如果指定了路径，先设置到 GlobalVar 中
    if path_obj and path_obj != AivkIO.get_aivk_root():
        original_path = AivkIO.get_aivk_root()
        AivkIO.set_aivk_root(path_obj.absolute())
        logger.info(f" {original_path} —> {path_obj.absolute()}")
    
    if not AivkIO.is_aivk_root():
        logger.error("pls init AIVK_ROOT first  !")
        sys.exit(1)

    
    try:
        interactive_shell()  # 不再传递路径参数
    except Exception as e:
        logger.error(f"Failed to start interactive shell: {e}")
        sys.exit(1)


def interactive_shell():
    """
    AIVK 交互式命令行界面
    """
    # 从 AivkIO 获取根目录路径
    path = AivkIO.get_aivk_root()
    
    # 显示欢迎信息
    print(__WELCOME__)
    print(f"AIVK Shell v{__version__}")
    print(f"Root: {path}")
    print("Type 'help' for a list of commands, 'exit' to quit")
    
    # 注册内置命令
    register_command("help", cmd_help, "Show help for available commands", ["?", "h"])
    register_command("exit", cmd_exit, "Exit the AIVK shell", ["quit", "q"])
    register_command("clear", cmd_clear, "Clear the screen", ["cls"])
    register_command("status", cmd_status, "Show AIVK status", ["stat"])
    register_command("version", cmd_version, "Show AIVK version", ["ver"])
    
    # 注册文件系统命令
    register_command("ls", cmd_ls, "list files and directories", ["dir", "list"])
    register_command("cd", cmd_cd, "Change current directory", ["chdir"])
    register_command("pwd", cmd_pwd, "Print working directory", ["cwd"])
    register_command("cat", cmd_cat, "Display content of a file", ["type", "show"])
    register_command("mkdir", cmd_mkdir, "Create a new directory", ["md"])
    
    # 保存当前工作目录
    current_dir = path
    # 命令行循环
    running = True
    while running:
        try:
            # 显示提示符并获取用户输入
            user_input = input(f"AIVK [{current_dir.name}]> ")
            
            # 处理空输入
            if not user_input.strip():
                continue
                
            # 解析命令和参数
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            # 检查别名
            if cmd in ALIASES:
                cmd = ALIASES[cmd]
                
            # 执行命令
            if cmd in COMMANDS:
                # 传递当前目录作为参数，并获取可能更新的目录作为返回值
                result = COMMANDS[cmd](args, current_dir)
                if isinstance(result, tuple):
                    continue_flag, new_dir = result
                    if new_dir:
                        current_dir = new_dir
                    if not continue_flag:
                        running = False
                elif not result:
                    running = False
            else:
                # 尝试系统命令
                if cmd.startswith("!"):
                    os.system(user_input[1:])
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for a list of available commands")
        
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # 显示退出消息
    print(__BYE__)


# 交互式命令实现
def cmd_help(args: str, path: Path) -> bool:
    """显示帮助信息"""
    print("Available commands:")
    for name, help_text in sorted(HELP_TEXT.items()):
        print(f"  {name:12} - {help_text}")
    
    # 显示别名信息
    if ALIASES:
        print("\nAliases:")
        for alias, cmd in sorted(ALIASES.items()):
            print(f"  {alias:12} → {cmd}")
    
    print("\nYou can also run system commands by prefixing them with '!'")
    print("Example: !dir, !ls")
    return True


def cmd_exit(_args: str, _path: Path) -> bool:
    """退出交互式界面"""
    print("Exiting AIVK shell...")
    return False


def cmd_clear(_args: str, _path: Path) -> bool:
    """清屏"""
    _ = os.system('cls' if os.name == 'nt' else 'clear')
    return True


def cmd_status(_args: str, path: Path) -> bool:
    """显示AIVK状态"""
    print("AIVK Status:")
    print(f"  Version: {__version__}")
    print(f"  Root: {path}")
    print(f"  Initialized: {'Yes' if AivkIO.is_aivk_root() else 'No'}")
    
    # 读取配置文件获取更多信息
    try:
        dotaivk_file = path / ".aivk"
        if dotaivk_file.exists():
            import toml
            with open(dotaivk_file) as f:
                config = toml.load(f)
            
            # 使用类型注解解决 Any 类型警告
            metadata: dict[str, str] = config.get('metadata', {})
            print(f"  Created: {metadata.get('created', 'Unknown')}")
            print(f"  Updated: {metadata.get('updated', 'Unknown')}")
            if 'accessed' in metadata:
                print(f"  Last accessed: {metadata['accessed']}")
    except Exception as e:
        print(f"  Error reading config: {e}")
    
    return True


def cmd_version(_args: str, _path: Path) -> bool:
    """显示版本信息"""
    print(f"AIVK version: {__version__}")
    print(f"GitHub: {__github__}")
    return True


def cmd_ls(args: str, path: Path) -> bool:
    """列出文件和目录"""
    try:
        # 解析参数
        target_path = path
        if args:
            target_path = path / args if not args.startswith("/") else Path(args)
        
        if not target_path.exists():
            print(f"Path not found: {target_path}")
            return True
            
        # 获取文件和目录列表
        items = list(target_path.iterdir())
        
        # 分类并排序
        dirs = sorted([item for item in items if item.is_dir()], key=lambda x: x.name.lower())
        files = sorted([item for item in items if item.is_file()], key=lambda x: x.name.lower())
        
        # 显示目录
        if dirs:
            print("\nDirectories:")
            for d in dirs:
                print(f"  📁 {d.name}/")
        
        # 显示文件
        if files:
            print("\nFiles:")
            for f in files:
                size = f.stat().st_size
                size_str = f"{size} B"
                if size > 1024*1024:
                    size_str = f"{size/1024/1024:.1f} MB"
                elif size > 1024:
                    size_str = f"{size/1024:.1f} KB"
                print(f"  📄 {f.name:<30} {size_str:>10}")
        
        # 显示统计信息
        print(f"\nTotal: {len(dirs)} directories, {len(files)} files")
        
    except Exception as e:
        print(f"Error listing directory: {e}")
    return True


def cmd_cd(args: str, path: Path) -> tuple[bool, Path | None]:
    """更改当前目录"""
    try:
        # 处理特殊情况
        if not args or args == ".":
            return True, path
        
        if args == "..":
            return True, path.parent
        
        if args == "~" or args == "/":
            # 使用 AivkIO 获取根目录
            return True, AivkIO.get_aivk_root()
        
        # 尝试解析路径
        target = path / args if not args.startswith("/") else Path(args)
        
        if target.is_dir():
            print(f"Changed directory to: {target}")
            return True, target.resolve()
        else:
            print(f"Not a directory: {args}")
    except Exception as e:
        print(f"Error changing directory: {e}")
    return True, None


def cmd_pwd(_args: str, path: Path) -> bool:
    """打印工作目录"""
    print(f"Current directory: {path.resolve()}")
    return True


def cmd_cat(args: str, path: Path) -> bool:
    """显示文件内容"""
    if not args:
        print("Error: No file specified")
        print("Usage: cat <filename>")
        return True
        
    try:
        # 解析文件路径
        file_path = path / args if not args.startswith("/") else Path(args)
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return True
            
        if file_path.is_dir():
            print(f"Error: '{args}' is a directory")
            return True
            
        # 检查文件大小
        size = file_path.stat().st_size
        if size > 1024*1024:  # 大于1MB的文件警告
            response = input(f"Warning: File is large ({size/1024/1024:.1f} MB). Display anyway? (y/N): ")
            if response.lower() != 'y':
                return True
        
        # 读取文件内容
        with open(file_path, errors="replace") as f:
            content = f.read()
            
        # 显示文件内容
        print(f"\n--- Content of {file_path.name} ---\n")
        print(content)
        print(f"\n--- End of {file_path.name} ---\n")
        
    except UnicodeDecodeError:
        print(f"Error: Cannot display binary file '{args}'")
    except Exception as e:
        print(f"Error reading file: {e}")
    return True


def cmd_mkdir(args: str, path: Path) -> bool:
    """创建新目录"""
    if not args:
        print("Error: No directory name specified")
        print("Usage: mkdir <dirname>")
        return True
        
    try:
        # 解析目录路径
        dir_path = path / args if not args.startswith("/") else Path(args)
        
        if dir_path.exists():
            print(f"Directory already exists: {dir_path}")
            return True
            
        # 创建目录
        dir_path.mkdir(parents=True)
        print(f"Directory created: {dir_path}")
        
    except Exception as e:
        print(f"Error creating directory: {e}")
    return True


@cli.command(name="status")
def status():
    """Show the status of AIVK"""
    logger.info("Checking AIVK status...")
    # 检查是否初始化，使用 AivkIO 获取根目录和检查初始化状态
    root_path = AivkIO.get_aivk_root()
    initialized = AivkIO.is_aivk_root()
    
    if initialized:
        logger.info(f"AIVK is initialized at: {root_path}")
        # TODO: 添加更多状态检查
    else:
        logger.warning("AIVK is not initialized. Use 'aivk init' to initialize.")


@cli.command(name="mcp")
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio", help="Transport method for MCP")
@click.option("--host", default=None, help="Host for aivk MCP server (default: localhost)")
@click.option("--port", default=None, type=int, help="Port for aivk MCP server (default: 10140)")
@click.option("--path", "-p", type=click.Path(), envvar="AIVK_ROOT", help="Path to the aivk root directory")
@click.option("--save-config", is_flag=True, help="Save host and port to config file")
def mcp(transport: Literal["stdio", "sse"], host: str | None, port: int | None, path: str, save_config: bool) -> None:
    """MCP command to handle transport methods."""
    # 如果提供了路径，设置 AIVK 根目录
    if path:
        path_obj = Path(path)
        AivkIO.set_aivk_root(path_obj)
        logger.info(f"使用指定的 AIVK 根目录: {path_obj}")
    
    # 确保 AIVK 根目录已初始化
    root_path = AivkIO.get_aivk_root()
    if not AivkIO.is_aivk_root():
        logger.warning(f"AIVK 根目录 {root_path} 未初始化。尝试挂载...")
        try:
            asyncio.run(AivkIO.fs_mount())
        except Exception as e:
            logger.error(f"挂载 AIVK 根目录失败: {e}")
            sys.exit(1)
    
    # 设置默认值
    host_value = "localhost" if host is None else host
    port_value = 10140 if port is None else port
    
    # 如果需要保存配置
    if save_config:
        # 获取 AIVK 根目录路径
        config_path = root_path / "etc" / "aivk" / "config.toml"
        
        # 确保目录存在
        _ = config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建或更新配置
        import toml
        try:
            if config_path.exists():
                config = toml.load(config_path)
            else:
                config = {}
                
            config["host"] = host_value
            config["port"] = port_value
            
            with open(config_path, 'w') as f:
                _ = toml.dump(config, f)
                
            logger.info(f"配置已保存至: {config_path}")
            logger.info(f"配置详情: host={host_value}, port={port_value}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    print(f"Transport: {transport}, Host: {host_value}, Port: {port_value}")
    print(f"AIVK 根目录: {root_path}")
    
    # 导入 mcp 模块 (server.py)
    from ..mcp.server import mcp
    
    if transport == "stdio":
        logger.info("正在启动 MCP (stdio transport)...")
    elif transport == "sse":
        logger.info(f"正在启动 MCP (SSE transport) on {host_value}:{port_value}...")
        
    # 运行 MCP 服务器
    mcp.run(transport=transport)

@cli.command(name="help")
@click.argument("command_name", required=False, type=str)
def help_cmd(command_name: str | None) -> None:
    """Show help information for commands
    
    If COMMAND_NAME is provided, show detailed help for that command.
    Otherwise, show general help information.
    """
    ctx = click.get_current_context()
    if command_name:
        # 查找指定命令
        command = cli.get_command(ctx, command_name)
        if command:
            # 显示特定命令的帮助信息
            click.echo(command.get_help(ctx))
        else:
            click.echo(f"Unknown command: {command_name}")
            sys.exit(1)
    else:
        # 显示通用帮助信息
        click.echo(cli.get_help(ctx))


if __name__ == "__main__":
    cli()
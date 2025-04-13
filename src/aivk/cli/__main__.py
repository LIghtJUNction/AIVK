import asyncio
import click
import logging
from pathlib import Path
import sys
import os
from typing import Optional

try:
    from ..base.models import GlobalVar
    from ..__about__ import __version__, __github__ , __WELCOME__, __BYE__
    from ..base import fs
except ImportError:
    from aivk.__about__ import __version__, __github__, __WELCOME__, __BYE__
    from aivk.base import fs
    from aivk.base.models import GlobalVar

logger = logging.getLogger("aivk.cli")

# 定义可用的命令
COMMANDS = {}
HELP_TEXT = {}
ALIASES = {}

def register_command(name, func, help_text, aliases=None):
    """注册一个命令到交互式界面"""
    COMMANDS[name] = func
    HELP_TEXT[name] = help_text
    if aliases:
        for alias in aliases:
            ALIASES[alias] = name

@click.group(name="aivk")
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
@click.version_option(version=__version__, prog_name="AIVK")
def cli(debug):
    """AIVK CLI"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@cli.command(name="init")
@click.option("--force", "-f", is_flag=True, help="Force overwrite the existing aivk root directory")
@click.option("--path", "-p", type=click.Path(writable=True), envvar="AIVK_ROOT", help="Path to the aivk root directory")
def init(path, force):
    """Initialize the AIVK root directory"""
    try:
        path_obj = Path(path) if path else None
        result = asyncio.run(fs.initialize(path=path_obj, force=force))
        logger.info(f"Successfully initialized AIVK at {result}")
    except FileExistsError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to initialize AIVK: {e}")
        sys.exit(1)


@cli.command(name="mount")
@click.option("--path", "-p", type=click.Path(), envvar="AIVK_ROOT", help="Path to the aivk root directory")
@click.option("--interactive", "-i", is_flag=True, default=True, help="Enter interactive shell after mounting (default: True)")
@click.option("--no-interactive", "-n", is_flag=True, help="Do not enter interactive shell after mounting")
def mount(path, interactive, no_interactive):
    """Mount the AIVK root directory"""
    try:
        path_obj = Path(path) if path else None
        result = asyncio.run(fs.mount(path=path_obj))
        if result:
            logger.info("Successfully mounted AIVK")
            # 如果明确指定了 no_interactive，则不进入交互界面
            if no_interactive:
                interactive = False
            if interactive:
                # 进入交互式界面
                interactive_shell(path_obj)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to mount AIVK: {e}")
        sys.exit(1)


@cli.command(name="shell")
@click.option("--path", "-p", type=click.Path(), envvar="AIVK_ROOT", help="Path to the aivk root directory")
def shell(path):
    """Enter the interactive AIVK shell"""
    path_obj = Path(path) if path else None
    
    # 检查是否已挂载，如果没有则先挂载
    if not fs.is_initialized(path_obj):
        logger.warning("AIVK is not initialized. Please run 'aivk init' first.")
        sys.exit(1)
    
    try:
        # 先确保挂载
        asyncio.run(fs.mount(path=path_obj))
        # 然后进入交互式界面
        interactive_shell(path_obj)
    except Exception as e:
        logger.error(f"Failed to start interactive shell: {e}")
        sys.exit(1)


def interactive_shell(path: Optional[Path] = None):
    """
    AIVK 交互式命令行界面
    
    Args:
        path: AIVK 根目录路径
    """
    # 确保路径存在
    path = path if path else fs.get_root_path()
    
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
    register_command("ls", cmd_ls, "List files and directories", ["dir", "list"])
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
def cmd_help(args, path):
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


def cmd_exit(args, path):
    """退出交互式界面"""
    print("Exiting AIVK shell...")
    return False


def cmd_clear(args, path):
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')
    return True


def cmd_status(args, path):
    """显示AIVK状态"""
    print("AIVK Status:")
    print(f"  Version: {__version__}")
    print(f"  Root: {path}")
    print(f"  Initialized: {fs.is_initialized(path)}")
    
    # 读取配置文件获取更多信息
    try:
        dotaivk_file = path / ".aivk"
        if dotaivk_file.exists():
            import toml
            with open(dotaivk_file, "r") as f:
                config = toml.load(f)
            
            print(f"  Created: {config['metadata'].get('created', 'Unknown')}")
            print(f"  Updated: {config['metadata'].get('updated', 'Unknown')}")
            if 'accessed' in config['metadata']:
                print(f"  Last accessed: {config['metadata']['accessed']}")
    except Exception as e:
        print(f"  Error reading config: {e}")
    
    return True


def cmd_version(args, path):
    """显示版本信息"""
    print(f"AIVK version: {__version__}")
    print(f"GitHub: {__github__}")
    return True


def cmd_ls(args, path):
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


def cmd_cd(args, path):
    """更改当前目录"""
    try:
        # 处理特殊情况
        if not args or args == ".":
            return True, path
        
        if args == "..":
            return True, path.parent
        
        if args == "~" or args == "/":
            return True, fs.get_root_path()
        
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


def cmd_pwd(args, path):
    """打印工作目录"""
    print(f"Current directory: {path.resolve()}")
    return True


def cmd_cat(args, path):
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
        with open(file_path, "r", errors="replace") as f:
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


def cmd_mkdir(args, path):
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
    # 检查是否初始化
    root_path = fs.get_root_path()
    initialized = fs.is_initialized(root_path)
    
    if initialized:
        logger.info(f"AIVK is initialized at: {root_path}")
        # TODO: 添加更多状态检查
    else:
        logger.warning("AIVK is not initialized. Use 'aivk init' to initialize.")


@cli.command(name="mcp")
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="stdio", help="Transport method for MCP")
@click.option("--host", default=None, help="Host for aivk MCP server (default: localhost)")
@click.option("--port", default=None, type=int, help="Port for aivk MCP server (default: 10140)")
@click.option("--save-config", is_flag=True, help="Save host and port to config file")
def mcp(transport: str, host: str, port: int, save_config: bool):
    """MCP command to handle transport methods."""
    # 首先尝试从参数获取值，如果没有提供则使用配置系统
    if host is not None:
        GlobalVar.set("host", host)
    else:
        host = GlobalVar.get_host()
        
    if port is not None:
        GlobalVar.set("port", port)
    else:
        port = GlobalVar.get_port()
    
    # 如果需要保存配置
    if save_config:
        # 获取 AIVK 根目录路径
        root_path = fs.get_root_path()
        config_path = root_path / "etc" / "aivk" / "config.toml"
        
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 更新配置并保存
        config = GlobalVar.get_config()
        config.host = host
        config.port = port
        GlobalVar.save_config(config_path)
        logger.info(f"配置已保存至: {config_path}")
        logger.info(f"配置详情: host={host}, port={port}")
    
    print(f"Transport: {transport}, Host: {host}, Port: {port}")
    
    # 导入 mcp 模块 (server.py)
    from ..mcp.server import mcp
    
    if transport == "stdio":
        logger.info(f"正在启动 MCP (stdio transport)...")
    elif transport == "sse":
        logger.info(f"正在启动 MCP (SSE transport) on {host}:{port}...")
        
    # 运行 MCP 服务器
    mcp.run(transport=transport)

@cli.command(name="help")
@click.argument("command_name", required=False)
def help_cmd(command_name):
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
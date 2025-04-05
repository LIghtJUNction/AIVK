import asyncio
from pathlib import Path
from rich.console import Console
try:
    from ..aivk import Entry
except ImportError:
    from aivk.aivk import Entry

async def init(aivk_root: Path | str) -> None:
    """
    初始化一个空目录作为AIVK的根目录
    """
    
    Entry.onInstall(aivk_root)

async def remove(aivk_root: Path | str) -> None:
    """
    移除AIVK的根目录
    """

    Entry.onUninstall(aivk_root)

async def update() -> None:
    """
    更新AIVK 元模块
    """

    Entry.onUpdate()

ASCII_AIVK_LOGO = r"""


     _      ___  __     __  _  __
    / \    |_ _| \ \   / / | |/ /
   / _ \    | |   \ \ / /  | ' / 
  / ___ \   | |    \ V /   | . \  
 /_/   \_\ |___|    \_/    |_|\_\
                                 
                           
 
"""

async def menu() -> None:
    """
    显示AIVK的菜单
    """
    console.print(ASCII_AIVK_LOGO, style="bold white")


async def main() -> None:
    """
    主函数
    """
    console = Console()
    # 参数解析
    # 
    # --init <path>  初始化一个空目录作为AIVK的根目录
    # --mount <path>  挂载AIVK的根目录
    # --remove <path>  移除AIVK的根目录
    # --help 显示帮助信息
    # --version 显示版本信息

    import argparse
    parser = argparse.ArgumentParser(description="AIVK - AI Virtual Kernel")

    parser.add_argument('--help', action='help', help='显示帮助信息')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0', help='显示版本信息')
    parser.add_argument('--init', type=str, help='初始化一个空目录作为AIVK的根目录')
    parser.add_argument('--mount', type=str, help='挂载AIVK的根目录')
    parser.add_argument('--remove', type=str, help='移除AIVK的根目录')
    args = parser.parse_args()

    if args.init:
        # 初始化一个空目录作为AIVK的根目录
        aivk_root = Path(args.init)
        await init(aivk_root)
        console.print(f"Initialized AIVK at {aivk_root}", style="bold green")
    
    elif args.remove:

        aivk_root = Path(args.remove)
        await remove(aivk_root)
        console.print(f"Removed AIVK at {aivk_root}", style="bold red")
    
    elif args.mount:

        aivk_root = Path(args.mount)
        console.print(f"Mounted AIVK at {aivk_root}", style="bold blue")
    
    elif args.version:
        # 显示版本信息
        from aivk import __version__, __author__
        console.print(f"{__version__} by {__author__}", style="bold white")

    elif args.help:
        # 显示帮助信息
        parser.print_help()
        console.print("Use --init, --remove, or --mount to manage AIVK.", style="bold yellow")
        
    else:
        console.print("No valid arguments provided. Use --init, --remove, or --mount.", style="bold yellow")
        # 无参数时显示菜单
        await menu()


asyncio.run(main())
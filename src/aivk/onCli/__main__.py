"""AIVK CLI 入口模块

提供命令行接口的入口点和主要命令实现。
"""
import asyncio
import logging
import click
from anytree import RenderTree
from click import Context # Import Context
from typing import Optional # Import Optional

try:
    from ..logger import setup_logging
    from ..__about__ import __LOGO__
    from ..base.cli import AivkCLI
except ImportError:
    from aivk.logger import setup_logging
    from aivk.__about__ import __LOGO__
    from aivk.base.cli import AivkCLI


setup_logging(
    style="error",
    theme="dark",        # 使用深色主题
    icons="emoji",       # 使用emoji图标，更直观
    level=logging.INFO,  # 默认INFO级别
    show_time=True,     # 显示时间戳
    show_path=True      # 显示文件路径，方便调试
)

logger = logging.getLogger("aivk.cli.entry")

logger.info(__LOGO__)

# 先定义命令组函数
@click.group(cls=AivkCLI.AivkGroup, name="aivk", invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """AIVK CLI 命令行入口"""
    # 如果没有子命令被调用，则显示帮助信息
    if ctx.invoked_subcommand is None:
        logger.info("显示帮助信息:")
        logger.info(ctx.get_help())

aivk = AivkCLI(id="aivk")
aivk.cli_parent = None # 更新字段名为 cli_parent
aivk.cli = cli  # 明确设置cli属性

@cli.command()
@click.option("--path","-p", help="Aivk Root Path", default="~/.aivk")
def load(path: str):
    """加载命令"""
    load = aivk.on("load", "aivk")
    kwargs = {
        "path": path
    }
    asyncio.run(load(**kwargs))

@cli.command()
@click.option("--path","-p", help="Aivk Root Path", default="~/.aivk")
def unload(path: str):
    """取消挂载命令"""
    unload = aivk.on("unload", "aivk")
    kwargs = {
        "path": path
    }
    asyncio.run(unload(**kwargs))

@cli.command()
@click.argument("id")
def install(id: str):
    """安装命令"""
    install = aivk.on("install", "aivk")
    kwargs = {
        "id": id
    }
    asyncio.run(install(**kwargs))

@cli.command()
@click.argument("id")
def uninstall(id: str):
    """卸载命令"""
    uninstall = aivk.on("uninstall", "aivk")
    kwargs = {
        "id": id
    }
    asyncio.run(uninstall(**kwargs))

@cli.command()
def list():
    """列出已安装的模块"""
    list = aivk.on("list", "aivk")
    asyncio.run(list())

@cli.command()
def update():
    """更新命令"""
    update = aivk.on("update", "aivk")
    asyncio.run(update())

@cli.command()
@click.argument('command', required=False) # 添加可选参数 command
@click.pass_context
def help(ctx: Context, command: Optional[str]): # 接收 command 参数
    """显示帮助信息"""
    logger.info("显示树形结构:")
    # Ensure aivk is the root node for RenderTree if needed
    # You might need to adjust how 'aivk' is passed or accessed if it's not directly available
    # Assuming 'aivk' is the root AivkCLI instance accessible here
    print(RenderTree(aivk)) # Keep the tree rendering

    if command: # 如果提供了 command 参数
        # 从父级上下文（主 cli group）获取命令对象
        cmd_obj = cli.get_command(ctx, command)
        if cmd_obj:
            logger.info(f"显示命令 '{command}' 的帮助信息:")
            # 使用 Click 的方式打印子命令的帮助信息
            click.echo(cmd_obj.get_help(ctx))
        else:
            logger.error(f"未找到命令: {command}")
            ctx.exit(1) # Indicate error
    else:
        # 如果没有提供 command 参数，显示主帮助信息
        logger.info("显示主要帮助信息:")
        click.echo(ctx.parent.get_help()) # Use ctx.parent to get help for the main group

if __name__ == "__main__":
    pass
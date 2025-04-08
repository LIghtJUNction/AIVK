"""AIVK CLI 入口模块

提供命令行接口的入口点和主要命令实现。
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import click
from functools import wraps

try:
    from ..logger import setup_logging
    from ..__about__ import __LOGO__
    from ..base.utils import aivk_on
except ImportError:
    from aivk.logger import setup_logging
    from aivk.__about__ import __LOGO__
    from aivk.base.utils import aivk_on

def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

# 设置日志
setup_logging(style="error", theme="colorful", icons="blocks", level=logging.DEBUG)
logger = logging.getLogger("aivk.cli")

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)

@click.group(name="aivk", context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """AIVK - ai virtual kernel
获取帮助:
  aivk --help
  aivk help <command>
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
    else:
        logger.info("AIVK CLI is running...")

@cli.command()
@click.argument("id", default="fs")
@coro
async def install(id: str):
    """安装指定的 AIVK 模块

参数:
    MODULE_ID  要安装的模块 ID，默认为 fs (文件系统模块)

示例:
    aivk install fs      安装文件系统模块
    aivk install ai      安装 AI 功能模块
    aivk install webui   安装 Web 界面模块
    """
    kwargs = {
        "id": id,
    }

    await aivk_on("install","aivk",**kwargs)


@cli.command()
@click.argument("id", default="fs")
@coro
async def update(id: str, **kwargs):
    """更新指定的 AIVK 模块

参数:
    MODULEID  要更新的模块 ID，默认为 fs (文件系统模块)

示例:
    aivk update fs      更新文件系统模块
    aivk update ai      更新 AI 功能模块
    aivk update webui   更新 Web 界面模块
    """
    kwargs = {
        "id": id,
    }
    await aivk_on("update", "aivk", **kwargs)


@cli.command()
@click.argument("id", default="fs")
@coro
async def uninstall(id : str):
    """卸载指定的 AIVK 模块

参数:
    MODULEID  要卸载的模块 ID，默认为 fs (文件系统模块)

示例:
    aivk uninstall fs      卸载文件系统模块
    aivk uninstall ai      卸载 AI 功能模块
    aivk uninstall webui   卸载 Web 界面模块
    """
    kwargs = {
        "id" : id
    }
    await aivk_on("uninstall", "aivk", **kwargs)


@cli.command()
@click.option("-p", "--path", 
            help="AIVK 根目录路径，默认为 ~/.aivk",
            type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
@click.option("-m", "--id",
            help="要加载的模块 ID，默认为所有模块",
            default=None,
            type=str)
@coro
async def load(path: Optional[str] = "", id: Optional[str] = "", **kwargs):
    """加载 AIVK 框架与模块

选项:
    -p, --path PATH     指定 AIVK 根目录路径
    -m, --id ID        指定要加载的模块 ID

配置查找顺序:
    1. 命令行参数指定的路径
    2. 环境变量 AIVK_ROOT
    3. 默认路径 ~/.aivk

示例:
    aivk load                       使用默认路径加载所有模块
    aivk load -p /path/to/aivk     使用指定路径加载所有模块
    aivk load -m fs                只加载文件系统模块
    aivk load -p /path -m fs       使用指定路径加载指定模块
    """
    kwargs = {}
    if path:
        kwargs["path"] = path
    if id:
        kwargs["module_id"] = id  # 使用 module_id 而不是 id 作为参数名
        
    await aivk_on("load", "aivk", **kwargs)


@cli.command()
@click.option("-p", "--path",
            help="AIVK 根目录路径，默认为 ~/.aivk",
            type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
@coro
async def unload(path: Optional[str] = ""):
    """卸载 AIVK 框架与已加载的模块

选项:
    -p, --path PATH  指定 AIVK 根目录路径

配置查找顺序:
    1. 命令行参数指定的路径
    2. 环境变量 AIVK_ROOT
    3. 默认路径 ~/.aivk

示例:
    aivk unload                    卸载默认路径的框架
    aivk unload -p /path/to/aivk   卸载指定路径的框架
    """
    kwargs = {
        "path": path,
    }

    await aivk_on("unload", "aivk" , **kwargs)


@cli.command()
@click.option("-p", "--path",
            help="AIVK 根目录路径，默认为 ~/.aivk",
            type=click.Path(file_okay=False, dir_okay=True, path_type=Path))
@coro
async def list(path: Optional[str] = ""):
    """列出 AIVK 模块

不带路径参数时，列出全局已安装的 AIVK PyPI 包。
带路径参数时，列出指定路径下的本地模块配置。

选项:
    -p, --path PATH  指定 AIVK 根目录路径，用于查看本地模块配置
    
配置查找顺序:
    1. 命令行参数指定的路径
    2. 环境变量 AIVK_ROOT
    3. 默认路径 ~/.aivk
    
示例:
    aivk list                    列出全局已安装的 AIVK PyPI 包
    aivk list -p /path/to/aivk   列出指定路径下的本地模块配置
    """
    
    kwargs = {
        "path": path,
    }
    await aivk_on("list", "aivk" , **kwargs)


@cli.command()
@coro
async def version(**kwargs):
    """显示 AIVK 版本信息与相关详情
显示内容:
    - 版本号
    - 作者信息
    - 源码仓库地址

示例:
    aivk version   显示版本信息
    """
    from ..__about__ import __version__, __author__, __email__, __github__
    click.echo(f"AIVK Version: {__version__}")
    click.echo(f"Author: {__author__} <{__email__}>")
    click.echo(f"GitHub: {__github__}")

@cli.command()
@click.argument('command', required=False)
@click.pass_context
@coro
async def help(ctx, command):
    """显示命令帮助信息

参数:
    COMMAND  要查看帮助的命令名称

示例:
    aivk help           显示通用帮助
    aivk help install   显示 install 命令帮助
    aivk help update    显示 update 命令帮助
    """
    if command:
        # 在命令组中查找指定的命令
        cmd = cli.get_command(ctx, command)
        if cmd:
            # 创建一个新的上下文来显示命令帮助
            with click.Context(cmd, info_name=command, parent=ctx) as cmd_ctx:
                click.echo(cmd.get_help(cmd_ctx))
        else:
            click.echo(f'错误: 命令 "{command}" 不存在')
    else:
        # 显示通用帮助
        click.echo(ctx.parent.get_help() if ctx.parent else ctx.get_help())

@coro
def main():
    """AIVK CLI 入口点函数"""
    return cli()


if __name__ == "__main__":
    main()
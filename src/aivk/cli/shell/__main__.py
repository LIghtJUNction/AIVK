import asyncio
from sys import platform
import subprocess
from click import command
from logging import getLogger

from ...api import AivkContext

logger = getLogger("aivk.cli.shell")

@command()
def shell():
    """
    AIVK Shell CLI -- 待完善
    """

    aivk_ctx = AivkContext.getContext()
    
    async def enter_shell():
        async with aivk_ctx.env(id="aivk", create_venv=True) as fs:
            logger.debug("已进入 AIVK 虚拟环境，启动 shell ...")
            logger.info("安装aivk 模块：'uv pip install aivk_web'")
            logger.info("进入aivk 虚拟环境：./aivk_venv/Scripts/activate" if platform == "win32" else "source ./aivk_venv/bin/activate")

            match platform:
                case "win32":
                    shell_cmd = [
                        "wt",
                        "-d", str(fs.home),  # -d 是 --startingDirectory 的简写
                        "--title", "AIVK Shell"
                    ]
                case "darwin":
                    shell_cmd = [
                        "open", "-a", "Terminal", str(fs.home)
                    ]
                case "linux":
                    shell_cmd = [
                        "konsole", "--workdir", str(fs.home)
                    ]
                case _:
                    logger.error(f"不支持的操作系统: {platform}")
                    return
            subprocess.Popen(shell_cmd,env=fs.env)
    asyncio.run(enter_shell())


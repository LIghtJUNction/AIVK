import asyncio
import os
import subprocess
from click import command
from logging import getLogger
from pathlib import Path

from ...api import AivkContext

logger = getLogger("aivk.cli.shell")

@command()
def shell():
    """
    AIVK Shell CLI
    进入/激活 aivk 虚拟环境并启动交互式 shell
    """

    aivk_ctx = AivkContext.getContext()
    
    
    def get_default_shell_command():
        if os.name == "nt":
            for shell in ["pwsh.exe", "powershell.exe", "cmd.exe"]:
                if any((Path(path) / shell).exists() for path in os.environ["PATH"].split(os.pathsep)):
                    return shell
            return "cmd.exe"
        else:
            # Linux/macOS: 优先 $SHELL，否则常见终端
            shell = os.environ.get("SHELL")
            if shell and Path(shell).exists():
                return shell
            for term in ["bash", "zsh", "fish", "sh"]:
                if any((Path(path) / term).exists() for path in os.environ["PATH"].split(os.pathsep)):
                    return term
            return "/bin/sh"
    
    async def enter_shell():
        async with aivk_ctx.env(id="aivk", create_venv=True):
            logger.debug("已进入 AIVK 虚拟环境，启动 shell ...")
            logger.info("安装aivk 模块：'uv pip install aivk_web'")
            shell_cmd = get_default_shell_command()
            subprocess.Popen([shell_cmd], creationflags=subprocess.CREATE_NEW_CONSOLE)
    asyncio.run(enter_shell())


import asyncio
from typing import Literal, Self
from mcp.server.fastmcp import FastMCP
from aivk.base.fs import AivkFS
from click import command, option
from logging import getLogger
logger = getLogger("aivk.amcp")

class AivkMCPMeta(type):
    """
    AIVK MCP 元类
    """
    @property
    def fs(cls) -> AivkFS:
        """
        获取 AIVK 文件系统实例
        """
        return AivkFS.getFS()
    
class AivkMCP(FastMCP,metaclass=AivkMCPMeta):
    """
    AIVK MCP 类
    """

    @classmethod
    def initMCP(cls) -> Self:
        """
        初始化 AIVK MCP
        """
        cls._instance = cls.getMCP()
        
        @cls._instance.tool()
        def getHOME(): # type: ignore
            """
            获取 mcp服务器主目录
            """
            return AivkFS.getFS("mcp").home
        
        return cls._instance

    @classmethod
    def getMCP(cls) -> Self:
        """
        获取 AIVK MCP 实例
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls("name")

        return cls._instance

    @classmethod
    def stdio(cls):
        """
        启动 MCP stdio 模式
        """
        asyncio.run(cls.initMCP().run_stdio_async())

    @classmethod
    def sse(cls, host: str = "localhost", port: int = 10140  ):
        """
        启动 MCP SSE 模式
        """
        cls._instance = cls.initMCP()
        cls._instance.settings.host = host
        cls._instance.settings.port = port
        asyncio.run(cls._instance.run_sse_async())

# MCP DEV 入口
def __getattr__(name: str) -> AivkMCP | None:
    """
    获取 AIVK MCP 实例
    """
    if name == "mcp": # mcp dev
        return AivkMCP.initMCP()
    
    elif name == "stdio":
        AivkMCP.stdio()

    elif name == "sse":
        AivkMCP.sse() # 以默认值启动

    raise AttributeError(" 禁止访问 ")


@command("mcp", help="启动 AIVK MCP 服务")
@option("--host","-h", default="localhost", help="MCP 服务主机地址")
@option("--port","-p", default=10140, help="MCP 服务端口")
@option("--stdio","transport", flag_value="stdio", default=True, help="以 stdio 模式启动 MCP")
@option("--sse","transport", flag_value="sse", help="以 SSE 模式启动 MCP")
def aivk_mcp(host: str, port: int, transport: Literal["stdio", "sse"]):
    """
    启动 AIVK MCP
    """
    logger.info(f"启动 AIVK MCP 服务，模式: {transport}, 地址: {host}:{port}")
    if transport == "stdio":
        AivkMCP.stdio()
    elif transport == "sse":
        AivkMCP.sse(host=host, port=port)
    

__all__ = ["aivk_mcp", "AivkMCP"]
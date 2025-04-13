from mcp.server.fastmcp import FastMCP
from datetime import datetime

try:
    from ..base.models import GlobalVar
except ImportError:
    from aivk.base.models import GlobalVar

port = GlobalVar.get_port()
host = GlobalVar.get_host()

# 创建 FastMCP 实例
mcp = FastMCP(
    name="aivk", 
    instructions="aivk mcp server", 
    port=port,
    host=host
)

@mcp.resource("aivk://status", mime_type = "text/plain")
def status():
    """返回 AIVK 状态信息"""
    return {
        "status": "running",
        "host": host,
        "port": port,
        "server_name": "aivk-mcp"
    }


@mcp.resource("aivk://time" , mime_type="text/plain")
def time():
    """返回当前时间"""
    return {
        "current_time": datetime.now().isoformat()
    }

@mcp.resource("aivk://root", mime_type="text/plain")
def root():
    """返回 AIVK 根目录"""
    return {
        "aivk_root": str(GlobalVar.get_aivk_root())
    }

@mcp.tool(name="ping", instructions="send ping response", mime_type="text/plain")
def ping():
    """返回 AIVK ping 响应信息"""
    return "pong!"


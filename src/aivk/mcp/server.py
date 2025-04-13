import asyncio
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from datetime import datetime

try:
    from ..base.fs import AivkFS
    from ..base.models import GlobalVar
except ImportError:
    from aivk.base.fs import AivkFS
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
    """返回 AIVK 状态信息
    查看现在是否已经初始化aivk root dir
    """
    root: Path = GlobalVar.get_aivk_root()
    if AivkFS.is_initialized(root):
        return {
            "status": "AIVK is initialized",
            "aivk_root": str(root),
            }
    else:
        return {
            "status": f"AIVK is not initialized ! :{str(root)}",  
        }
    


    
@mcp.tool(name="init aivk root dir", instructions="initialize aivk root dir", mime_type="text/plain")
def init_aivk_root_dir(path: str ):
    """初始化 AIVK 根目录
    path: str, AIVK 根目录路径
    """
    #  为了安全起见， 不允许AI使用强制模式，以免删除重要文件
    root = Path(path)
        
    # 记录初始化步骤
    steps = []
    steps.append(f"1. 设置 AIVK 根目录: {path}")
    
    # 设置全局变量
    GlobalVar.set_aivk_root(root)
    steps.append(f"2. 已更新全局变量 AIVK_ROOT: {path}")
    
    try:
        # 执行初始化过程
        asyncio.run(AivkFS.initialize(root, force=False))
        steps.append("3. 创建了以下基本目录结构:")
        steps.append(f"   - {path}/cache (缓存目录)")
        steps.append(f"   - {path}/tmp (临时目录)")
        steps.append(f"   - {path}/data (数据目录)")
        steps.append(f"   - {path}/etc (配置目录)")
        steps.append(f"   - {path}/home (主目录)")
        steps.append(f"   - {path}/etc/aivk (AIVK配置目录)")
        steps.append(f"4. 创建了以下配置文件:")
        steps.append(f"   - {path}/.aivk (根标记文件，包含版本、创建时间等元数据)")
        steps.append(f"   - {path}/etc/mcp.toml (MCP服务器配置)")
        steps.append(f"   - {path}/etc/aivk/meta.toml (AIVK元数据配置)")
        steps.append(f"5. 初始化了uv项目环境")
        steps.append(f"   - 创建了pyproject.toml和README.md")
        steps.append(f"   - 执行了uv sync命令同步环境")
        
    except Exception as e:
        return f"初始化失败: {str(e)}\n已执行的步骤:\n" + "\n".join(steps)

    # 返回详细的初始化信息
    return f"AIVK根目录初始化成功！\n\n初始化过程详情:\n" + "\n".join(steps)

@mcp.tool(name="mount aivk root dir", instructions="mount aivk root dir", mime_type="text/plain")
def mount_aivk_root_dir(path: str = None):
    """挂载 AIVK 根目录
    path: str, AIVK 根目录路径
    """
    # 记录挂载步骤
    steps = []
    
    try:
        # 使用提供的路径或默认路径
        if path:
            root_path = Path(path)
            steps.append(f"1. 使用指定路径: {path}")
        else:
            root_path = Path.home() / ".aivk"
            steps.append(f"1. 使用默认路径: {root_path}")
        
        # 检查路径是否存在
        if not root_path.exists():
            steps.append(f"错误: 路径 {root_path} 不存在，无法挂载")
            return "\n".join(steps)
        
        steps.append(f"2. 验证路径存在: {root_path}")
        
        # 检查.aivk标记文件
        dotaivk_file = root_path / ".aivk"
        if not dotaivk_file.exists():
            steps.append(f"错误: {root_path} 不是有效的AIVK根目录，缺少.aivk标记文件")
            return "\n".join(steps)
        
        steps.append(f"3. 验证.aivk标记文件存在")
        
        # 执行挂载
        asyncio.run(AivkFS.mount(path))
        
        # 读取配置文件，显示更多信息
        try:
            import toml
            with open(dotaivk_file, "r") as f:
                config = toml.load(f)
            
            meta = config.get("metadata", {})
            steps.append(f"4. 读取.aivk配置文件:")
            steps.append(f"   - 创建时间: {meta.get('created', '未知')}")
            steps.append(f"   - 更新时间: {meta.get('updated', '未知')}")
            steps.append(f"   - AIVK版本: {meta.get('version', '未知')}")
        except Exception as e:
            steps.append(f"4. 无法读取配置文件: {str(e)}")
        
        # 更新全局变量
        GlobalVar.set_aivk_root(root_path)
        steps.append(f"5. 更新全局变量AIVK_ROOT: {root_path}")
        
        # 检查目录结构
        steps.append(f"6. 验证目录结构:")
        for subdir in ["cache", "tmp", "data", "etc", "home"]:
            if (root_path / subdir).exists():
                steps.append(f"   - {subdir}/ ✓")
            else:
                steps.append(f"   - {subdir}/ ✗")
        
        # 显示挂载时间
        steps.append(f"7. 挂载完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    except Exception as e:
        return f"挂载失败: {str(e)}\n已执行的步骤:\n" + "\n".join(steps)
    
    # 返回详细的挂载信息
    return f"AIVK根目录挂载成功！\n\n挂载过程详情:\n" + "\n".join(steps)


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

@mcp.tool(name="set aivk root dir", instructions="set aivk root dir", mime_type="text/plain")
def set_aivk_root_dir(path: str):
    """设置 AIVK 根目录"""
    GlobalVar.set_aivk_root(path)
    return f"AIVK root dir set to {path}"


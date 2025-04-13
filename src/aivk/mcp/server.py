import asyncio
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import logging

try:
    from ..base.aivkio import AivkIO
except ImportError:
    from aivk.base.aivkio import AivkIO

# 设置 logger
logger = logging.getLogger("aivk.mcp")

# 获取配置
aivk_config = AivkIO.get_config("aivk")
port = aivk_config.get("port", 10140)
host = aivk_config.get("host", "localhost")

# 创建 FastMCP 实例
mcp = FastMCP(
    name="aivk", 
    instructions="AIVK MCP 服务器提供文件系统操作接口", 
    port=port,
    host=host
)
aivk_config["port"] = port
aivk_config["host"] = host
AivkIO.save_config("aivk", aivk_config)


@mcp.resource("aivk://status", mime_type = "text/plain")
def status():
    """返回 AIVK 状态信息
    查看现在是否已经初始化aivk root dir
    """
    root: Path = AivkIO.get_aivk_root()
    if AivkIO.is_aivk_root():
        # 获取更多状态信息
        try:
            meta = AivkIO.get_meta("aivk")
            module_ids = AivkIO.get_module_ids()
            
            return {
                "status": "initialized",
                "aivk_root": str(root),
                "version": meta.get("version", "unknown"),
                "created_at": meta.get("created_at", ""),
                "updated_at": meta.get("updated_at", ""),
                "modules_count": len(module_ids) if module_ids else 0,
                "modules": list(module_ids.keys()) if module_ids else []
            }
        except Exception as e:
            logger.error(f"获取状态信息失败: {e}")
            return {
                "status": "initialized",
                "aivk_root": str(root),
                "error": str(e)
            }
    else:
        return {
            "status": "not_initialized",
            "aivk_root": str(root),
            "message": "AIVK 未初始化，请先执行 init_aivk_root_dir 初始化"
        }
    
    
@mcp.tool(name="init_aivk_root_dir", description="initialize aivk root dir")
def init_aivk_root_dir(path: str = None):
    """初始化 AIVK 根目录
    
    :param path: AIVK 根目录路径，默认为当前配置的路径
    :return: 初始化结果
    """
    try:
        if path:
            path_obj = Path(path).absolute()
            logger.info(f"设置 AIVK 根目录: {AivkIO.get_aivk_root()} -> {path_obj}")
            AivkIO.set_aivk_root(path_obj)
        
        # 使用 force=False 保证安全性，防止误删除
        AIVK_ROOT = asyncio.run(AivkIO.fs_init(force=False))
        
        return {
            "success": True,
            "path": str(AIVK_ROOT),
            "message": f"AIVK 根目录初始化成功: {AIVK_ROOT}"
        }
    except Exception as e:
        logger.error(f"初始化 AIVK 根目录失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"初始化失败: {e}"
        }

@mcp.tool(name="mount_aivk_root_dir", description="mount aivk root dir")
def mount_aivk_root_dir(path: str = None):
    """挂载 AIVK 根目录
    
    :param path: AIVK 根目录路径，默认为当前配置的路径
    :return: 挂载结果
    """
    try:
        if path:
            path_obj = Path(path).absolute()
            logger.info(f"设置 AIVK 根目录: {AivkIO.get_aivk_root()} -> {path_obj}")
            AivkIO.set_aivk_root(path_obj)
        
        AIVK_ROOT = asyncio.run(AivkIO.fs_mount())
        
        # 获取已加载的模块ID
        module_ids = AivkIO.get_module_ids()
        
        return {
            "success": True,
            "path": str(AIVK_ROOT),
            "message": f"AIVK 根目录挂载成功: {AIVK_ROOT}",
            "modules_count": len(module_ids) if module_ids else 0,
            "modules": list(module_ids.keys()) if module_ids else []
        }
    except FileNotFoundError as e:
        logger.error(f"挂载 AIVK 根目录失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "AIVK 根目录不存在或未初始化，请先执行 init_aivk_root_dir 初始化"
        }
    except Exception as e:
        logger.error(f"挂载 AIVK 根目录失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"挂载失败: {e}"
        }


@mcp.resource("aivk://root", mime_type="text/plain")
def root():
    """返回 AIVK 根目录路径"""
    return {
        "aivk_root": str(AivkIO.get_aivk_root()),
        "is_initialized": AivkIO.is_aivk_root()
    }

@mcp.tool(name="ping", description="send ping response")
def ping():
    """返回 AIVK ping 响应信息"""
    return {
        "message": "pong!",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool(name="set_aivk_root_dir", description="set aivk root dir")
def set_aivk_root_dir(path: str):
    """设置 AIVK 根目录
    
    :param path: 新的 AIVK 根目录路径
    :return: 设置结果
    """
    try:
        path_obj = Path(path).absolute()
        original_path = AivkIO.get_aivk_root()
        
        # 检查路径是否存在
        if not path_obj.exists():
            return {
                "success": False,
                "error": "指定路径不存在",
                "message": f"路径不存在: {path_obj}"
            }
        
        AivkIO.set_aivk_root(path_obj)
        
        return {
            "success": True,
            "original_path": str(original_path),
            "new_path": str(path_obj),
            "message": f"AIVK 根目录已设置: {original_path} -> {path_obj}"
        }
    except Exception as e:
        logger.error(f"设置 AIVK 根目录失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"设置失败: {e}"
        }

@mcp.tool(name="get_config", description="get configuration by id")
def get_config(id: str):
    """获取指定ID的配置
    
    :param id: 配置ID
    :return: 配置内容
    """
    try:
        config = AivkIO.get_config(id)
        return {
            "success": True,
            "id": id,
            "config": config
        }
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        return {
            "success": False,
            "id": id,
            "error": str(e),
            "message": f"获取配置失败: {e}"
        }



@mcp.tool(name="get_meta", description="get metadata by id")
def get_meta(id: str):
    """获取指定ID的元数据
    
    :param id: 元数据ID
    :return: 元数据内容
    """
    try:
        meta = AivkIO.get_meta(id)
        return {
            "success": True,
            "id": id,
            "meta": meta
        }
    except Exception as e:
        logger.error(f"获取元数据失败: {e}")
        return {
            "success": False,
            "id": id,
            "error": str(e),
            "message": f"获取元数据失败: {e}"
        }



@mcp.tool(name="get_module_ids", description="get all registered module IDs")
def get_module_ids():
    """获取所有已注册的模块ID
    
    :return: 模块ID列表
    """
    try:
        module_ids = AivkIO.get_module_ids()
        return {
            "success": True,
            "count": len(module_ids) if module_ids else 0,
            "module_ids": list(module_ids.keys()) if module_ids else [],
            "modules_info": module_ids
        }
    except Exception as e:
        logger.error(f"获取模块ID失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"获取模块ID失败: {e}"
        }
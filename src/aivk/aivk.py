# AIVK - AI Virtual Kernel
# Author: LIghtJUNction
# Version: 0.1.0
# Description: AI virtual kernel 
# 
# 导入核心库
try:
    from .core import LKM, LifeCycle, AivkRoot
except ImportError:
    raise ImportError(" import error : aivk etc.")
# 导入基本库
try:
    from pathlib import Path
    import logging
except ImportError:
    raise ImportError("oops: import error : pathlib")

# 设置日志记录器
logger = logging.getLogger("aivk.entry")

# 导入第三方库
# try:
#     from pydantic import BaseModel
# except ImportError:
#     raise ImportError("Please install the required dependencies: pydantic, pathlib, etc.")


"""
请实现以下方法：
- _onLoad
- _onUnload
- _onInstall
- _onUninstall
- _onUpdate

为什么是这些方法？
_onload 为内部方法，真正的onLoad方法在基类中已经实现
这样是为了添加锁机制，避免错误的调用顺序

put it simply:
pls implement _onLoad, _onUnload, _onInstall, _onUninstall, _onUpdate methods
and call them onLoad, onUnload, onInstall, onUninstall, onUpdate methods
so that we can add lock mechanism to avoid wrong call order

因此开发模块时，请实现_onLoad方法 
而调用其他模块时，直接调用onLoad方法即可

"""



class Entry(LKM):
    """
    AIVK系统入口类
    
    该类继承自LKM(Loadable Kernel Module)，实现了AIVK系统的生命周期管理。
    作为系统的主要入口点，负责将CLI命令转发给底层的LifeCycle模块处理。
    所有方法都是类方法，可以访问类的状态和配置。
    """
    
    @classmethod
    async def _onLoad(cls, aivk_root: str | Path) -> None:
        """
        挂载AIVK根目录
        
        当用户请求挂载AIVK根目录时，该方法被调用，激活系统
        
        参数:
            aivk_root: AIVK根目录路径，可以是字符串或Path对象
        """
        aivk = await LifeCycle.onLoad(aivk_root)
        return aivk
    
    @classmethod
    async def _onUnload(cls, aivk : AivkRoot) -> None:
        """
        取消挂载AIVK根目录
        
        当AIVK系统需要关闭时执行，用于安全地终止服务和释放资源
        
        参数:
            aivk: AivkRoot实例 挂载成功后获取的对象
        """
        await LifeCycle.onUnload(aivk)
    
    @classmethod
    async def _onInstall(cls, aivk_root: str | Path) -> None:
        """
        初始化AIVK根目录
        
        用于首次设置AIVK系统，创建必要的目录结构和配置文件
        
        参数:
            aivk_root: AIVK根目录路径，可以是字符串或Path对象
        """
        aivk = await LifeCycle.onInstall(aivk_root)
        return aivk
    
    @classmethod
    async def _onUninstall(cls, aivk: AivkRoot) -> None:
        """
        移除AIVK根目录
        
        注意：确保只传递AivkRoot实例给LifeCycle.onUninstall，
        而不是传递布尔值等其他类型
        """
        try:
            # 确保aivk是AivkRoot实例
            if isinstance(aivk, AivkRoot):
                # 调用LifeCycle的onUninstall方法
                await LifeCycle.onUninstall(aivk)
            else:
                logger.error(f"_onUninstall接收到非AivkRoot参数: {type(aivk)}")
        except Exception as e:
            logger.error(f"Error during loader module onUninstall: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    @classmethod
    async def _onUpdate(cls, aivk_root: str | Path) -> None:
        """
        更新AIVK系统
        
        当系统需要升级或更新配置时调用
        
        参数:
            aivk_root: AIVK根目录路径，可以是字符串或Path对象
        """
        await LifeCycle.onUpdate(aivk_root)
















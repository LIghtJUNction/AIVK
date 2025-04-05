# AIVK - AI Virtual Kernel
# Author: LIghtJUNction
# Version: 0.1.0
# Description: AI virtual kernel 
# 
# 导入核心库
try:
    from .core import LKM,LifeCycle
except ImportError:
    raise ImportError(" import error : aivk etc.")
# 导入基本库
# ...

# 导入第三方库
# try:
#     from pydantic import BaseModel
# except ImportError:
    raise ImportError("Please install the required dependencies: pydantic, pathlib, etc.")

class Entry(LKM):
    async def onLoad():
        await LifeCycle.onLoad()
    async def onUnload():
        await LifeCycle.onUnload()
    async def onInstall():
        await LifeCycle.onInstall()
    async def onUninstall():
        await LifeCycle.onUninstall()
    async def onUpdate():
        await LifeCycle.onUpdate()
    















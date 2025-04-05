from pydantic import BaseModel



class LifeCycle(BaseModel):
    @staticmethod
    async def onLoad() -> None:
        """
        初始化 -- 运行初始模块加载器
        """
        pass
    @staticmethod
    async def onUnload() -> None:
        pass
    @staticmethod
    async def onInstall() -> None:
        pass
    @staticmethod
    async def onUninstall() -> None:
        pass
    @staticmethod
    async def onUpdate() -> None:
        pass


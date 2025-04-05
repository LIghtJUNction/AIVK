from pathlib import Path
from pydantic import BaseModel

# 修复循环导入问题 - 不再从..core导入AivkRoot
from .aivkroot import AivkRoot
import shutil
import logging

logger = logging.getLogger("aivk.core.lifecycle")

class LifeCycle(BaseModel):
    @staticmethod
    async def onLoad(aivk_root: Path | str) -> None:
        """
        初始化 -- 运行初始模块加载器
        """
        if isinstance(aivk_root, str):
            # 将字符串路径转换为Path对象
            path = Path(aivk_root)
            # 如果是相对路径，转换为绝对路径
            if not path.is_absolute():
                aivk_root = path.absolute()
            else:
                aivk_root = path
        # aivk 是AivkRoot类的一个实例  
        aivk = AivkRoot.mount(aivk_root)
        # 仅调用loader模块的onLoad方法 之后将模块加载权移交给loader
        # core 模块 ： loader
        
        if aivk.check_module_status("loader"):
            # loader模块存在且未禁用
            loader_entry = aivk.get_module_entry("loader")
            try:
                if loader_entry:
                    # 调用loader模块的onLoad方法
                    await loader_entry.onLoad(aivk)
                else:
                    logger.error("entry point not found in loader module!")
            except Exception as e:
                logger.error(f"Error during loader module onLoad: {e}")

        return aivk
        

    @staticmethod
    async def onUnload(aivk : AivkRoot) -> None:
        """
        优雅退出并关闭 清理资源
        """
        logger.info("退出 AIVK 系统...")    
        # 调用loader模块的onUnload方法
        # 随后由loader模块调用其他模块的onUnload方法
        if aivk.check_module_status("loader"):
            loader_entry = aivk.get_module_entry("loader")
            try:
                if loader_entry:
                    await loader_entry.onUnload(aivk)
                else:
                    logger.error("entry point not found in loader module!")
            except Exception as e:
                logger.error(f"Error during loader module onUnload: {e}")
        
    @staticmethod
    async def onInstall(aivk_root: Path | str) -> None:
        """
        初始化 -- 给定一个空目录作为AIVK的根目录
        """
        if isinstance(aivk_root, str):
            # 将字符串路径转换为Path对象
            path = Path(aivk_root)
            # 如果是相对路径，转换为绝对路径
            if not path.is_absolute():
                aivk_root = path.absolute()
            else:
                aivk_root = path
        
        # 目录不存在时执行初始化
        if not aivk_root.exists():
            aivk_root.mkdir(parents=True, exist_ok=True)
            logger.info("开始初始化 AIVK 根目录...")
            # aivk 是AivkRoot类的一个实例
            aivk = AivkRoot.init(aivk_root)
            # TODO : 下载核心模块并解压至modules目录
            logger.info("aivk_root 初始化完成 \n 请使用 aivk -m 命令挂载")
            return aivk
        
        # 目录存在时的处理
        # 检查是否为空目录
        is_empty = not any(aivk_root.iterdir())
        if is_empty:
            logger.info("开始在空目录初始化 AIVK 根目录...")
            aivk = AivkRoot.init(aivk_root)
            logger.info("aivk_root 初始化完成 \n 请使用 aivk -m 命令挂载")
            return aivk
        else:
            logger.warning("该目录非空！")
            _aivk = aivk_root / ".aivk"
            if _aivk.exists() and _aivk.is_file():
                logger.warning("该目录已存在AIVK系统！")
                aivk = AivkRoot.mount(aivk_root)
                return aivk
            else:
                logger.error("该目录不是有效的AIVK根目录！")
                logger.warning("将删除该目录并重新初始化 AIVK 根目录...")
                input("回车继续: ")
                shutil.rmtree(aivk_root)
                aivk_root.mkdir(parents=True, exist_ok=True)
                aivk = AivkRoot.init(aivk_root)
                return aivk


    @staticmethod
    async def onUninstall(aivk : AivkRoot | str | Path | bool) -> None:
        """
        移除AIVK的根目录
        
        参数:
            aivk: AivkRoot实例、路径字符串、Path对象或布尔值
                 如果是AivkRoot实例，将使用其aivk_root属性
                 如果是字符串或Path对象，将直接作为AIVK根目录路径
                 如果是布尔值，则表示操作是否成功，这种情况下不执行任何操作
        """
        # 处理不同类型的输入参数
        if isinstance(aivk, bool):
            logger.error("接收到布尔值而不是AivkRoot实例，无法继续执行卸载安装操作")
            return
        
        # 获取AIVK根目录路径
        if isinstance(aivk, AivkRoot):
            aivk_root = aivk.aivk_root
        elif isinstance(aivk, (str, Path)):
            aivk_root = Path(aivk)
        else:
            logger.error(f"无法识别的参数类型: {type(aivk)}")
            return
        
        # 直接将整个目录删除
        if aivk_root.exists():
            for item in aivk_root.iterdir():
                if item.is_dir():
                    AivkRoot.rmtree(item)
                else:
                    item.unlink()
            aivk_root.rmdir()
            logger.info(f"已删除目录: {aivk_root}")
        else:
            logger.info(f"目录不存在: {aivk_root}")

    
    @staticmethod
    async def onUpdate() -> None:
        pass


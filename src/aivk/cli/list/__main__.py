# -*- coding: utf-8 -*-
import logging
from logging import getLogger
from aivk.api import AivkContext
from click import command, option

logger = getLogger("aivk.cli.list")

@command("list")
@option("-v", "--verbose", count=True,default=1 , help="增加详细程度 (-v INFO, -vv DEBUG, -vvv 显示所有包详情)")
def aivk_list(verbose: int) -> list[dict[str, str]]:
    """
    列出所有已安装的 AIVK 模块
    """
    # 根据 verbose 级别配置日志
    if verbose == 0:
        log_level = logging.WARNING
    elif verbose == 1:
        log_level = logging.INFO
    elif verbose == 2:
        log_level = logging.DEBUG
    elif verbose == 3:  # verbose >= 3
        log_level = logging.DEBUG
    else:
        log_level = logging.DEBUG
        logger.warning("已达最高 verbose 级别，使用 DEBUG 级别")
    show_all_packages = verbose >= 3
      # 配置当前模块的日志器
    logger.setLevel(log_level)
    
    # 如果没有处理器，添加一个控制台处理器
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    else:
        # 如果已有处理器，更新其级别
        for handler in logger.handlers:
            handler.setLevel(log_level)
    try:        
        logger.info("正在扫描已安装的 AIVK 模块...")
        ctx = AivkContext.getContext()
        modules = ctx.get_aivk_installed_modules("aivk", show_all_packages)
        
        if not modules:
            logger.warning("没有找到已安装的 AIVK 模块")
            logger.info("提示：AIVK 模块应该以 'aivk_' 或 'aivk-' 开头")
            return []        
        logger.info(f"找到 {len(modules)} 个已安装的 AIVK 模块：")
        
        for module in modules:
            # 截断过长的描述
            description = module['description']
            if len(description) > 40:
                description = description[:37] + "..."

            logger.info(f"{module['name']} ({module['version']})<{module['author']}>: {description}")
        logger.info(f"列出了 {len(modules)} 个 AIVK 模块")
        return modules
        
    except Exception as e:
        error_msg = f"列出 AIVK 模块时发生错误: {e}"
        logger.error(error_msg)
        if verbose >= 2:  # 只在 DEBUG 级别显示完整堆栈跟踪
            import traceback
            logger.debug(traceback.format_exc())
        return []
    
# -*- coding: utf-8 -*-
from logging import getLogger , basicConfig , DEBUG , INFO, WARNING, ERROR
from aivk.api import AivkContext
from click import command, option


logger = getLogger("aivk.cli.run")


@command()
@option("-v", "--verbose", count=True,default = 2, help="详细程度，可以多次使用 (-v, -vv, -vvv)")
def run( verbose: int):
    """
    AIVK 运行命令
    :param style: 运行方式，支持 "cli" 或 "web"
    启动 AIVK CLI
    """    # 更合理的日志级别设置
    if verbose == 3:
        # -vvv: 显示所有日志（DEBUG 及以上）
        basicConfig(level=DEBUG)
        logger.info(f"日志级别设置为 DEBUG (verbose={verbose}) - 显示所有调试信息")
    elif verbose == 2:
        # -vv: 显示详细信息（INFO 及以上）
        basicConfig(level=INFO)
        logger.info(f"日志级别设置为 INFO (verbose={verbose}) - 显示详细信息")
    elif verbose == 1:
        # -v: 显示重要信息（INFO 及以上，但减少部分详细输出）
        basicConfig(level=WARNING)
        logger.info(f"日志级别设置为 WARNING (verbose={verbose}) - 显示重要信息")
    else:
        basicConfig(level=ERROR)
        logger.info(f"日志级别设置为 ERROR (verbose={verbose}) - 只显示错误信息")
        # 不输出日志级别信息，保持简洁

    try:
        # 加载aivk_module
        logger.info("开始加载 AIVK 模块...")
        ctx = AivkContext.getContext()
        ctx.load_aivk_modules(verbose_level=verbose)

        logger.info("AIVK 模块加载完成")
                
    except Exception as e:
        logger.error(f"运行 AIVK 时发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
# -*- coding: utf-8 -*-
from click import Context, group, option, pass_context
from logging import Logger, getLogger

from rich.traceback import install as install_rich_traceback
from colorlog import ColoredFormatter
from .run import run
install_rich_traceback()
logger = getLogger("aivk")

def setup_aivk_logger(logger: Logger, level: int):
    """
    基础日志设置
    """
    fmt = (
        "%(asctime_log_color)s%(asctime)s "
        "%(levelname_log_color)s%(levelname)s "
        "%(name_log_color)s%(name)s "
        "%(log_color)s%(message)s"
    )
    colors = {
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
    secondary_colors = {
        'asctime': {
            'DEBUG':    'blue',
            'INFO':     'white',
            'WARNING':  'white',
            'ERROR':    'red',
            'CRITICAL': 'bold_white',
        },
        'levelname': {
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        },
        'name': {
            'DEBUG':    'blue',
            'INFO':     'white',
            'WARNING':  'white',
            'ERROR':    'red',
            'CRITICAL': 'white',
        }
    }
    formatter = ColoredFormatter(fmt, log_colors=colors, secondary_log_colors=secondary_colors)
    handler = logger.handlers[0] if logger.handlers else None
    if handler:
        handler.setFormatter(formatter)
    else:
        import sys
        from logging import StreamHandler
        handler = StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)

@group()
@option('--verbose', "-v", count=True, default=4, help='aivk 日志级别，1-5，默认为4:INFO (CRITICAL=1, ERROR=2, WARNING=3, INFO=4, DEBUG=5)')
@pass_context
def cli(ctx: Context, verbose: int) -> None:
    """
    Aivk CLI
    """
    setup_aivk_logger(logger, verbose)
    logger.debug(f"Aivk CLI 启动，日志级别: {logger.getEffectiveLevel()}")
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose

cli.add_command(run)
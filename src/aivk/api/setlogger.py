# AIVK 日志工具集
# CLI 日志等级设置 set_logger_level_from_ctx
# ...
from logging import Logger
from click import Context

def set_logger_level_from_ctx(ctx: Context, logger: Logger) -> None:
    """
    根据 click ctx 的 verbose 参数设置 logger 日志等级，并自动添加 StreamHandler（如无）
    """
    ctx.ensure_object(dict)
    verbose = ctx.obj.get('verbose', 2)
    # 日志等级映射
    if verbose >= 3:
        level = 'DEBUG'
    elif verbose == 2:
        level = 'INFO'
    elif verbose == 1:
        level = 'WARNING'
    else:
        level = 'ERROR'
    logger.setLevel(level)
    # 自动添加 handler，避免无输出
    if not logger.hasHandlers():
        import sys
        from logging import StreamHandler, Formatter
        handler = StreamHandler(sys.stdout)
        handler.setFormatter(Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(handler)
    logger.propagate = False

from logging import LogRecord, Formatter

class ErrorTraceFormatter(Formatter):
    """
    彩色日志格式化器，error 级别自动输出堆栈和具体位置
    """
    def __init__(self, base_formatter: Formatter) -> None:
        super().__init__()
        self.base_formatter = base_formatter

    def format(self, record: LogRecord) -> str:
        s = self.base_formatter.format(record)
        if record.levelno >= 40:  # ERROR 及以上
            import traceback
            # 追加代码位置
            s += f"\n位置: {record.pathname}:{record.lineno}"
            # 追加堆栈（如有）
            if record.exc_info:
                s += "\n" + ''.join(traceback.format_exception(*record.exc_info))
        return s

def set_logger_style(logger: Logger, style: str = "fancy") -> None:
    """
    设置 logger 的美化样式，支持彩色/带时间/自定义格式，推荐用 colorlog
    时间戳字段也高亮，error 自动带堆栈和位置
    """
    import sys
    from logging import StreamHandler
    try:
        from colorlog import ColoredFormatter
        match style:
            case "fancy":
                fmt = (
                    "%(log_color)s[%(levelname)s]%(reset)s "
                    "%(asctime_log_color)s%(asctime)s%(reset)s "
                    "%(cyan)s%(name)s%(reset)s: "
                    "%(message_log_color)s%(message)s"
                )
                datefmt = "%H:%M:%S"
                colors = {
                    'DEBUG':    'bold_blue',
                    'INFO':     'bold_green',
                    'WARNING':  'bold_yellow',
                    'ERROR':    'bold_red',
                    'CRITICAL': 'bold_purple',
                }
                secondary = {
                    'message': colors,
                    'asctime': {'DEBUG': 'white', 'INFO': 'cyan', 'WARNING': 'yellow', 'ERROR': 'red', 'CRITICAL': 'purple'}
                }
                base_formatter = ColoredFormatter(fmt, datefmt=datefmt, log_colors=colors, secondary_log_colors=secondary)
            case "timestamp":
                base_formatter = ColoredFormatter("[%(levelname)s] %(asctime)s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            case _:
                base_formatter = ColoredFormatter("[%(levelname)s] %(message)s")
    except ImportError:
        from logging import Formatter
        base_formatter = Formatter("[%(levelname)s] %(message)s")
    logger.handlers.clear()
    handler = StreamHandler(sys.stdout)
    handler.setFormatter(ErrorTraceFormatter(base_formatter))
    logger.addHandler(handler)
    logger.propagate = False
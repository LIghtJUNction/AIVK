"""AIVK Logger Module

提供多种日志样式，适应不同场景需求：
- minimal: 最简约的单行样式，适合高密度日志
- compact: 紧凑型布局，适合一般日志记录
- status: 状态栏风格，适合系统状态监控
- notify: 通知风格，适合重要消息提醒
- json: JSON风格，适合结构化数据
- code: 代码风格，适合开发调试
- error: 错误展示风格，适合异常追踪
- metric: 指标风格，适合性能监控
"""

from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.align import Align
from rich.layout import Layout
from rich.text import Text
from rich.json import JSON
from rich.syntax import Syntax
from rich.measure import Measurement
from rich import box
from rich.style import Style
from datetime import datetime
import logging
import json
from typing import Literal, Optional, Union, Dict, Any, Callable
from rich.traceback import Traceback
import threading
import functools
import time

# 创建控制台实例
console = Console(width=120, color_system="truecolor")

# 默认主题
THEMES = {
    "minimal": {
        "debug": "grey70",
        "info": "bright_blue",
        "warning": "yellow",
        "error": "red",
        "critical": "red reverse"
    },
    "dark": {
        "debug": "grey50",
        "info": "cyan",
        "warning": "yellow",
        "error": "red1",
        "critical": "bright_red"
    },
    "light": {
        "debug": "grey42",
        "info": "blue",
        "warning": "orange3",
        "error": "red3",
        "critical": "red1 reverse"
    },
    "colorful": {
        "debug": "purple4",
        "info": "spring_green3",
        "warning": "gold3",
        "error": "red1",
        "critical": "bright_red reverse"
    }
}

# 图标集
ICONS = {
    "minimal": {
        logging.DEBUG: "·",
        logging.INFO: "○",
        logging.WARNING: "△",
        logging.ERROR: "×",
        logging.CRITICAL: "⬟"
    },
    "emoji": {
        logging.DEBUG: "🔍",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "☠️"
    },
    "ascii": {
        logging.DEBUG: "[d]",
        logging.INFO: "[i]",
        logging.WARNING: "[!]",
        logging.ERROR: "[x]",
        logging.CRITICAL: "[!!]"
    },
    "blocks": {
        logging.DEBUG: "▪",
        logging.INFO: "▫",
        logging.WARNING: "▲",
        logging.ERROR: "▼",
        logging.CRITICAL: "◆"
    }
}

# 基础处理器
class BaseHandler(RichHandler):
    def __init__(self, *args, **kwargs):
        self.theme_name = kwargs.pop("theme", "dark")
        self.icon_set = kwargs.pop("icons", "minimal")
        kwargs['console'] = Console(
            theme=Theme(THEMES[self.theme_name]),
            width=120,
            color_system="truecolor"
        )
        kwargs['rich_tracebacks'] = True
        kwargs['markup'] = True
        kwargs['show_time'] = True
        kwargs['show_level'] = True
        super().__init__(*args, **kwargs)
        
    def get_style(self, level: int) -> str:
        """获取日志级别对应的样式"""
        level_names = {
            logging.DEBUG: "debug",
            logging.INFO: "info",
            logging.WARNING: "warning",
            logging.ERROR: "error",
            logging.CRITICAL: "critical"
        }
        return level_names.get(level, "default")
    
    def get_icon(self, level: int) -> str:
        """获取日志级别对应的图标"""
        return ICONS[self.icon_set].get(level, "?")

# 最简约风格 - 适合高密度日志
class MinimalHandler(BaseHandler):
    def render(self, record: logging.LogRecord, traceback: Optional[Traceback] = None, message_renderable: Union[str, Text] = "") -> Text:
        style = self.get_style(record.levelno)
        icon = self.get_icon(record.levelno)
        text = Text()
        text.append(f"{icon} ", style=style)
        text.append(str(message_renderable), style=style)
        return text

# 紧凑风格 - 适合一般日志
class CompactHandler(BaseHandler):
    def render(self, record: logging.LogRecord, traceback: Optional[Traceback] = None, message_renderable: Union[str, Text] = "") -> Text:
        style = self.get_style(record.levelno)
        icon = self.get_icon(record.levelno)
        text = Text()
        text.append(f"{icon} {record.levelname:8}", style=style)
        text.append(" │ ", style="bright_black")
        text.append(str(message_renderable))
        if traceback:
            text.append(f"\n{traceback}")
        return text

# 状态风格 - 适合系统监控
class StatusHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bright_black][[/]{task.fields[icon]}[bright_black]][/]", justify="center"),
            TextColumn("[{task.fields[style]}]{task.fields[level]:8}[/]", justify="right"),
            TextColumn("{task.fields[message]:<40}"),
            TextColumn("[bright_black]{task.fields[location]}[/]"),
            TextColumn("[bright_black]{task.fields[time]}[/]"),
            console=console,
            expand=True
        )
        self.task_id = self.progress.add_task(
            "", 
            icon="",
            style="",
            level="",
            message="",
            location="",
            time=""
        )
    
    def render(self, record: logging.LogRecord, traceback: Optional[Traceback] = None, message_renderable: Union[str, Text] = "") -> Progress:
        style = self.get_style(record.levelno)
        icon = self.get_icon(record.levelno)
        
        # 格式化文件位置信息
        location = f"{record.pathname}:{record.lineno}"
        if len(location) > 30:
            # 如果路径太长，只显示最后的文件名和行号
            parts = location.split('\\')  # 使用Windows路径分隔符
            location = f".../{parts[-1]}"
            
        # 格式化消息，确保不会太长
        message = str(message_renderable)
        if len(message) > 40:
            message = message[:37] + "..."
            
        self.progress.update(
            self.task_id,
            icon=icon,
            style=style,
            level=record.levelname,
            message=message,
            location=location,
            time=self.formatter.formatTime(record)
        )
        
        if traceback:
            self.progress.print(traceback)
        
        return self.progress

# 通知风格 - 适合重要消息
class NotifyHandler(BaseHandler):
    def render(self, record: logging.LogRecord, traceback: Optional[Traceback] = None, message_renderable: Union[str, Text] = "") -> Panel:
        style = self.get_style(record.levelno)
        icon = self.get_icon(record.levelno)
        title = Text()
        title.append(f" {icon} ", style=style)
        title.append(record.levelname, style=style)
        
        message = Text(str(message_renderable))
        if traceback:
            message.append(f"\n{traceback}")
            
        footer = Text()
        footer.append(self.formatter.formatTime(record), style="bright_black")
        footer.append(" | ", style="bright_black")
        footer.append(record.name, style="bright_black")
        
        return Panel(
            Align.center(message),
            title=title,
            subtitle=footer,
            border_style=style,
            box=box.HEAVY,
            padding=(1, 2)
        )

# JSON风格 - 适合结构化数据
class JsonHandler(BaseHandler):
    def render(self, record: logging.LogRecord, traceback: Optional[Traceback] = None, message_renderable: Union[str, Text] = "") -> Text:
        # 创建日志数据字典
        try:
            # 如果消息是字典，直接使用
            message = eval(str(message_renderable))
            if not isinstance(message, dict):
                message = {"message": str(message_renderable)}
        except:
            message = {"message": str(message_renderable)}
        
        data = {
            "timestamp": self.formatter.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            **message
        }
        if traceback:
            data["traceback"] = str(traceback)
            
        # 创建一个漂亮的JSON显示
        style = self.get_style(record.levelno)
        icon = self.get_icon(record.levelno)
        
        text = Text()
        text.append(f"{icon} ", style=style)
        
        # 使用 json.dumps 格式化 JSON 数据
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        # 为不同类型的内容添加语法高亮
        for line in json_str.split("\n"):
            # 检测并高亮键
            if ": " in line:
                key, value = line.split(": ", 1)
                text.append(key, style="bright_blue")
                text.append(": ")
                # 根据值类型设置不同颜色
                if value.startswith('"'):
                    text.append(value, style=style)
                elif value in ("true", "false", "null"):
                    text.append(value, style="bright_magenta")
                elif value.replace(".", "").isdigit():
                    text.append(value, style="bright_cyan")
                else:
                    text.append(value, style=style)
            else:
                text.append(line, style="bright_black")
            text.append("\n")
            
        return text

# 代码风格 - 适合调试
class CodeHandler(BaseHandler):
    def render(self, record: logging.LogRecord, traceback: Optional[Traceback] = None, message_renderable: Union[str, Text] = "") -> Panel:
        style = self.get_style(record.levelno)
        icon = self.get_icon(record.levelno)
        
        header = Text()
        header.append(f"{icon} ", style=style)
        header.append(f"[{record.levelname}] ", style=style)
        header.append(self.formatter.formatTime(record), style="bright_black")
        
        # 尝试解析消息为Python代码
        message = str(message_renderable)
        try:
            syntax = Syntax(message, "python", theme="monokai")
        except:
            syntax = Text(message)
            
        if traceback:
            syntax.append(f"\n{traceback}")
            
        return Panel(
            syntax,
            title=header,
            border_style=style,
            box=box.HEAVY,
            padding=(0, 1)
        )

# 错误风格 - 适合异常追踪
class ErrorHandler(BaseHandler):
    def render(self, record: logging.LogRecord, traceback: Optional[Traceback] = None, message_renderable: Union[str, Text] = "") -> Panel:
        style = self.get_style(record.levelno)
        icon = self.get_icon(record.levelno)
        
        layout = Layout()
        
        # 头部：错误类型和时间
        header = Text()
        header.append(f"{icon} ", style=style)
        header.append(record.levelname, style=style)
        header.append(" | ", style="bright_black")
        header.append(self.formatter.formatTime(record), style="bright_black")
        
        # 主体：错误消息、文件路径和行号
        main = Text()
        main.append(str(message_renderable))
        main.append("\n", style="bright_black")
        main.append(f"File: {record.pathname}:{record.lineno}", style="bright_black")
        if hasattr(record, "funcName") and record.funcName:
            main.append(f"\nFunction: {record.funcName}", style="bright_black")
        if traceback:
            main.append("\n")
            main.append(traceback)
            
        # 页脚：logger名称
        footer = Text()
        footer.append("Logger: ", style="bright_black")
        footer.append(record.name)
        
        return Panel(
            main,
            title=header,
            subtitle=footer,
            border_style=style,
            box=box.DOUBLE_EDGE,
            padding=(1, 2)
        )

# 指标风格 - 适合性能监控
class MetricHandler(BaseHandler):
    def render(self, record: logging.LogRecord, traceback: Optional[Traceback] = None, message_renderable: Union[str, Text] = "") -> Table:
        style = self.get_style(record.levelno)
        icon = self.get_icon(record.levelno)
        
        # 创建表格
        table = Table(
            show_header=False,
            box=box.MINIMAL,
            show_edge=False,
            padding=(0, 1)
        )
        
        # 添加列
        table.add_column("Icon", style=style, width=2)
        table.add_column("Level", style=style, width=8)
        table.add_column("Time", style="bright_black", width=20)
        table.add_column("Metrics", ratio=1)
        
        # 尝试解析消息为指标数据
        message = str(message_renderable)
        try:
            data = json.loads(message)
            metrics = " | ".join(f"{k}: {v}" for k, v in data.items())
        except:
            metrics = message
            
        # 添加行
        table.add_row(
            icon,
            record.levelname,
            self.formatter.formatTime(record),
            metrics
        )
        
        if traceback:
            table.add_row("", "", "", str(traceback))
            
        return table

# 日志样式管理器
class LoggerManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.current_style = "compact"
            self.current_theme = "dark"
            self.current_icons = "minimal"
            self.level = logging.INFO
            self.show_time = True
            self.show_path = False
            self.handlers = {}
            self._initialized = True
    
    def switch_style(self, 
        style: Literal["minimal", "compact", "status", "notify", "json", "code", "error", "metric"] = None,
        theme: Literal["minimal", "dark", "light", "colorful"] = None,
        icons: Literal["minimal", "emoji", "ascii", "blocks"] = None,
        level: int = None,
        show_time: bool = None,
        show_path: bool = None
    ) -> None:
        """
        动态切换日志样式
        Args:
            style: 日志样式
            theme: 颜色主题
            icons: 图标集
            level: 日志级别
            show_time: 是否显示时间
            show_path: 是否显示文件路径
        """
        with self._lock:
            if style is not None:
                self.current_style = style
            if theme is not None:
                self.current_theme = theme
            if icons is not None:
                self.current_icons = icons
            if level is not None:
                self.level = level
            if show_time is not None:
                self.show_time = show_time
            if show_path is not None:
                self.show_path = show_path
                
            # 更新日志配置
            setup_logging(
                style=self.current_style,
                theme=self.current_theme,
                icons=self.current_icons,
                level=self.level,
                show_time=self.show_time,
                show_path=self.show_path
            )
    
    def get_current_config(self) -> dict:
        """获取当前日志配置"""
        return {
            "style": self.current_style,
            "theme": self.current_theme,
            "icons": self.current_icons,
            "level": self.level,
            "show_time": self.show_time,
            "show_path": self.show_path
        }

# 创建全局管理器实例
logger_manager = LoggerManager()

def setup_logging(
    style: Literal["minimal", "compact", "status", "notify", "json", "code", "error", "metric"] = "compact",
    theme: Literal["minimal", "dark", "light", "colorful"] = "dark",
    icons: Literal["minimal", "emoji", "ascii", "blocks"] = "minimal",
    level: int = logging.INFO,
    show_time: bool = True,
    show_path: bool = False
) -> None:
    """
    设置日志配置
    Args:
        style: 日志样式
            - minimal: 最简约的单行样式，适合高密度日志
            - compact: 紧凑型布局，适合一般日志记录
            - status: 状态栏风格，适合系统状态监控
            - notify: 通知风格，适合重要消息提醒
            - json: JSON风格，适合结构化数据
            - code: 代码风格，适合开发调试
            - error: 错误展示风格，适合异常追踪
            - metric: 指标风格，适合性能监控
        theme: 颜色主题
            - minimal: 最简约的颜色方案
            - dark: 深色主题
            - light: 浅色主题
            - colorful: 丰富多彩的主题
        icons: 图标集
            - minimal: 最简约的符号
            - emoji: emoji表情
            - ascii: ASCII字符
            - blocks: 方块字符
        level: 日志级别
        show_time: 是否显示时间
        show_path: 是否显示文件路径
    """
    # 更新管理器的当前配置
    logger_manager.current_style = style
    logger_manager.current_theme = theme
    logger_manager.current_icons = icons
    logger_manager.level = level
    logger_manager.show_time = show_time
    logger_manager.show_path = show_path
    
    # 确保在设置新的handler之前移除已有的handlers
    root = logging.getLogger()
    root.handlers = []
    
    # 样式映射
    handlers = {
        "minimal": MinimalHandler,
        "compact": CompactHandler,
        "status": StatusHandler,
        "notify": NotifyHandler,
        "json": JsonHandler,
        "code": CodeHandler,
        "error": ErrorHandler,
        "metric": MetricHandler
    }
    
    # 创建handler实例
    handler_class = handlers.get(style, CompactHandler)
    handler = handler_class(
        theme=theme,
        icons=icons,
        show_time=show_time,
        show_path=show_path,
        omit_repeated_times=False
    )
    
    # 配置日志
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[handler],
        force=True
    )

def time_logger(logger: Optional[logging.Logger] = None, 
               level: int = logging.INFO) -> Callable:
    """
    装饰器: 记录函数执行时间
    
    Args:
        logger: 日志记录器实例，如果为None则创建新实例
        level: 日志级别，默认为INFO
    
    Examples:
        @time_logger(level=logging.DEBUG)
        def slow_function():
            time.sleep(1)
            return "done"
            
        @time_logger()
        def process_data(items):
            for item in items:
                process(item)
    """
    def decorator(func: Callable) -> Callable:
        nonlocal logger
        
        if logger is None:
            logger = logging.getLogger(func.__module__)
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                log_message = f"函数 {func.__name__} 执行完成 - 耗时: {duration:.4f}s"
                logger.log(level, log_message)
                
                return result
            except Exception as e:
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                log_message = f"函数 {func.__name__} 执行失败 - 耗时: {duration:.4f}s - 错误: {str(e)}"
                logger.error(log_message)
                    
                raise
                    
        return wrapper
    return decorator



__all__ = [
    "setup_logging",
    "time_logger"
]


if __name__ == "__main__":
    import asyncio
    import random
    
    # 为不同测试创建专门的logger
    json_logger = logging.getLogger("aivk.test.json")
    metric_logger = logging.getLogger("aivk.test.metric")
    code_logger = logging.getLogger("aivk.test.code")
    status_logger = logging.getLogger("aivk.test.status")
    error_logger = logging.getLogger("aivk.test.error")
    
    # 添加装饰器测试用例
    @time_logger(logger=json_logger, level=logging.INFO)
    def test_json_style():
        time.sleep(0.5)
        return "JSON style test"
        
    @time_logger(logger=metric_logger, level=logging.INFO)
    def test_metric_style():
        time.sleep(0.3)
        data = {"processed": 100, "errors": 0}
        return data
        
    @time_logger(logger=code_logger, level=logging.DEBUG)
    def test_code_style():
        time.sleep(0.2)
        return "Code style test"
        
    @time_logger(logger=status_logger, level=logging.INFO)
    def test_status_style():
        time.sleep(0.4)
        return "Status style test"
        
    @time_logger(logger=error_logger, level=logging.ERROR)
    def test_error_style():
        time.sleep(0.1)
        raise ValueError("测试错误")
    
    async def test_styles():
        """测试所有日志样式"""
        # 样式和主题组合
        styles = ["minimal", "compact", "status", "notify", "json", "code", "error", "metric"]
        themes = ["minimal", "dark", "light", "colorful"]
        icon_sets = ["minimal", "emoji", "ascii", "blocks"]
        
        for style in styles:
            print(f"\n=== 测试 {style} 样式 ===\n")
            # 随机选择主题和图标集
            theme = random.choice(themes)
            icons = random.choice(icon_sets)
            
            setup_logging(style=style, theme=theme, icons=icons, level=logging.DEBUG)
            logger = logging.getLogger(f"aivk.test.{style}")
            
            # 根据不同样式生成适合的测试数据
            if style == "json":
                logger.debug({"action": "initialize", "status": "starting"})
                await asyncio.sleep(0.2)
                logger.info({"status": "running", "uptime": "00:00:01"})
                await asyncio.sleep(0.2)
                logger.warning({"alert": "high_memory", "usage": "85%"})
                await asyncio.sleep(0.2)
                logger.error({"error": "connection_failed", "retry": 3})
                await asyncio.sleep(0.2)
                logger.critical({"fatal": "system_crash", "code": "0xDEAD"})
            elif style == "metric":
                logger.debug({"cpu": "2%", "memory": "156MB", "disk": "45GB"})
                await asyncio.sleep(0.2)
                logger.info({"requests": 150, "response_time": "45ms"})
                await asyncio.sleep(0.2)
                logger.warning({"cpu": "75%", "memory": "1.8GB"})
                await asyncio.sleep(0.2)
                logger.error({"failed_requests": 5, "error_rate": "2.3%"})
                await asyncio.sleep(0.2)
                logger.critical({"cpu": "100%", "memory": "0MB"})
            elif style == "code":
                logger.debug("def initialize():\\n    print('Starting...')")
                await asyncio.sleep(0.2)
                logger.info("result = calculate_sum([1, 2, 3])\\nprint(f'Sum: {result}')")
                await asyncio.sleep(0.2)
                logger.warning("# Warning: Deprecated function used\\nold_function()")
                await asyncio.sleep(0.2)
                logger.error("try:\\n    raise ValueError('Invalid input')\\nexcept:\\n    pass")
                await asyncio.sleep(0.2)
                logger.critical("sys.exit('Fatal error occurred')")
            else:
                logger.debug("调试信息: 正在初始化系统...")
                await asyncio.sleep(0.2)
                logger.info("信息: 系统启动成功")
                await asyncio.sleep(0.2)
                logger.warning("警告: 检测到性能下降")
                await asyncio.sleep(0.2)
                logger.error("错误: 无法连接到数据库")
                await asyncio.sleep(0.2)
                logger.critical("严重: 系统崩溃")
            
            await asyncio.sleep(1)
            print("\n" + "="*50 + "\n")
    
    asyncio.run(test_styles())
    
    async def test_dynamic_styles():
        """测试动态切换日志样式"""
        logger = logging.getLogger("aivk.test")
        
        # 测试不同样式组合
        style_configs = [
            {"style": "minimal", "theme": "dark", "icons": "minimal"},
            {"style": "compact", "theme": "light", "icons": "emoji"},
            {"style": "status", "theme": "colorful", "icons": "blocks"},
            {"style": "notify", "theme": "minimal", "icons": "ascii"},
            {"style": "json", "theme": "dark", "icons": "minimal"},
            {"style": "code", "theme": "light", "icons": "emoji"},
            {"style": "error", "theme": "colorful", "icons": "blocks"},
            {"style": "metric", "theme": "minimal", "icons": "ascii"}
        ]
        
        for config in style_configs:
            print(f"\n=== 切换到 {config['style']} 样式 ===\n")
            logger_manager.switch_style(**config)
            
            # 输出测试日志
            if config["style"] in ["json", "metric"]:
                logger.debug({"action": "switch_style", "status": "success"})
                await asyncio.sleep(0.2)
                logger.info({"performance": "good", "latency": "45ms"})
                await asyncio.sleep(0.2)
                logger.warning({"warning": "high_load", "cpu": "85%"})
                await asyncio.sleep(0.2)
                logger.error({"error": "timeout", "duration": "5s"})
                await asyncio.sleep(0.2)
                logger.critical({"fatal": "crash", "code": "0xDEAD"})
            elif config["style"] == "code":
                logger.debug("def test_function():\\n    print('Testing...')")
                await asyncio.sleep(0.2)
                logger.info("result = process_data()\\nprint(result)")
                await asyncio.sleep(0.2)
                logger.warning("# Warning: Memory leak detected\\nfix_memory()")
                await asyncio.sleep(0.2)
                logger.error("raise Exception('Test failed')\\n")
                await asyncio.sleep(0.2)
                logger.critical("sys.exit(1)  # Fatal error")
            else:
                logger.debug("调试信息: 样式切换测试...")
                await asyncio.sleep(0.2)
                logger.info("信息: 切换成功")
                await asyncio.sleep(0.2)
                logger.warning("警告: 资源使用率上升")
                await asyncio.sleep(0.2)
                logger.error("错误: 操作超时")
                await asyncio.sleep(0.2)
                logger.critical("严重: 系统不响应")
            
            await asyncio.sleep(1)
            print("\n" + "="*50 + "\n")
            
        # 打印最终配置
        print("当前日志配置:")
        print(json.dumps(logger_manager.get_current_config(), indent=2, ensure_ascii=False))
    
    async def test_decorator():
        """测试时间装饰器"""
        print("\n=== 测试时间装饰器 ===\n")
        
        try:
            test_json_style()
            await asyncio.sleep(0.2)
            
            test_metric_style()
            await asyncio.sleep(0.2)
            
            test_code_style()
            await asyncio.sleep(0.2)
            
            test_status_style()
            await asyncio.sleep(0.2)
            
            test_error_style()
        except Exception:
            pass
            
        print("\n" + "="*50 + "\n")
    
    # 运行所有测试
    async def run_all_tests():
        await test_styles()
        await test_decorator()
    
    if __name__ == "__main__":
        asyncio.run(run_all_tests())
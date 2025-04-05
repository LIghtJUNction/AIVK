import asyncio
import os
import platform
import locale
from pathlib import Path
import logging
from datetime import datetime
import shutil
import time
from rich.console import Console

# 精简导入，只保留必要的组件
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from rich.text import Text
from rich.rule import Rule
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.columns import Columns
from rich.align import Align



try:
    from ..aivk import Entry
    from ..core import AivkRoot
    from .. import __version__, __author__, __BYE__, __SUCCESS__
except ImportError:
    from aivk.aivk import Entry
    from aivk.core import AivkRoot
    from aivk import __version__, __author__, __BYE__, __SUCCESS__


def setup_logging():
    """配置日志记录"""
    from rich.logging import RichHandler
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=True)]
    )

# 在CLI工具入口处调用
setup_logging()


def AIVK_ROOT(aivk_root: Path | str) -> Path:
    """确定AIVK根目录路径"""
    if aivk_root == "AIVK_ROOT":
        aivk_root = Path(os.environ.get("AIVK_ROOT", Path.home() / ".aivk")).absolute()
        print("AIVK_ROOT is set to", aivk_root)
    return Path(aivk_root).absolute()

# AIVK核心操作函数
async def init(aivk_root: Path | str) -> None:
    """初始化AIVK根目录"""
    aivk = await Entry.onInstall(aivk_root)
    return aivk
async def remove(aivk: AivkRoot | str | Path) -> None:
    """
    移除AIVK根目录
    
    注意：直接将aivk参数传递给Entry.onUninstall方法
    """
    # 添加logger
    logger = logging.getLogger("aivk.cli.remove")
    
    try:
        # 确保获取到的是有效的AivkRoot对象
        if isinstance(aivk, AivkRoot):
            # 直接传递到Entry._onUninstall绕过LKM.onUninstall方法的包装
            # 这样可以避免布尔值返回传递问题
            result = await Entry._onUninstall(aivk)
            return result
        elif isinstance(aivk, (str, Path)):
            # 如果是路径，先尝试挂载，然后移除
            logger.info(f"接收到路径参数，尝试先挂载: {aivk}")
            mounted_aivk = await Entry.onLoad(aivk)
            if mounted_aivk and isinstance(mounted_aivk, AivkRoot):
                # 同样直接调用_onUninstall方法
                result = await Entry._onUninstall(mounted_aivk)
                return result
            else:
                logger.error(f"无法挂载: {aivk}")
                return False
        else:
            logger.error(f"不支持的参数类型: {type(aivk)}")
            return False
    except Exception as e:
        logger.error(f"移除失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def mount(aivk_root: Path | str) -> None:
    """挂载AIVK根目录"""
    aivk = await Entry.onLoad(aivk_root)
    return aivk

async def unmount(aivk: AivkRoot) -> None:
    """取消挂载AIVK根目录"""
    await Entry.onUnload(aivk)


# 统一颜色主题 -materia design风格配色方案
AIVK_COLORS = {
    "primary": "#2196F3",        # 主要颜色，蓝色 (Blue 500)
    "secondary": "#673AB7",      # 次要颜色，深紫色 (Deep Purple 500)
    "accent": "#FF4081",         # 强调色，粉色 (Pink A200)
    "warning": "#FF9800",        # 警告色，橙色 (Orange 500)
    "error": "#F44336",          # 错误色，红色 (Red 500)
    "success": "#4CAF50",        # 成功色，绿色 (Green 500)
    "info": "#03A9F4",           # 信息色，浅蓝色 (Light Blue 500)
    "muted": "#9E9E9E",          # 暗淡色，灰色 (Grey 500)
    "text": "#FFFFFF",           # 文本色，白色
    "text_dark": "#212121",      # 深色文本，近黑色 (Grey 900)
    "text_secondary": "#757575", # 次要文本，深灰色 (Grey 600)
    "divider": "#BDBDBD",        # 分隔线，浅灰色 (Grey 400)
    "background": "#303030",     # 背景色，深灰色 (背景)
    "surface": "#424242",        # 表面色，稍浅灰色 (表面)
    "elevation": "#2f3438"       # 阴影色，用于表现高度
}

# 多语言支持
# 获取系统语言
def get_system_language():
    """
    获取系统语言并返回语言代码
    返回两字符语言代码: 'zh', 'en', 'ja', 'es', 'fr', 'de'
    """
    try:
        # 获取系统语言
        if platform.system() == 'Windows':
            import ctypes
            windll = ctypes.windll.kernel32
            # 获取系统UI语言
            lang_id = windll.GetUserDefaultUILanguage()
            # 转换为语言代码
            primary_lang_id = lang_id & 0x3FF
            # 映射语言ID到语言代码
            lang_map = {
                0x04: 'zh',  # 中文
                0x09: 'en',  # 英语
                0x11: 'ja',  # 日语
                0x0A: 'es',  # 西班牙语
                0x0C: 'fr',  # 法语
                0x07: 'de',  # 德语
            }
            return lang_map.get(primary_lang_id, 'en')
        else:
            # 对于非Windows系统，使用locale模块
            loc = locale.getdefaultlocale()[0]
            if loc:
                lang_code = loc.split('_')[0].lower()
                # 确保是我们支持的语言
                if lang_code in ['zh', 'en', 'ja', 'es', 'fr', 'de']:
                    return lang_code
    except Exception as e:
        logging.warning(f"获取系统语言失败: {e}")
    
    # 默认返回英语
    return 'en'

# 语言配置
class LanguageManager:
    """语言管理器，负责加载和提供多语言文本"""
    
    # 支持的语言列表
    SUPPORTED_LANGUAGES = {
        'zh': '简体中文',
        'en': 'English',
        'ja': '日本語',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch'
    }
    
    def __init__(self):
        # 默认从系统获取语言
        self.current_lang = get_system_language()
        # 翻译字典
        self.translations = {}
        # 加载翻译
        self._load_translations()
    
    def set_language(self, lang_code):
        """设置当前语言"""
        if lang_code in self.SUPPORTED_LANGUAGES:
            self.current_lang = lang_code
            return True
        return False
    
    def _load_translations(self):
        """加载所有语言的翻译"""
        # 英文翻译 (基础翻译)
        self.translations['en'] = {
            # 常用UI元素
            'title': 'AI Virtual Kernel',
            'menu_title': 'AIVK CLI Menu',
            'path': 'Path',
            'status': 'Status',
            'time': 'Time',
            'initialized': 'Initialized',
            'not_initialized': 'Not Initialized',
            'confirm': 'Confirm',
            'select': 'Select',
            'select_tip': 'Tip: Enter option number or first letter',
            'press_enter': 'Press Enter to continue',
            'invalid_selection': 'Invalid selection, please try again',
            'yes': 'Yes',
            'no': 'No',
            'cancel': 'Canceled',
            'bye': 'Goodbye! 👋',
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            
            # 菜单选项
            'option_change_root': 'Change AIVK Root Directory',
            'option_init': 'Initialize AIVK Root Directory',
            'option_remove': 'Remove AIVK Root Directory',
            'option_mount': 'Mount AIVK Root Directory',
            'option_unmount': 'Unmount AIVK Root Directory',
            'option_exit': 'Exit (q)',
            'option_language': 'Change Language(k)',
            
            # 子菜单选项
            'use_env_var': 'Use AIVK_ROOT Environment Variable',
            'use_default_path': 'Use Default Path',
            'manual_input': 'Manual Input Path',
            'use_current_dir': 'Use Current Directory',
            'env_var': 'Environment Variable',
            'current_dir': 'Current Directory',
            'setting_method': 'Select Setting Method',
            
            # 操作提示
            'setting_root_dir': 'Setting AIVK Root Directory...',
            'set_to': 'Set to',
            'init_target': 'Target',
            'delete_confirm': 'Type \'DELETE\' to confirm',
            'delete_warning': 'WARNING! Will delete all AIVK data in',
            'not_initialized_warning': 'Warning: Directory not initialized',
            'continue': 'Continue',
            'unmount_confirm': 'Confirm unmount',
            
            # 问候语
            'good_morning': 'Good Morning!',
            'good_afternoon': 'Good Afternoon!',
            'good_evening': 'Good Evening!',
            
            # 语言设置
            'language_setting': 'Language Setting',
            'current_language': 'Current Language',
            'select_language': 'Select Language',
            'language_changed': 'Language changed to',
            
            # 任务消息
            'mount_task': 'Mounting AIVK...',
            'unmount_task': 'Unmounting AIVK...',
            'init_task': 'Initializing AIVK...',
            'remove_task': 'Removing AIVK...',
            'mount_success': 'Mount successful',
            'unmount_success': 'Unmount successful',
            'task_error': 'Task Error',
            
            # 其他
            'version': 'Version',
            'author': 'Author',
            'env_var_set': 'Environment Variable Set',
            'env_var_not_set': 'AIVK_ROOT Environment Variable Not Set',
            'enter_path': 'Enter Path',
            'thanks_for_using': 'Thanks for using',
            'cli': 'CLI'
        }
        
        # 中文翻译
        self.translations['zh'] = {
            # 常用UI元素
            'title': 'AI虚拟内核',
            'menu_title': 'AIVK 命令行菜单',
            'path': '路径',
            'status': '状态',
            'time': '时间',
            'initialized': '已初始化',
            'not_initialized': '未初始化',
            'confirm': '确认',
            'select': '请选择',
            'select_tip': '提示: 输入选项编号或者选项首字母',
            'press_enter': '按回车继续',
            'invalid_selection': '无效选择，请重试',
            'yes': '是',
            'no': '否',
            'cancel': '已取消',
            'bye': '再见! 👋',
            'success': '成功',
            'error': '错误',
            'warning': '警告',
            
            # 菜单选项
            'option_change_root': '重新指定AIVK根目录',
            'option_init': '初始化AIVK根目录',
            'option_remove': '移除AIVK根目录',
            'option_mount': '挂载AIVK根目录',
            'option_unmount': '取消挂载AIVK根目录',
            'option_exit': '退出 (q)',
            'option_language': '切换语言(k)',
            
            # 子菜单选项
            'use_env_var': '使用环境变量AIVK_ROOT',
            'use_default_path': '使用默认路径',
            'manual_input': '手动输入路径',
            'use_current_dir': '使用当前目录',
            'env_var': '环境变量',
            'current_dir': '当前目录',
            'setting_method': '请选择设置方式',
            
            # 操作提示
            'setting_root_dir': '设置AIVK根目录中...',
            'set_to': '已设置为',
            'init_target': '目标',
            'delete_confirm': '输入\'DELETE\'确认',
            'delete_warning': '警告! 将删除以下目录的所有AIVK数据',
            'not_initialized_warning': '警告: 目录未初始化',
            'continue': '继续',
            'unmount_confirm': '确认取消挂载',
            
            # 问候语
            'good_morning': '早上好!',
            'good_afternoon': '下午好!',
            'good_evening': '晚上好!',
            
            # 语言设置
            'language_setting': '语言设置',
            'current_language': '当前语言',
            'select_language': '选择语言',
            'language_changed': '语言已更改为',
            
            # 任务消息
            'mount_task': '挂载AIVK...',
            'unmount_task': '取消挂载AIVK...',
            'init_task': '初始化AIVK...',
            'remove_task': '移除AIVK...',
            'mount_success': '挂载成功',
            'unmount_success': '已取消挂载',
            'task_error': '执行任务出错',
            
            # 其他
            'version': '版本',
            'author': '作者',
            'env_var_set': '环境变量已设置',
            'env_var_not_set': '未设置AIVK_ROOT环境变量',
            'enter_path': '请输入路径',
            'thanks_for_using': '感谢使用',
            'cli': '命令行界面'
        }
        
        # 添加其他语言的翻译
        # 日语翻译
        self.translations['ja'] = {
            # 基本UI要素
            'title': 'AI仮想カーネル',
            'menu_title': 'AIVK CLIメニュー',
            'path': 'パス',
            'status': 'ステータス',
            'time': '時間',
            'initialized': '初期化済み',
            'not_initialized': '未初期化',
            'confirm': '確認',
            'select': '選択してください',
            'select_tip': 'ヒント: オプション番号または最初の文字を入力してください',
            'press_enter': '続けるにはEnterを押してください',
            'invalid_selection': '無効な選択です。もう一度お試しください',
            'yes': 'はい',
            'no': 'いいえ',
            'cancel': 'キャンセルしました',
            'bye': 'さようなら! 👋',
            'success': '成功',
            'error': 'エラー',
            'warning': '警告',
            
            # メニューオプション
            'option_change_root': 'AIVKルートディレクトリを変更',
            'option_init': 'AIVKルートディレクトリを初期化',
            'option_remove': 'AIVKルートディレクトリを削除',
            'option_mount': 'AIVKルートディレクトリをマウント',
            'option_unmount': 'AIVKルートディレクトリをアンマウント',
            'option_exit': '終了 (q)',
            'option_language': '言語を変更(k)',
            
            # サブメニューオプション
            'use_env_var': 'AIVK_ROOT環境変数を使用',
            'use_default_path': 'デフォルトパスを使用',
            'manual_input': '手動でパスを入力',
            'use_current_dir': '現在のディレクトリを使用',
            'env_var': '環境変数',
            'current_dir': '現在のディレクトリ',
            'setting_method': '設定方法を選択',
            
            # 操作メッセージ
            'setting_root_dir': 'AIVKルートディレクトリを設定中...',
            'set_to': '設定先',
            'init_target': 'ターゲット',
            'delete_confirm': '\'DELETE\'と入力して確認',
            'delete_warning': '警告! 次のディレクトリのすべてのAIVKデータが削除されます',
            'not_initialized_warning': '警告: ディレクトリは初期化されていません',
            'continue': '続ける',
            'unmount_confirm': 'アンマウントを確認',
            
            # 挨拶
            'good_morning': 'おはようございます!',
            'good_afternoon': 'こんにちは!',
            'good_evening': 'こんばんは!',
            
            # 言語設定
            'language_setting': '言語設定',
            'current_language': '現在の言語',
            'select_language': '言語を選択',
            'language_changed': '言語が次に変更されました',
            
            # タスクメッセージ
            'mount_task': 'AIVKをマウント中...',
            'unmount_task': 'AIVKをアンマウント中...',
            'init_task': 'AIVKを初期化中...',
            'remove_task': 'AIVKを削除中...',
            'mount_success': 'マウント成功',
            'unmount_success': 'アンマウント成功',
            'task_error': 'タスクエラー',
            
            # その他
            'version': 'バージョン',
            'author': '作者',
            'env_var_set': '環境変数が設定されています',
            'env_var_not_set': 'AIVK_ROOT環境変数が設定されていません',
            'enter_path': 'パスを入力してください',
            'thanks_for_using': 'ご利用ありがとうございます',
            'cli': 'CLI'
        }
        
        # 添加其他语言...（简化示例，可根据需要扩展）
        # 西班牙语，法语，德语等可以按照相同模式添加
        
    def get_text(self, key, lang=None):
        """获取翻译文本"""
        if not lang:
            lang = self.current_lang
        
        # 如果请求的语言没有翻译，回退到英语
        if lang not in self.translations:
            lang = 'en'
        
        # 获取翻译，如果不存在则回退到英语
        return self.translations[lang].get(key, self.translations['en'].get(key, key))
    
    def get_language_name(self, lang_code=None):
        """获取语言名称"""
        if not lang_code:
            lang_code = self.current_lang
        return self.SUPPORTED_LANGUAGES.get(lang_code, 'Unknown')

# 初始化语言管理器
language_manager = LanguageManager()

# 获取文本的便捷函数
def _(key):
    """获取当前语言的文本"""
    return language_manager.get_text(key)


# 简化的UI组件和辅助函数
COLORED_AIVK_LOGO = Text.assemble(
    Text("     _      ___  __     __  _  __\n", style="bold cyan"),
    Text("    / \\    ", style="bold cyan"), Text("|_ _| ", style="bold yellow"), Text("\\ \\   / / ", style="bold green"), Text("| |/ /\n", style="bold blue"),
    Text("   / _ \\    ", style="bold cyan"), Text("| |   ", style="bold yellow"), Text("\\ \\ / /  ", style="bold green"), Text("| ' / \n", style="bold blue"),
    Text("  / ___ \\   ", style="bold cyan"), Text("| |   ", style="bold yellow"), Text(" \\ V /   ", style="bold green"), Text("| . \\ \n", style="bold blue"),
    Text(" /_/   \\_\\ ", style="bold cyan"), Text("|___|  ", style="bold yellow"), Text("  \\_/    ", style="bold green"), Text("|_|\\_\\\n", style="bold blue"),
)

# 更小更紧凑的logo，移除不必要的换行符
MINI_AIVK_LOGO = Text.assemble(
    Text("  _   ___ __   __ _  __", style="bold cyan"),
    Text(" / \\ ", style="bold cyan"), Text("|_ _|", style="bold yellow"), Text(" \\ \\ / /", style="bold green"), Text(" |/ /", style="bold blue"),
    Text(" | | ", style="bold cyan"), Text(" | | ", style="bold yellow"), Text(" \\ V / ", style="bold green"), Text(" ' / ", style="bold blue"),
    Text(" |_| ", style="bold cyan"), Text("|___|", style="bold yellow"), Text("  \\_/  ", style="bold green"), Text("|_\\_\\", style="bold blue")
)

# 更美观的AIVK标志，使用新的配色方案
AIVK_LOGO = Text.assemble(
    Text("   █████╗ ██╗██╗   ██╗██╗  ██╗\n", style=f"bold {AIVK_COLORS['primary']}"),
    Text("  ██╔══██╗██║██║   ██║██║ ██╔╝\n", style=f"bold {AIVK_COLORS['primary']}"),
    Text("  ███████║██║██║   ██║█████╔╝ \n", style=f"bold {AIVK_COLORS['accent']}"),
    Text("  ██╔══██║██║╚██╗ ██╔╝██╔═██╗ \n", style=f"bold {AIVK_COLORS['accent']}"),
    Text("  ██║  ██║██║ ╚████╔╝ ██║  ██╗\n", style=f"bold {AIVK_COLORS['secondary']}"),
    Text("  ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═╝  ╚═╝\n", style=f"bold {AIVK_COLORS['secondary']}"),
)

# 紧凑型LOGO用于小终端，使用新的配色方案
COMPACT_LOGO = Text.assemble(
    Text("╭─────────────────────────╮\n", style=AIVK_COLORS["primary"]),
    Text("│ ", style=AIVK_COLORS["primary"]), Text("A", style=f"bold {AIVK_COLORS['primary']}"), 
    Text("I ", style=f"bold {AIVK_COLORS['accent']}"), 
    Text("V", style=f"bold {AIVK_COLORS['secondary']}"), Text("irtual ", style=AIVK_COLORS["text"]), 
    Text("K", style=f"bold {AIVK_COLORS['primary']}"), Text("ernel ", style=AIVK_COLORS["text"]), Text("│\n", style=AIVK_COLORS["primary"]),
    Text("╰─────────────────────────╯", style=AIVK_COLORS["primary"]),
)

#materia design主题面板样式
def md_panel(content, title=None, padding=(1, 2), border_style=None):
    """创建符合材料设计风格的面板"""
    if border_style is None:
        border_style = AIVK_COLORS["primary"]
    
    return Panel(
        content,
        title=title,
        title_align="left",
        border_style=border_style,
        padding=padding,
        box=box.ROUNDED
    )

def clear_screen():
    """清空终端屏幕，兼容不同操作系统"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_time_greeting():
    """基于当前时间返回美化的问候语"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return Panel(
            Align.center(f"[bold]{_('good_morning')}[/bold]"),
            border_style=AIVK_COLORS["success"],
            expand=False
        )
    elif 12 <= hour < 18:
        return Panel(
            Align.center(f"[bold]{_('good_afternoon')}[/bold]"),
            border_style=AIVK_COLORS["accent"],
            expand=False
        )
    else:
        return Panel(
            Align.center(f"[bold]{_('good_evening')}[/bold]"),
            border_style=AIVK_COLORS["info"],
            expand=False
        )


async def execute_task(console, message, action_func, args=None):
    """使用进度动画执行任务并返回操作函数的结果"""
    # 创建具有动画效果的进度条
    progress = Progress(
        SpinnerColumn(),  # 添加旋转动画
        TextColumn(f"[bold {AIVK_COLORS['primary']}]{{task.description}}[/bold {AIVK_COLORS['primary']}]"),  # 修复格式字符串
        BarColumn(complete_style=AIVK_COLORS["accent"]),  # 进度条
        TaskProgressColumn(),  # 显示百分比进度
        expand=True  # 允许进度条扩展填充可用空间
    )
    
    try:
        with progress:
            # 添加任务到进度条
            task_id = progress.add_task(f"{message}", total=100)
            
            # 更新进度到30%表示准备中
            # 这是一种视觉反馈，让用户知道任务已经开始
            progress.update(task_id, completed=30)
            
            # 执行实际操作
            try:
                result = None
                if args:
                    result = await action_func(*args)  # 如果有参数，传入参数执行
                else:
                    result = await action_func()  # 无参数执行
                    
                # 操作成功，完成进度
                progress.update(task_id, completed=100)  # 显示100%完成
                return result  # 返回操作函数的实际结果，而不是布尔值
            except Exception as e:
                # 操作失败，显示错误
                # 使用错误颜色显示失败信息
                progress.update(task_id, description=f"{_('error')}: {str(e)}")
                progress.update(task_id, completed=100)  # 确保进度条完成
                raise e  # 重新抛出异常以便上层处理
    except Exception as e:
        # 如果progress本身出错，直接打印错误信息
        console.print(f"[bold {AIVK_COLORS['error']}]{_('task_error')}: {str(e)}[/bold {AIVK_COLORS['error']}]")
        return None

def get_directory_info(dir_path):
    """获取目录信息统计"""
    if not dir_path.exists() or not dir_path.is_dir():
        return None
    
    try:
        stats = {
            "total_files": 0,
            "total_dirs": 0,
            "total_size": 0,
            "is_initialized": (dir_path / ".aivk").exists(),
            "items": []
        }
        
        for item in dir_path.glob("**/*"):
            if item.is_file():
                stats["total_files"] += 1
                stats["total_size"] += item.stat().st_size
            elif item.is_dir():
                stats["total_dirs"] += 1
        
        # 获取根目录内容
        for item in dir_path.iterdir():
            item_info = {
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None,
                "mod_time": datetime.fromtimestamp(item.stat().st_mtime)
            }
            stats["items"].append(item_info)
        
        return stats
    except Exception:
        return None


def aivk_confirm(message, console, default=True):
    """美化的确认提示"""
    default_str = "Y/n" if default else "y/N"
    styled_message = f"[bold {AIVK_COLORS['primary']}]{message}[/bold {AIVK_COLORS['primary']}]"
    
    # 创建一个包含确认消息的面板
    confirm_panel = Panel(
        f"{styled_message} [{AIVK_COLORS['accent']}]{default_str}[/{AIVK_COLORS['accent']}]",
        title=_("confirm"),
        title_align="left",
        border_style=AIVK_COLORS["secondary"],
        padding=(1, 2)
    )
    
    console.print(confirm_panel)
    response = console.input().strip().lower()
    
    if not response:
        return default
    
    return response.startswith('y')

# 使用更兼容的列表选择器
def choose_option(console, title, options, choices=None):
    """显示美化的选项列表并等待用户选择"""
    # 创建选项表格
    option_table = Table(
        show_header=False,
        box=box.ROUNDED,
        border_style=AIVK_COLORS["secondary"],
        show_edge=True,
        padding=(0, 1),
        expand=False
    )
    
    option_table.add_column("Key", style=f"bold {AIVK_COLORS['accent']}", justify="center", width=6)
    option_table.add_column("Option", style=AIVK_COLORS["text"])
    
    # 如果提供了选项对应的值
    if choices is None:
        choices = [str(i) for i in range(len(options))]
    
    # 添加选项到表格
    for i, option in enumerate(options):
        option_table.add_row(f"[{choices[i]}]", option)
    
    # 创建包含表格的面板
    menu_panel = Panel(
        option_table,
        title=f"[bold {AIVK_COLORS['primary']}]{title}[/bold {AIVK_COLORS['primary']}]",
        border_style=AIVK_COLORS["primary"],
        padding=(1, 1)
    )
    
    console.print(menu_panel)
    console.print(f"[{AIVK_COLORS['muted']}]{_('select_tip')}[/{AIVK_COLORS['muted']}]")
    
    # 获取选择
    # 创建有效输入映射：数字、首字母（大小写均可）
    valid_inputs = {}
    
    # 添加数字选项
    for i, choice in enumerate(choices):
        valid_inputs[choice] = choice  # 直接选择
        
        # 添加首字母选择方式（如果选项是字母或字符串）
        if isinstance(choice, str) and len(choice) > 0:
            valid_inputs[choice[0].lower()] = choice  # 小写首字母
            valid_inputs[choice[0].upper()] = choice  # 大写首字母
    
    # 处理用户输入
    while True:
        choice_input = console.input(f"[bold {AIVK_COLORS['accent']}]{_('select')}: [/bold {AIVK_COLORS['accent']}]").strip()
        
        # 检查输入是否在有效选项中
        if choice_input in valid_inputs:
            return valid_inputs[choice_input]
        
        # 检查输入是否为索引
        try:
            index = int(choice_input)
            if 0 <= index < len(choices):
                return choices[index]
        except ValueError:
            pass
        
        # 允许直接回车选择第一个选项
        if not choice_input and len(options) > 0:
            return choices[0]
        
        console.print(f"[{AIVK_COLORS['error']}]{_('invalid_selection')}[/{AIVK_COLORS['error']}]")


# 添加语言设置功能
def change_language(console):
    """更改语言设置"""
    clear_screen()
    
    # 显示语言设置面板
    console.print(md_panel(
        f"[bold]{_('current_language')}:[/bold] {language_manager.get_language_name()}",
        title=_('language_setting'),
        border_style=AIVK_COLORS["info"]
    ))
    
    # 创建语言选项
    lang_options = [
        f"[{AIVK_COLORS['text']}]{name} ({code})[/{AIVK_COLORS['text']}]" 
        for code, name in language_manager.SUPPORTED_LANGUAGES.items()
    ]
    # 为每种语言创建一个数字标识符
    lang_codes = list(language_manager.SUPPORTED_LANGUAGES.keys())
    number_choices = [str(i) for i in range(len(lang_codes))]
    
    # 获取用户选择 - 使用数字标识符而不是语言代码
    choice_index = choose_option(console, _('select_language'), lang_options, number_choices)
    # 将选择的索引转换为实际语言代码
    selected_lang = lang_codes[int(choice_index)]
    
    # 设置新语言
    language_manager.set_language(selected_lang)
    console.print(f"[{AIVK_COLORS['success']}]{_('language_changed')} {language_manager.get_language_name(selected_lang)}[/{AIVK_COLORS['success']}]")
    
    time.sleep(1)  # 给用户时间看到确认消息


async def menu(console: Console) -> None:
    """显示美化的AIVK菜单"""
    # 使用Layout创建页面布局
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=6),
        Layout(name="body", ratio=1)
    )
    
    # 获取时间问候
    greeting = get_time_greeting()
    
    # 渲染美化的标题区域
    header_panel = Panel(
        Align.center(
            Columns([
                AIVK_LOGO,
                Align.center(
                    Text.assemble(
                        Text(f"{_('version')}: v{__version__}\n", style=f"bold {AIVK_COLORS['accent']}"),
                        Text(f"{_('author')}: {__author__}\n", style=AIVK_COLORS["info"]),
                        Text(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}", style=AIVK_COLORS["muted"])
                    )
                )
            ], expand=True),
        ),
        title=f"[bold {AIVK_COLORS['primary']}]AI Virtual Kernel[/bold {AIVK_COLORS['primary']}]",
        border_style=AIVK_COLORS["primary"],
        padding=(1, 2)
    )
    
    layout["header"].update(header_panel)
    
    # 添加问候语到布局 - 实际使用greeting变量
    layout["header"].update(greeting)
    
    # 渲染布局
    console.print(layout)
    
    # 获取AIVK根目录
    current_dir = Path.cwd()
    
    if "AIVK_ROOT" in os.environ:
        aivk_root = Path(os.environ["AIVK_ROOT"])
        console.print(Panel(
            f"{_('env_var_set')}: [bold {AIVK_COLORS['success']}]{aivk_root}[/bold {AIVK_COLORS['success']}]",
            title="AIVK_ROOT",
            border_style=AIVK_COLORS["success"],
            padding=(1, 2)
        ))
    else:
        console.print(Panel(
            f"[{AIVK_COLORS['warning']}] {_('env_var_not_set')}[/{AIVK_COLORS['warning']}]\n"
            f"{_('current_dir')}: [{AIVK_COLORS['info']}]{current_dir}[/{AIVK_COLORS['info']}]",
            title=_('setting_method'),
            border_style=AIVK_COLORS["warning"],
            padding=(1, 2)
        ))
        
        input_path = Prompt.ask(
            f"[bold {AIVK_COLORS['primary']}] {_('enter_path')}[/bold {AIVK_COLORS['primary']}]",
            default=str(current_dir),
            show_default=True
        )
        aivk_root = Path(input_path).absolute()
    
    # 主菜单循环
    while True:
        clear_screen()
        
        # 状态标志
        is_initialized = aivk_root.exists() and (aivk_root / ".aivk").exists()
        status_style = AIVK_COLORS["success"] if is_initialized else AIVK_COLORS["warning"]
        status_text = _("initialized") if is_initialized else _("not_initialized")
        
        # 紧凑型标题
        console.print(COMPACT_LOGO)
        console.print(Panel(
            Columns([
                f"[bold]{_('path')}:[/bold] [{AIVK_COLORS['info']}]{aivk_root}[/{AIVK_COLORS['info']}]",
                f"[bold]{_('status')}:[/bold] [bold {status_style}]{status_text}[/bold {status_style}]",
                f"[bold]{_('time')}:[/bold] [{AIVK_COLORS['muted']}]{datetime.now().strftime('%H:%M:%S')}[/{AIVK_COLORS['muted']}]"
            ], expand=True),
            border_style=AIVK_COLORS["secondary"],
            padding=(0, 1)
        ))
        
        # 创建更美观的菜单选项 - 确保文字在各种终端都可见
        menu_options = [
            f"[bold {AIVK_COLORS['warning']}]{_('option_change_root')}[/bold {AIVK_COLORS['warning']}]",
            f"[bold {AIVK_COLORS['success']}]{_('option_init')}[/bold {AIVK_COLORS['success']}]",
            f"[bold {AIVK_COLORS['error']}]{_('option_remove')}[/bold {AIVK_COLORS['error']}]",
            f"[bold {AIVK_COLORS['info']}]{_('option_mount')}[/bold {AIVK_COLORS['info']}]",
            f"[bold {AIVK_COLORS['primary']}]{_('option_unmount')}[/bold {AIVK_COLORS['primary']}]",
            f"[bold {AIVK_COLORS['error']}]{_('option_exit')}[/bold {AIVK_COLORS['error']}]",
            f"[bold {AIVK_COLORS['info']}]{_('option_language')}[/bold {AIVK_COLORS['info']}]"
        ]
        
        # 选项标识符列表
        choices = ["0", "1", "2", "3", "4", "q", "k"]
        
        # 使用更美观的选择方法
        choice = choose_option(
            console,
            _("menu_title"),
            menu_options,
            choices
        )
        
        # 处理菜单选择...
        # 保持原有的菜单处理逻辑

        # 处理选择
        """
        README
        如果不先使用init或者mount，直接使用unmount会报错
        因为缺少挂载后才能获取到的AivkRoot实例
        这样的设计是为了避免不必要的错误
        确保流程正确
        """

        if choice == "0":  # 重新指定AIVK根目录
            clear_screen()
            console.print(Panel(
                f"[bold]{_('option_change_root')}[/bold]", 
                border_style=AIVK_COLORS["warning"],
                padding=(1, 2)
            ))
            
            # 显示选项 - 更美观的展示
            submenus = [
                f"[{AIVK_COLORS['success']}] {_('use_env_var')}[/{AIVK_COLORS['success']}]",
                f"[{AIVK_COLORS['info']}] {_('use_default_path')}[/{AIVK_COLORS['info']}]",
                f"[{AIVK_COLORS['info']}] {_('manual_input')}[/{AIVK_COLORS['info']}]",
                f"[{AIVK_COLORS['warning']}] {_('use_current_dir')}[/{AIVK_COLORS['warning']}]"
            ]
            
            # 使用面板显示当前信息
            console.print(Panel(
                Columns([
                    f"{_('env_var')}: [{AIVK_COLORS['success']}]{os.environ.get('AIVK_ROOT', _('env_var_not_set'))}[/{AIVK_COLORS['success']}]",
                    f"{_('current_dir')}: [{AIVK_COLORS['warning']}]{current_dir}[/{AIVK_COLORS['warning']}]"
                ]),
                border_style=AIVK_COLORS["secondary"],
                padding=(1, 2)
            ))
            
            # 获取用户选择 - 修复选项数量不匹配的问题
            subchoice = choose_option(console, _('setting_method'), submenus, ["1", "2", "3", "4"])
            
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn(f"[bold blue]{_('setting_root_dir')}[/bold blue]"),
                transient=True
            ) as progress:
                progress.add_task("setting", total=100)
                
                if subchoice == "1" and "AIVK_ROOT" in os.environ:
                    aivk_root = Path(os.environ["AIVK_ROOT"])
                elif subchoice == "2":
                    # 使用默认路径
                    aivk_root = Path.home() / ".aivk"
                elif subchoice == "3":
                    input_path = Prompt.ask(_("enter_path"), default=str(aivk_root))
                    aivk_root = Path(input_path).absolute()
                else:  # 选择3或默认
                    aivk_root = current_dir
            
            console.print(Panel(
                f"{_('set_to')}: [bold {AIVK_COLORS['success']}]{aivk_root}[/bold {AIVK_COLORS['success']}]",
                border_style=AIVK_COLORS["success"],
                padding=(1, 2)
            ))
            Prompt.ask(_("press_enter"), password=True)
        
        elif choice == "1":  # 初始化AIVK
            clear_screen()
            console.print(f"[bold {AIVK_COLORS['success']}] {_('option_init')}[/bold {AIVK_COLORS['success']}]")
            console.print(Rule(style=AIVK_COLORS["success"]))
            
            # 检查目录状态与确认操作 - 紧凑显示
            is_initialized = aivk_root.exists() and (aivk_root / ".aivk").exists()
            console.print(f"{_('init_target')}: [{AIVK_COLORS['success'] if is_initialized else AIVK_COLORS['warning']}] {aivk_root}[/] | {_('status')}: " + (f"[{AIVK_COLORS['success']}] {_('initialized')}[/]" if is_initialized else f"[{AIVK_COLORS['warning']}] {_('not_initialized')}[/]"))
                
            if aivk_confirm(_("confirm"), console, default=True):
                aivk = await execute_task(console, f"CLI_INIT:{_('init_task')} {aivk_root}", init, [aivk_root])
                console.print(f"\n{__SUCCESS__}")
            else:
                console.print(f"[{AIVK_COLORS['warning']}] {_('cancel')}[/]")
            
            Prompt.ask(_("press_enter"), password=True)
        
        elif choice == "2":  # 移除AIVK - 极简紧凑显示
            clear_screen()
            console.print(f"[bold {AIVK_COLORS['error']}] {_('option_remove')}[/bold {AIVK_COLORS['error']}]")
            console.print(Rule(style=AIVK_COLORS["error"]))
            
            console.print(f"[bold {AIVK_COLORS['error']}] {_('delete_warning')} [yellow]{aivk_root}[/yellow]")
            
            if aivk_confirm(f"[bold {AIVK_COLORS['error']}] {_('confirm')}[/bold {AIVK_COLORS['error']}]", console, default=False):

                try:
                    await execute_task(console, f"CLI_REMOVE:{_('remove_task')} {aivk_root}", remove, [aivk])
                except Exception as e:
                    console.print(f"[bold {AIVK_COLORS['error']}]移除失败: {str(e)}[/bold {AIVK_COLORS['error']}]")
                    console.print("尝试直接删除目录...")

                if Prompt.ask(_("delete_confirm")).upper() == "DELETE":
                    shutil.rmtree(aivk_root, ignore_errors=True)

                    console.print(f"[bold {AIVK_COLORS['error']}] {__BYE__}[/bold {AIVK_COLORS['error']}]")
                else:
                    console.print(f"[{AIVK_COLORS['warning']}] {_('cancel')}[/]")
            else:
                console.print(f"[{AIVK_COLORS['warning']}] {_('cancel')}[/]")
            
            Prompt.ask(_("press_enter"), password=True)

        elif choice == "3":  # 挂载AIVK - 极简紧凑显示
            clear_screen()
            console.print(f"[bold {AIVK_COLORS['info']}] {_('option_mount')}[/bold {AIVK_COLORS['info']}]")
            console.print(Rule(style=AIVK_COLORS["info"]))
            
            console.print(f"{_('init_target')}: [{AIVK_COLORS['info']}] {aivk_root}[/]")
            
            initialized = aivk_root.exists() and (aivk_root / ".aivk").exists()
            if not initialized:
                console.print(f"[{AIVK_COLORS['warning']}] {_('not_initialized_warning')}[/]")
                if not aivk_confirm(_("continue"), console, default=False):
                    continue
            
            aivk = await execute_task(console, f"CLI_MOUNT:{_('mount_task')} {aivk_root}", mount, [aivk_root])
            console.print(f"[bold {AIVK_COLORS['info']}] {_('mount_success')}[/bold {AIVK_COLORS['info']}]")
            
            Prompt.ask(_("press_enter"), password=True)
        
        elif choice == "4":  # 取消挂载AIVK - 极简显示
            clear_screen()
            console.print(f"[bold {AIVK_COLORS['primary']}] {_('option_unmount')}[/bold {AIVK_COLORS['primary']}]")
            console.print(Rule(style=AIVK_COLORS["primary"]))
            
            console.print(f"{_('init_target')}: [{AIVK_COLORS['primary']}] {aivk_root}[/]")
            if aivk_confirm(_("unmount_confirm"), console, default=True):
                try:
                    await execute_task(console, f"CLI_UNMOUNT:{_('unmount_task')} {aivk_root}", unmount, [aivk])
                    console.print(f"[bold {AIVK_COLORS['primary']}] {_('unmount_success')}[/bold {AIVK_COLORS['primary']}]")
                except Exception as e:
                    console.print(f"[bold red]取消挂载失败: {str(e)}[/bold red]")
                    console.print("你必须先初始化或挂载AIVK后才能取消挂载")
                
            else:
                console.print(f"[{AIVK_COLORS['warning']}] {_('cancel')}[/]")
            
            Prompt.ask(_("press_enter"), password=True)
        
        elif choice == "q":  # 退出 - 美化版
            clear_screen()
            
            # 创建动画效果的再见消息
            with Live(refresh_per_second=10) as live:
                for i in range(5):
                    # 不断变化的边框颜色
                    live.update(Panel(
                        Align.center(
                            Text.assemble(
                                Text(f"\n{_('thanks_for_using')} ", style="bold white"),
                                Text("AIVK", style=f"bold {AIVK_COLORS['primary' if i % 2 == 0 else 'accent']}"),
                                Text(f" {_('cli')}!\n\n", style="bold white"),
                                Text(f"{_('bye')}", style="bold yellow"),
                                Text("\n")
                            )
                        ),
                        border_style=AIVK_COLORS["primary" if i % 2 == 0 else "secondary"],
                        padding=(1, 4)
                    ))
                    time.sleep(0.3)
            break
        
        elif choice == "k":  # 更改语言
            change_language(console)


async def main_async() -> None:
    """异步主函数"""
    console = Console()
    
    # 参数解析
    import argparse
    parser = argparse.ArgumentParser(description="AIVK - AI Virtual Kernel CLI")
    parser.add_argument('-v', '--version', action='version', version=__version__, help='显示版本信息')
    parser.add_argument('-i', '--init', type=str, help='初始化AIVK根目录')
    parser.add_argument('-m', '--mount', type=str, help='挂载AIVK根目录')
    parser.add_argument('-r', '--remove', type=str, help='移除AIVK根目录')
    parser.add_argument('-u', '--unmount', type=str, help='取消挂载AIVK根目录')
    args = parser.parse_args()

    if args.init:
        # 初始化
        aivk_root = AIVK_ROOT(args.init)
        try:
            await execute_task(console, f"AIVK -i {aivk_root}...", init, [aivk_root])
            console.print(f"[bold green]已初始化 {aivk_root}[/bold green]")
            console.print(f"[bold green]{__SUCCESS__}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]初始化失败: {str(e)}[/bold red]")
    
    elif args.remove:
        # 移除 - 修复：先挂载再移除
        aivk_root = AIVK_ROOT(args.remove)
        try:
            # 先尝试挂载该目录
            aivk = await execute_task(console, f"AIVK -m {aivk_root}...", mount, [aivk_root])
            # 然后删除
            await execute_task(console, f"AIVK -r {aivk_root}...", remove, [aivk])
            console.print("[bold red]已移除[/bold red]")
            console.print(f"[bold red]{__BYE__}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]移除失败: {str(e)}[/bold red]")
    
    elif args.mount:
        # 挂载
        aivk_root = AIVK_ROOT(args.mount)
        await execute_task(console, f"AIVK -m {aivk_root}...", mount, [aivk_root])
        console.print(f"[bold blue]已挂载 {aivk_root}[/bold blue]")
    
    elif args.unmount:
        # 取消挂载 (新增)
        aivk_root = AIVK_ROOT(args.unmount)
        try:
            # 先尝试挂载该目录以获取AivkRoot对象
            aivk = await execute_task(console, f"AIVK -m {aivk_root}...", mount, [aivk_root])
            # 然后取消挂载
            await execute_task(console, f"AIVK -u {aivk_root}...", unmount, [aivk])
            console.print(f"[bold cyan]已取消挂载 {aivk_root}[/bold cyan]")
        except Exception as e:
            console.print(f"[bold red]取消挂载失败: {str(e)}[/bold red]")
    
    else:
        # 无参数时显示菜单
        await menu(console)


def main():
    """非异步入口点函数"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    main()
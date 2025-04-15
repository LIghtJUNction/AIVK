"""
工具类模块，包含 AIVK 使用的通用工具函数和类
"""

import os
import sys
import subprocess
import shlex
import asyncio
import time
import platform
import logging
from typing import Optional, List, Dict, Union, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
import threading


class CommandStatus(Enum):
    """命令执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    TERMINATED = "terminated"


@dataclass
class CommandResult:
    """命令执行结果数据类"""
    command: str
    status: CommandStatus
    stdout: str = ""
    stderr: str = ""
    return_code: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[Exception] = None
    
    @property
    def execution_time(self) -> Optional[float]:
        """计算命令执行耗时（秒）"""
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        return None

    @property
    def is_successful(self) -> bool:
        """检查命令是否成功执行"""
        return self.status == CommandStatus.COMPLETED and self.return_code == 0

    def __str__(self) -> str:
        """字符串表示"""
        status_str = f"状态: {self.status.value}"
        time_str = f", 耗时: {self.execution_time:.2f}秒" if self.execution_time is not None else ""
        code_str = f", 返回码: {self.return_code}" if self.return_code is not None else ""
        return f"命令 '{self.command}' - {status_str}{time_str}{code_str}"


class AivkExecuter:
    """
    全能命令执行器
    
    提供同步和异步执行系统命令的功能，支持超时设置、错误处理和命令输出捕获。
    """
    
    # 默认类级别的logger
    _default_logger = None
    
    @classmethod
    def get_default_logger(cls) -> logging.Logger:
        """获取默认的日志记录器"""
        if cls._default_logger is None:
            cls._default_logger = logging.getLogger(__name__)
        return cls._default_logger
    
    @classmethod
    def _parse_command(cls, command: Union[str, List[str]], shell: bool) -> Union[str, List[str]]:
        """
        解析命令，确保命令格式正确
        
        Args:
            command: 要执行的命令，可以是字符串或列表
            shell: 是否在shell中执行
            
        Returns:
            命令字符串或列表，取决于shell参数
        """
        if shell:
            return command if isinstance(command, str) else " ".join(command)
        else:
            if isinstance(command, str):
                return shlex.split(command)
            return command
            
    
    @classmethod
    def exec(cls, 
             command: Union[str, List[str]], 
             timeout: Optional[float] = None,
             shell: bool = False,
             cwd: Optional[str] = None,
             env: Optional[Dict[str, str]] = None,
             encoding: str = 'utf-8',
             errors: str = 'replace',
             stream_output: bool = False,
             callback: Optional[Callable[[str], None]] = None,
             logger: Optional[logging.Logger] = None,
             new_process: bool = False,
             use_daemon_thread: bool = False) -> CommandResult:
        """
        同步执行命令
        
        Args:
            command: 要执行的命令，可以是字符串或参数列表
            timeout: 超时时间（秒），None 表示不设置超时
            shell: 是否在 shell 中执行命令
            cwd: 命令执行的工作目录
            env: 环境变量字典
            encoding: 输出编码
            errors: 编码错误处理方式
            stream_output: 是否流式处理输出（实时打印）
            callback: 输出回调函数，每当有新输出时调用
            logger: 日志记录器，不提供则使用默认日志记录器
            new_process: 是否在新进程中执行命令（解决终端状态异常问题）
            use_daemon_thread: 是否使用守护线程（防止主线程等待）
            
        Returns:
            CommandResult: 命令执行结果对象
        """
        logger = logger or cls.get_default_logger()
        cmd = cls._parse_command(command, shell)
        cmd_str = command if isinstance(command, str) else " ".join(command)
        is_windows = platform.system() == "Windows"
        
        result = CommandResult(command=cmd_str, status=CommandStatus.PENDING)
        result.start_time = time.time()
        
        logger.debug(f"执行命令: {cmd_str}")
        
        # 如果需要在新进程中执行
        if new_process:
            logger.debug(f"在新进程中运行命令: {cmd_str}")
            
            # 准备环境变量
            merged_env = None
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env)
            else:
                merged_env = os.environ.copy()
                
            try:
                if is_windows:
                    # Windows 平台创建独立进程
                    # 使用 CREATE_NEW_CONSOLE 标志创建一个新的控制台窗口
                    process = subprocess.Popen(
                        cmd,
                        cwd=cwd,
                        env=merged_env,
                        shell=shell,
                        creationflags=subprocess.CREATE_NEW_CONSOLE
                    )
                else:
                    # Unix 平台创建独立进程
                    process = subprocess.Popen(
                        cmd,
                        cwd=cwd,
                        env=merged_env,
                        shell=shell
                    )
                
                # 进程 ID
                pid = process.pid
                logger.info(f"在新进程中启动命令成功，PID: {pid}")
                
                # 等待进程完成
                try:
                    return_code = process.wait(timeout=timeout)
                    result.return_code = return_code
                    if return_code == 0:
                        result.status = CommandStatus.COMPLETED
                    else:
                        result.status = CommandStatus.FAILED
                        
                except subprocess.TimeoutExpired:
                    # 超时处理
                    cls._terminate_process(process, is_windows, logger)
                    result.status = CommandStatus.TIMEOUT
                    result.error = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
                    
            except Exception as e:
                result.status = CommandStatus.FAILED
                result.error = e
                logger.exception(f"在新进程中执行命令出错: {cmd_str}")
            
            result.end_time = time.time()
            return result
            
        # 使用守护线程执行
        if use_daemon_thread:
            logger.debug(f"使用守护线程模式执行命令: {cmd_str}")
            
            # 准备环境变量
            merged_env = None
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env) if env else None
            
            # 结果容器，用于线程间通信
            result_container = {
                "completed": False,
                "stdout": "",
                "stderr": "",
                "return_code": None,
                "error": None
            }
            
            # 执行命令的线程函数
            def run_command():
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=shell,
                        cwd=cwd,
                        env=merged_env,
                        text=True,
                        encoding=encoding,
                        errors=errors
                    )
                    
                    if stream_output:
                        stdout_parts = []
                        stderr_parts = []
                        
                        def read_stream(stream, parts, is_stderr=False):
                            for line in iter(stream.readline, ''):
                                if not line:
                                    break
                                parts.append(line)
                                if callback:
                                    callback(line)
                                elif stream_output:
                                    if is_stderr:
                                        sys.stderr.write(line)
                                        sys.stderr.flush()
                                    else:
                                        sys.stdout.write(line)
                                        sys.stdout.flush()
                        
                        stdout_thread = threading.Thread(
                            target=read_stream, args=(process.stdout, stdout_parts)
                        )
                        stderr_thread = threading.Thread(
                            target=read_stream, args=(process.stderr, stderr_parts, True)
                        )
                        
                        stdout_thread.daemon = True
                        stderr_thread.daemon = True
                        stdout_thread.start()
                        stderr_thread.start()
                        
                        try:
                            return_code = process.wait(timeout=timeout)
                            stdout_thread.join()
                            stderr_thread.join()
                            result_container["stdout"] = ''.join(stdout_parts)
                            result_container["stderr"] = ''.join(stderr_parts)
                            result_container["return_code"] = return_code
                            
                        except subprocess.TimeoutExpired:
                            cls._terminate_process(process, is_windows, logger)
                            result_container["error"] = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
                    else:
                        try:
                            stdout, stderr = process.communicate(timeout=timeout)
                            result_container["stdout"] = stdout
                            result_container["stderr"] = stderr
                            result_container["return_code"] = process.returncode
                            
                        except subprocess.TimeoutExpired:
                            cls._terminate_process(process, is_windows, logger)
                            result_container["error"] = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
                            
                except Exception as e:
                    result_container["error"] = e
                
                result_container["completed"] = True
                
            # 创建并启动守护线程
            command_thread = threading.Thread(target=run_command)
            command_thread.daemon = True
            command_thread.start()
            
            # 阻塞主线程直到完成或超时
            max_wait = timeout if timeout else 3600  # 如果没有设置超时，默认1小时
            wait_until = time.time() + max_wait
            
            # 等待线程完成
            while not result_container["completed"] and time.time() < wait_until:
                # 轮询，避免主线程阻塞
                time.sleep(0.1)
            
            # 设置结果
            if result_container["error"]:
                result.status = CommandStatus.FAILED if not isinstance(result_container["error"], TimeoutError) else CommandStatus.TIMEOUT
                result.error = result_container["error"]
            else:
                result.stdout = result_container["stdout"]
                result.stderr = result_container["stderr"]
                result.return_code = result_container["return_code"]
                
                if result.return_code == 0:
                    result.status = CommandStatus.COMPLETED
                else:
                    result.status = CommandStatus.FAILED
            
            result.end_time = time.time()
            return result
        
        # 默认执行方式
        try:
            result.status = CommandStatus.RUNNING
            
            if stream_output:
                # 实时处理输出
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=shell,
                    cwd=cwd,
                    env=env,
                    text=True,
                    encoding=encoding,
                    errors=errors,
                    bufsize=1  # 行缓冲
                )
                
                stdout_parts = []
                stderr_parts = []
                
                def read_stream(stream, parts, is_stderr=False):
                    for line in iter(stream.readline, ''):
                        if not line:
                            break
                        parts.append(line)
                        if callback:
                            callback(line)
                        elif stream_output:
                            if is_stderr:
                                sys.stderr.write(line)
                            else:
                                sys.stdout.write(line)
                
                # 创建线程处理stdout和stderr
                stdout_thread = threading.Thread(
                    target=read_stream, args=(process.stdout, stdout_parts)
                )
                stderr_thread = threading.Thread(
                    target=read_stream, args=(process.stderr, stderr_parts, True)
                )
                
                stdout_thread.start()
                stderr_thread.start()
                
                try:
                    exit_code = process.wait(timeout=timeout)
                    stdout_thread.join()
                    stderr_thread.join()
                    result.stdout = ''.join(stdout_parts)
                    result.stderr = ''.join(stderr_parts)
                    result.return_code = exit_code
                    
                except subprocess.TimeoutExpired:
                    cls._terminate_process(process, is_windows, logger)
                    result.status = CommandStatus.TIMEOUT
                    result.error = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
                    raise result.error
            else:
                # 一次性捕获输出
                completed_process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=shell,
                    cwd=cwd,
                    env=env,
                    text=True,
                    encoding=encoding,
                    errors=errors,
                    timeout=timeout
                )
                
                result.stdout = completed_process.stdout
                result.stderr = completed_process.stderr
                result.return_code = completed_process.returncode
                
            if result.return_code == 0:
                result.status = CommandStatus.COMPLETED
            else:
                result.status = CommandStatus.FAILED
                
        except subprocess.TimeoutExpired:
            result.status = CommandStatus.TIMEOUT
            result.error = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
            logger.error(f"命令超时: {cmd_str}")
            
        except Exception as e:
            result.status = CommandStatus.FAILED
            result.error = e
            logger.exception(f"命令执行出错: {cmd_str}")
            
        finally:
            result.end_time = time.time()
            logger.debug(f"命令 '{cmd_str}' {result.status.value}，"
                         f"耗时: {result.execution_time:.2f}秒")
            
        return result
    
    @classmethod
    async def aexec(cls, 
                    command: Union[str, List[str]], 
                    timeout: Optional[float] = None,
                    shell: bool = False,
                    cwd: Optional[str] = None,
                    env: Optional[Dict[str, str]] = None,
                    encoding: str = 'utf-8',
                    errors: str = 'replace',
                    stream_output: bool = False,
                    callback: Optional[Callable[[str], Awaitable[None]]] = None,
                    logger: Optional[logging.Logger] = None,
                    new_process: bool = False,
                    use_daemon_task: bool = False,
                    detect_terminal_app: bool = True) -> CommandResult:
        """
        异步执行命令
        
        Args:
            command: 要执行的命令，可以是字符串或参数列表
            timeout: 超时时间（秒），None 表示不设置超时
            shell: 是否在 shell 中执行命令
            cwd: 命令执行的工作目录
            env: 环境变量字典
            encoding: 输出编码
            errors: 编码错误处理方式
            stream_output: 是否实时处理输出
            callback: 异步输出回调函数，每当有新输出时调用
            logger: 日志记录器，不提供则使用默认日志记录器
            new_process: 是否在新进程中执行命令（解决终端状态异常问题）
            use_daemon_task: 是否使用守护任务（防止事件循环关闭错误）
            detect_terminal_app: 是否检测终端应用，自动选择合适的执行方式
            
        Returns:
            CommandResult: 命令执行结果对象
        """
        logger = logger or cls.get_default_logger()
        cmd = cls._parse_command(command, shell)
        cmd_str = command if isinstance(command, str) else " ".join(command)
        
        result = CommandResult(command=cmd_str, status=CommandStatus.PENDING)
        result.start_time = time.time()
        
        logger.debug(f"异步执行命令: {cmd_str}")
        
        # 检测特殊命令，为其设置最佳执行方式
        cmd_lower = cmd_str.lower()
        is_napcat = False
        if "napcat" in cmd_lower or "launcher.bat" in cmd_lower:
            logger.info("检测到 Napcat.Shell 命令，优化执行方式")
            is_napcat = True
            # 在 Windows 平台上使用新进程模式
            if platform.system() == "Windows":
                new_process = True
                # 如果在 PowerShell 中，添加特殊标志
                if cls._is_running_in_powershell():
                    logger.info("检测到 PowerShell 环境，使用特殊执行模式")
        
        # 检测是否为终端应用程序（如shell、console程序等）
        if detect_terminal_app and not new_process and not use_daemon_task:
            # 终端应用程序特征关键词
            terminal_app_keywords = [
                "shell", "term", "console", "cmd", "powershell", "bash", "zsh", 
                "napcat", "nc", "tty", "pty", "terminal", "prompt", 
                "launcher.bat", ".bat", ".exe", ".cmd"  # 添加更多终端应用特征
            ]
            
            # 检查命令中是否包含终端应用关键词
            is_terminal_app = any(keyword in cmd_lower for keyword in terminal_app_keywords)
            
            # 检测是否在 PowerShell 环境中运行
            is_powershell = cls._is_running_in_powershell()
            
            if is_terminal_app or is_powershell:
                # 检测到可能是终端应用，或在 PowerShell 中运行，输出警告
                warning_msg = (
                    f"\n警告: 检测到可能的终端应用程序 '{cmd_str}'，或在 PowerShell 环境中运行。"
                    "\n直接在当前进程执行可能导致终端状态异常或事件循环错误。"
                    "\n建议使用以下参数之一："
                    "\n  - new_process=True （在新进程中运行，独立控制台）"
                    "\n  - use_daemon_task=True （使用守护任务，避免事件循环错误）"
                    "\n例如: asyncio.run(AivkExecuter.aexec(command=cmd, new_process=True))"
                    "\n继续执行可能导致不可预期的结果...\n"
                )
                
                # 打印到终端和日志
                print(warning_msg)
                logger.warning(warning_msg)
                
                # 自动使用更安全的方式执行
                if ("napcat" in cmd_lower or "nc" in cmd_lower.split() or 
                    "launcher.bat" in cmd_lower or ".bat" in cmd_lower):
                    logger.info("检测到终端应用程序，自动切换到新进程模式执行")
                    new_process = True
        
        # 如果需要在新进程中执行（解决终端状态异常问题）
        if new_process:
            logger.debug(f"在新进程中运行命令: {cmd_str}")
            
            # 准备环境变量
            merged_env = None
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env)
            else:
                merged_env = os.environ.copy()
                
            is_windows = platform.system() == "Windows"
            
            try:
                if is_windows:
                    # Windows 平台使用 subprocess.Popen
                    # 定义创建标志
                    CREATE_NEW_CONSOLE = 0x00000010
                    DETACHED_PROCESS = 0x00000008
                    
                    # 检测是否为终端应用，如果是则使用分离模式
                    if is_napcat or "napcat" in cmd_str.lower() or ".bat" in cmd_str.lower():
                        process = subprocess.Popen(
                            cmd,
                            cwd=cwd,
                            env=merged_env,
                            shell=shell,
                            creationflags=DETACHED_PROCESS  # 使用分离模式，不依赖父进程控制台
                        )
                    else:
                        process = subprocess.Popen(
                            cmd,
                            cwd=cwd,
                            env=merged_env,
                            shell=shell,
                            creationflags=CREATE_NEW_CONSOLE
                        )
                else:
                    # Unix 平台使用 subprocess.Popen
                    process = subprocess.Popen(
                        cmd,
                        cwd=cwd,
                        env=merged_env,
                        shell=shell
                    )
                
                # 进程 ID
                pid = process.pid
                logger.info(f"在新进程中启动命令成功，PID: {pid}")
                
                # 如果是 NapCat.Shell，可能不需要等待进程完成
                if is_napcat and cls._is_running_in_powershell():
                    logger.info("NapCat.Shell 进程已启动，不等待其完成")
                    result.status = CommandStatus.COMPLETED
                    result.return_code = 0  # 假设成功启动
                    result.end_time = time.time()
                    return result
                
                # 等待进程完成
                try:
                    # 尝试获取当前事件循环，如果不存在则创建新的
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        # 没有正在运行的循环，创建一个新的
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    if timeout:
                        return_code = await asyncio.wait_for(
                            loop.run_in_executor(None, process.wait),
                            timeout=timeout
                        )
                    else:
                        return_code = await loop.run_in_executor(None, process.wait)
                    
                    result.return_code = return_code
                    if return_code == 0:
                        result.status = CommandStatus.COMPLETED
                    else:
                        result.status = CommandStatus.FAILED
                        
                except asyncio.TimeoutError:
                    # 超时处理
                    cls._terminate_process(process, is_windows, logger)
                    result.status = CommandStatus.TIMEOUT
                    result.error = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
                    raise result.error
                    
            except Exception as e:
                result.status = CommandStatus.FAILED
                result.error = e
                logger.exception(f"在新进程中执行命令出错: {cmd_str}")
            
            result.end_time = time.time()
            return result
        
        # 是否使用守护任务模式
        if use_daemon_task:
            # 创建一个没有强连接到当前事件循环的任务
            # 这样即使主事件循环关闭，任务也能继续执行
            logger.debug(f"使用守护任务模式执行命令: {cmd_str}")
            
            # 准备环境变量
            merged_env = None
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env) if env else None
            
            # 使用单独的事件循环运行命令
            try:
                executor_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(executor_loop)
                
                # 用subprocess.run替代asyncio子进程
                # 这样可以避免asyncio事件循环关闭问题
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE if not is_napcat else subprocess.DEVNULL,
                    stderr=subprocess.PIPE if not is_napcat else subprocess.DEVNULL,
                    shell=shell,
                    cwd=cwd,
                    env=merged_env,
                    text=True,
                    encoding=encoding,
                    errors=errors
                )
                
                # 等待进程完成
                try:
                    # 如果是 NapCat.Shell 且在 PowerShell 中运行，不等待其完成
                    if is_napcat and cls._is_running_in_powershell():
                        logger.info("NapCat.Shell 进程已启动，不等待其完成")
                        result.status = CommandStatus.COMPLETED
                        result.return_code = 0  # 假设成功启动
                    else:
                        if timeout:
                            # 设置超时
                            timer = threading.Timer(timeout, lambda p: p.kill(), [process])
                            timer.start()
                            stdout, stderr = process.communicate()
                            if timer.is_alive():
                                timer.cancel()
                        else:
                            stdout, stderr = process.communicate()
                        
                        result.stdout = stdout
                        result.stderr = stderr
                        result.return_code = process.returncode
                        
                        if result.return_code == 0:
                            result.status = CommandStatus.COMPLETED
                        else:
                            result.status = CommandStatus.FAILED
                        
                except Exception as e:
                    result.status = CommandStatus.FAILED
                    result.error = e
                    logger.exception(f"守护任务执行出错: {cmd_str}")
                    
            except Exception as e:
                result.status = CommandStatus.FAILED
                result.error = e
                logger.exception(f"创建守护任务出错: {cmd_str}")
            finally:
                try:
                    if 'executor_loop' in locals() and executor_loop.is_running():
                        executor_loop.stop()
                    if 'executor_loop' in locals() and not executor_loop.is_closed():
                        executor_loop.close()
                except Exception as e:
                    logger.warning(f"关闭事件循环出错: {e}")
                
            result.end_time = time.time()
            return result
        
        # 默认异步执行方式
        try:
            result.status = CommandStatus.RUNNING
            
            # 准备环境变量
            merged_env = None
            if env:
                merged_env = os.environ.copy()
                merged_env.update(env)
            
            # 创建子进程
            process = await asyncio.create_subprocess_shell(
                cmd if isinstance(cmd, str) else subprocess.list2cmdline(cmd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=shell,
                cwd=cwd,
                env=merged_env,
            )
            
            # 处理异步输出
            if stream_output or callback:
                stdout_parts = []
                stderr_parts = []
                
                async def read_stream(stream, parts, is_stderr=False):
                    while True:
                        line = await stream.readline()
                        if not line:
                            break
                        line_str = line.decode(encoding, errors=errors)
                        parts.append(line_str)
                        if callback:
                            await callback(line_str)
                        elif stream_output:
                            if is_stderr:
                                sys.stderr.write(line_str)
                                sys.stderr.flush()
                            else:
                                sys.stdout.write(line_str)
                                sys.stdout.flush()
                
                # 创建异步任务获取输出
                stdout_task = asyncio.create_task(read_stream(process.stdout, stdout_parts))
                stderr_task = asyncio.create_task(read_stream(process.stderr, stderr_parts, True))
                
                # 等待进程完成或超时
                try:
                    if timeout:
                        await asyncio.wait_for(process.wait(), timeout=timeout)
                    else:
                        await process.wait()
                    
                    # 等待输出处理完成
                    await stdout_task
                    await stderr_task
                    
                    result.stdout = ''.join(stdout_parts)
                    result.stderr = ''.join(stderr_parts)
                    
                except asyncio.TimeoutError:
                    # 超时处理
                    await cls._terminate_process_async(process, logger)
                    result.status = CommandStatus.TIMEOUT
                    result.error = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
                    raise result.error
            else:
                # 一次性获取输出
                try:
                    if timeout:
                        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                    else:
                        stdout, stderr = await process.communicate()
                        
                    result.stdout = stdout.decode(encoding, errors=errors)
                    result.stderr = stderr.decode(encoding, errors=errors)
                    
                except asyncio.TimeoutError:
                    await cls._terminate_process_async(process, logger)
                    result.status = CommandStatus.TIMEOUT
                    result.error = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
                    raise result.error
            
            result.return_code = process.returncode
            
            if result.return_code == 0:
                result.status = CommandStatus.COMPLETED
            else:
                result.status = CommandStatus.FAILED
                
        except asyncio.TimeoutError:
            result.status = CommandStatus.TIMEOUT
            result.error = TimeoutError(f"命令执行超时（{timeout}秒）: {cmd_str}")
            logger.error(f"异步命令超时: {cmd_str}")
            
        except Exception as e:
            result.status = CommandStatus.FAILED
            result.error = e
            logger.exception(f"异步命令执行出错: {cmd_str}")
                
        finally:
            result.end_time = time.time()
            logger.debug(f"异步命令 '{cmd_str}' {result.status.value}，"
                         f"耗时: {result.execution_time:.2f}秒")
            
        return result
        
    @classmethod
    async def _terminate_process_async(cls, process: asyncio.subprocess.Process, logger: logging.Logger) -> None:
        """
        异步终止进程
        
        Args:
            process: 要终止的异步进程对象
            logger: 日志记录器
        """
        if process.returncode is None:  # 检查进程是否仍在运行
            try:
                process.terminate()  # 发送 SIGTERM
                try:
                    # 等待进程终止
                    await asyncio.wait_for(process.wait(), timeout=3)
                except asyncio.TimeoutError:
                    # 如果进程没有及时终止，发送 SIGKILL
                    process.kill()
                    await asyncio.wait_for(process.wait(), timeout=3)
            except Exception as e:
                logger.error(f"异步终止进程出错: {e}")
    
    @classmethod
    def run(cls, 
            command: Union[str, List[str]], 
            timeout: Optional[float] = None,
            shell: bool = False,
            cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None,
            encoding: str = 'utf-8',
            errors: str = 'replace',
            stream_output: bool = False,
            logger: Optional[logging.Logger] = None) -> CommandResult:
        """
        类方法：快速同步执行命令
        
        Args:
            command: 要执行的命令，可以是字符串或参数列表
            timeout: 超时时间（秒），None 表示不设置超时
            shell: 是否在 shell 中执行命令
            cwd: 命令执行的工作目录
            env: 环境变量字典
            encoding: 输出编码
            errors: 编码错误处理方式
            stream_output: 是否流式处理输出（实时打印）
            logger: 日志记录器，如不提供则使用默认
            
        Returns:
            CommandResult: 命令执行结果对象
        """
        return cls.exec(
            command, timeout, shell, cwd, env, encoding, errors, stream_output, logger=logger
        )
    
    @classmethod
    def _terminate_process(cls, process: subprocess.Popen, is_windows: bool, logger: logging.Logger) -> None:
        """
        终止进程，尝试优雅关闭
        
        Args:
            process: 要终止的进程对象
            is_windows: 是否为 Windows 系统
            logger: 日志记录器
        """
        if process.poll() is None:  # 检查进程是否仍在运行
            try:
                if is_windows:
                    # Windows 下使用 taskkill 强制终止进程树
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5
                    )
                else:
                    # 在 Unix 系统中先发送 SIGTERM，然后是 SIGKILL
                    process.terminate()  # SIGTERM
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()  # SIGKILL
                        process.wait(timeout=3)
            except Exception as e:
                logger.error(f"终止进程出错: {e}")
    
    @classmethod
    def _is_running_in_powershell(cls) -> bool:
        """
        检测当前是否在 PowerShell 环境中运行
        
        Returns:
            bool: True 表示在 PowerShell 中运行，False 表示其他环境
        """
        import os
        # 检查父进程名称
        parent_process_name = os.environ.get('PSModulePath', '')
        # 检查其他 PowerShell 特有环境变量
        ps_version = os.environ.get('PSVersionTable.PSVersion', '')
        ps_executable = os.environ.get('PSExecutable', '')
        
        # 检查进程环境
        is_ps = bool(parent_process_name) or bool(ps_version) or bool(ps_executable)
        
        # 检查终端程序名称
        term_program = os.environ.get('TERM_PROGRAM', '').lower()
        if 'powershell' in term_program:
            is_ps = True
            
        # 检查系统Shell环境变量
        shell = os.environ.get('SHELL', '').lower()
        if 'powershell' in shell:
            is_ps = True
            
        return is_ps
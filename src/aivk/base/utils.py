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
             logger: Optional[logging.Logger] = None) -> CommandResult:
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
                    logger: Optional[logging.Logger] = None) -> CommandResult:
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
            
        Returns:
            CommandResult: 命令执行结果对象
        """
        logger = logger or cls.get_default_logger()
        cmd = cls._parse_command(command, shell)
        cmd_str = command if isinstance(command, str) else " ".join(command)
        
        result = CommandResult(command=cmd_str, status=CommandStatus.PENDING)
        result.start_time = time.time()
        
        logger.debug(f"异步执行命令: {cmd_str}")
        
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
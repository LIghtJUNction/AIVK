"""
工具类模块，包含 AIVK 使用的通用工具函数和类
"""

from logging import Logger


import shlex
import subprocess
import asyncio
import logging
import os
from pathlib import Path

logger: Logger = logging.getLogger(__name__)
class AivkExecuter:
    """
    Aivk 命令执行器
    
    提供同步和异步执行系统命令的功能，支持超时设置、错误处理和命令输出捕获。
    """    
    
    @classmethod
    async def _exec(cls, cmd: str | list[str], shell: bool = False, 
                  cwd: str | Path | None = None, 
                  timeout: float | None = None, 
                  env: dict[str, str] | None = None,
                  capture_output: bool = True) -> tuple[int, str, str]:
        """
        内部异步命令执行方法
        
        Args:
            cmd: 要执行的命令，可以是字符串或字符串列表
            shell: 是否使用shell模式执行
            cwd: 执行命令的工作目录
            timeout: 超时时间（秒）
            env: 环境变量
            capture_output: 是否捕获输出
            
        Returns:
            返回元组 (返回码, 标准输出, 标准错误)
        """
        # 处理命令参数
        if isinstance(cmd, str) and not shell:
            cmd_list = shlex.split(cmd)
        else:
            cmd_list = cmd if isinstance(cmd, list) else [cmd]
        
        # 当 shell=True 时，确保 cmd 是字符串
        cmd_str = cmd if isinstance(cmd, str) else " ".join([str(c) for c in cmd_list])
        
        # 合并环境变量
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
            
        logger.debug(f"执行命令: {cmd}")
        try:
            if shell:
                process = await asyncio.create_subprocess_shell(
                    cmd_str,
                    stdout=asyncio.subprocess.PIPE if capture_output else None,
                    stderr=asyncio.subprocess.PIPE if capture_output else None,
                    cwd=cwd,
                    env=merged_env,
                    shell=shell
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *cmd_list,
                    stdout=asyncio.subprocess.PIPE if capture_output else None,
                    stderr=asyncio.subprocess.PIPE if capture_output else None,
                    cwd=cwd,
                    env=merged_env
                )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except TimeoutError:
                try:
                    process.kill()
                except Exception as e:
                    logger.error(f"终止进程失败: {e}")
                raise TimeoutError(f"命令执行超时 (>{timeout}秒): {cmd}")
                
            # 确保返回码是 int 类型
            return_code = process.returncode if process.returncode is not None else -1
            stdout_str = stdout.decode('utf-8', errors='replace').strip() if stdout and capture_output else ""
            stderr_str = stderr.decode('utf-8', errors='replace').strip() if stderr and capture_output else ""
            
            if return_code != 0:
                logger.warning(f"命令返回非零状态码: {return_code}, 命令: {cmd}")
                if stderr_str:
                    logger.warning(f"错误输出: {stderr_str}")
                    
            return return_code, stdout_str, stderr_str
            
        except Exception as e:
            logger.error(f"执行命令时出错: {e}")
            return -1, "", str(e)

    @classmethod
    async def aexec(cls, cmd: str | list[str], shell: bool = False, 
                   cwd: str | Path | None = None, 
                   timeout: float | None = None, 
                   env: dict[str, str] | None = None,
                   check: bool = False,
                   capture_output: bool = True) -> tuple[int, str, str]:
        """
        异步执行命令
        
        Args:
            cmd: 要执行的命令，可以是字符串或字符串列表
            shell: 是否使用shell模式执行
            cwd: 执行命令的工作目录
            timeout: 超时时间（秒）
            env: 环境变量
            check: 如果为True且返回码非零，则抛出异常
            capture_output: 是否捕获输出
            
        Returns:
            返回元组 (返回码, 标准输出, 标准错误)
            
        Raises:
            subprocess.CalledProcessError: 当check=True且返回码非零时
            TimeoutError: 当命令执行超时时
        """
        return_code, stdout, stderr = await cls._exec(
            cmd, shell, cwd, timeout, env, capture_output
        )
        
        if check and return_code != 0:
            raise subprocess.CalledProcessError(
                return_code, cmd, stdout.encode() if stdout else None, stderr.encode() if stderr else None
            )
            
        return return_code, stdout, stderr
    
    @classmethod
    def exec(cls, cmd: str | list[str], shell: bool = False, 
            cwd: str | Path | None = None, 
            timeout: float | None = None, 
            env: dict[str, str] | None = None,
            check: bool = False,
            capture_output: bool = True) -> tuple[int, str, str]:
        """
        同步执行命令
        
        Args:
            cmd: 要执行的命令，可以是字符串或字符串列表
            shell: 是否使用shell模式执行
            cwd: 执行命令的工作目录
            timeout: 超时时间（秒）
            env: 环境变量
            check: 如果为True且返回码非零，则抛出异常
            capture_output: 是否捕获输出
            
        Returns:
            返回元组 (返回码, 标准输出, 标准错误)
            
        Raises:
            subprocess.CalledProcessError: 当check=True且返回码非零时
            subprocess.TimeoutExpired: 当命令执行超时时
        """
        try:
            if isinstance(cmd, str) and not shell:
                cmd_list = shlex.split(cmd)
            else:
                cmd_list = cmd if isinstance(cmd, list) else cmd
                
            # 合并环境变量
            merged_env = os.environ.copy()
            if env:
                merged_env.update(env)
                
            logger.debug(f"执行命令: {cmd}")
            result = subprocess.run(
                cmd_list if not shell else cmd,
                shell=shell,
                cwd=cwd,
                env=merged_env,
                timeout=timeout,
                check=check,
                capture_output=capture_output,
                text=True
            )
            
            return result.returncode, result.stdout or "", result.stderr or ""
            
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e.returncode, e.stdout or "", e.stderr or ""
        except subprocess.TimeoutExpired as e:
            logger.error(f"命令执行超时 (>{timeout}秒): {cmd}")
            if check:
                raise
            return -1, "", f"命令执行超时: {e}"
        except Exception as e:
            logger.error(f"执行命令时出错: {e}")
            if check:
                raise
            return -1, "", str(e)


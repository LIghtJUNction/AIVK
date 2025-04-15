"""
工具类模块，包含 AIVK 使用的通用工具函数和类
"""

import shlex
import subprocess
import asyncio
import logging
import os
import sys
import platform
import shutil
from pathlib import Path
from typing import List, Union, Dict, Tuple, Optional, Any


class AivkExecuter:
    """
    全能命令执行器
    
    提供同步和异步执行系统命令的功能，支持超时设置、错误处理和命令输出捕获。
    """    
    
    @classmethod
    def exec(cls, 
             cmd: Union[str, List[str]], 
             cwd: Optional[str] = None,
             env: Optional[Dict[str, str]] = None,
             timeout: Optional[float] = None,
             shell: bool = False,
             capture_output: bool = True,
             encoding: str = 'utf-8',
             check: bool = False,
             log_level: int = logging.INFO,
             detach: bool = False,
             window_title: Optional[str] = None,
             use_wt: bool = False,
             shell_type: str = "powershell",
             terminal_script: bool = False,
             wt_args: Optional[Dict[str, Any]] = None
             ) -> Union[Tuple[int, str, str], Optional[subprocess.Popen]]:
        """
        同步执行命令

        Args:
            cmd: 要执行的命令，可以是字符串或字符串列表
            cwd: 工作目录
            env: 环境变量
            timeout: 超时时间（秒）
            shell: 是否使用shell执行
            capture_output: 是否捕获输出
            encoding: 输出编码
            check: 命令失败时是否抛出异常
            log_level: 日志级别
            detach: 是否分离进程（不等待完成）
            window_title: 窗口标题（仅Windows有效）
            use_wt: 是否使用Windows Terminal（仅Windows有效）
            shell_type: shell类型（cmd、powershell、pwsh等）
            terminal_script: 是否作为脚本在终端中启动
            wt_args: Windows Terminal特有参数，可包含：
                     - window: 窗口ID或名称 (-w 参数)
                     - profile: 配置文件名称 (-p 参数)
                     - dir: 工作目录 (-d 参数)
                     - new_tab: 是否创建新标签页 (nt 参数)
                     - split_pane: 拆分窗格方向 (sp -H/-V 参数)
                     - command_line: 完整的wt命令行参数

        Returns:
            正常执行返回元组 (返回码, 标准输出, 标准错误)
            detach=True或terminal_script=True时返回进程对象或None（出错时）
        """
        logger = logging.getLogger(__name__)
        
        # 如果是终端脚本模式，使用内部方法处理
        if terminal_script and platform.system() == "Windows":
            return cls._start_terminal_script(
                script_path=cmd if isinstance(cmd, (str, Path)) else cmd[0] if cmd else None,
                cwd=cwd,
                shell_type=shell_type,
                use_wt=use_wt,
                window_title=window_title,
                env=env,
                extra_args=cmd[1:] if isinstance(cmd, list) and len(cmd) > 1 else None,
                wt_args=wt_args
            )
        
        if isinstance(cmd, str) and not shell:
            cmd = shlex.split(cmd)
        
        logger.log(log_level, f"执行命令: {cmd}")
        
        # 如果要求分离进程，则使用Popen直接启动
        if detach:
            try:
                kwargs = {
                    'cwd': cwd,
                    'env': env,
                    'shell': shell,
                    'close_fds': True,
                    'start_new_session': True if sys.platform != 'win32' else False
                }
                
                if sys.platform == 'win32':
                    # Windows系统特有配置
                    # 定义Windows常量
                    CREATE_NEW_CONSOLE = 0x00000010
                    STARTF_USESHOWWINDOW = 0x00000001
                    SW_NORMAL = 1
                    
                    # 设置启动参数
                    startupinfo = subprocess.STARTUPINFO()
                    
                    # Windows Terminal支持
                    if use_wt and shutil.which("wt"):
                        logger.info("🔓 启用Windows Terminal模式启动")
                        
                        # 检查是否提供了完整的Windows Terminal命令行
                        if wt_args and wt_args.get("command_line"):
                            full_cmd = ["wt"]
                            full_cmd.extend(shlex.split(wt_args["command_line"]))
                            cmd = full_cmd
                        elif isinstance(cmd, list):
                            orig_cmd = cmd.copy()
                            cmd = ["wt"]
                            
                            # 添加Windows Terminal特定参数
                            if wt_args:
                                # 窗口参数
                                if "window" in wt_args:
                                    cmd.extend(["-w", str(wt_args["window"])])
                                    
                                # 配置文件参数
                                if "profile" in wt_args:
                                    cmd.extend(["-p", str(wt_args["profile"])])
                                    
                                # 目录参数
                                if "dir" in wt_args:
                                    cmd.extend(["-d", str(wt_args["dir"])])
                                elif cwd:  # 如果未指定dir但有cwd
                                    cmd.extend(["-d", str(cwd)])
                                    
                                # 拆分窗格
                                if "split_pane" in wt_args:
                                    cmd.extend(["sp", "-" + str(wt_args["split_pane"]).upper()])
                                    
                                # 新标签页
                                if wt_args.get("new_tab", False):
                                    cmd.append("nt")
                            
                            # 如果指定了窗口标题但没有特定窗口参数
                            elif window_title and "window" not in (wt_args or {}):
                                cmd.extend(["--title", window_title])
                                
                            # 添加shell命令
                            if "profile" not in (wt_args or {}):  # 如果没有指定配置文件
                                # 添加shell命令和参数
                                cmd.append(shell_type)
                                if shell_type == "cmd":
                                    cmd.extend(["/k"])
                                
                                # 将原始命令添加到wt命令后
                                if shell_type == "cmd":
                                    if isinstance(orig_cmd, list):
                                        cmd.extend(orig_cmd)
                                    else:
                                        cmd.append(orig_cmd)
                                else:  # 对于PowerShell
                                    if isinstance(orig_cmd, list):
                                        ps_cmd = " ".join(f'"{arg}"' for arg in orig_cmd)
                                        cmd.append(ps_cmd)
                                    else:
                                        cmd.append(orig_cmd)
                            else:
                                # 如果指定了配置文件，直接追加命令
                                if isinstance(orig_cmd, list):
                                    cmd.extend(orig_cmd)
                                else:
                                    cmd.append(orig_cmd)
                        else:
                            # 处理字符串命令
                            wt_command = "wt"
                            
                            # 添加Windows Terminal特定参数
                            if wt_args:
                                if "window" in wt_args:
                                    wt_command += f" -w {wt_args['window']}"
                                if "profile" in wt_args:
                                    wt_command += f" -p \"{wt_args['profile']}\""
                                if "dir" in wt_args:
                                    wt_command += f" -d \"{wt_args['dir']}\""
                                elif cwd:
                                    wt_command += f" -d \"{cwd}\""
                                if "split_pane" in wt_args:
                                    wt_command += f" sp -{wt_args['split_pane'].upper()}"
                                if wt_args.get("new_tab", False):
                                    wt_command += " nt"
                            
                            if "profile" not in (wt_args or {}):
                                wt_command += f" {shell_type}"
                                if shell_type == "cmd":
                                    wt_command += f" /k {cmd}"
                                else:
                                    wt_command += f" {cmd}"
                            else:
                                wt_command += f" {cmd}"
                                
                            cmd = wt_command
                            shell = True
                            
                        # 在这种情况下不需要额外的Windows标志
                        kwargs.pop('creationflags', None)
                        shell = isinstance(cmd, str)
                    else:
                        # 使用传统控制台
                        kwargs['creationflags'] = CREATE_NEW_CONSOLE
                        startupinfo.dwFlags |= STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = SW_NORMAL
                        kwargs['startupinfo'] = startupinfo
                        
                        # 如果指定了窗口标题，需要额外处理
                        if window_title:
                            # 需要通过批处理或PowerShell设置标题
                            if shell:
                                if isinstance(cmd, list):
                                    cmd = " ".join(cmd)
                                cmd = f'start "{window_title}" /D "{cwd or os.getcwd()}" {cmd}'
                            else:
                                # 使用cmd.exe启动并设置标题
                                cmd_str = cmd if isinstance(cmd, str) else " ".join(f'"{arg}"' for arg in cmd)
                                cmd = ['cmd.exe', '/c', f'start "{window_title}" {cmd_str}']
                                shell = True
                                # 重新配置启动参数
                                kwargs.pop('creationflags', None)
                                kwargs.pop('startupinfo', None)
                else:
                    # Unix系统（Linux/macOS）
                    if sys.platform == 'darwin':  # macOS
                        # 使用open -a Terminal命令打开新终端
                        if isinstance(cmd, list):
                            cmd_str = " ".join(f"'{arg}'" for arg in cmd)
                        else:
                            cmd_str = cmd
                        cmd = ['open', '-a', 'Terminal', cmd_str]
                    else:  # Linux
                        # 尝试使用常见的终端模拟器
                        terminal_emulators = ['gnome-terminal', 'xterm', 'konsole', 'terminator']
                        terminal = None
                        
                        # 查找可用终端模拟器
                        for emulator in terminal_emulators:
                            try:
                                if subprocess.run(['which', emulator], 
                                                capture_output=True).returncode == 0:
                                    terminal = emulator
                                    break
                            except:
                                continue
                        
                        if terminal:
                            orig_cmd = cmd
                            if terminal == 'gnome-terminal':
                                if isinstance(orig_cmd, list):
                                    cmd_str = " ".join(f"'{arg}'" for arg in orig_cmd)
                                else:
                                    cmd_str = orig_cmd
                                cmd = [terminal, '--', 'bash', '-c', cmd_str]
                            else:
                                if isinstance(orig_cmd, list):
                                    cmd_str = " ".join(f"'{arg}'" for arg in orig_cmd)
                                else:
                                    cmd_str = orig_cmd
                                cmd = [terminal, '-e', f"bash -c '{cmd_str}'"]
                
                # 启动进程
                process = subprocess.Popen(cmd, **kwargs)
                return process
                
            except Exception as e:
                logger.error(f"启动程序异常: {e}")
                return None
        
        # 正常执行命令
        try:
            if capture_output:
                result = subprocess.run(
                    cmd, 
                    cwd=cwd,
                    env=env,
                    timeout=timeout,
                    shell=shell,
                    check=check,
                    text=True,
                    encoding=encoding,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(
                    cmd, 
                    cwd=cwd,
                    env=env,
                    timeout=timeout,
                    shell=shell,
                    check=check
                )
                return result.returncode, "", ""
        except subprocess.TimeoutExpired as e:
            logger.error(f"命令执行超时: {e}")
            return -1, "", f"命令执行超时: {e}"
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {e}")
            if check:
                raise
            return e.returncode, e.stdout or "", e.stderr or ""
        except Exception as e:
            logger.error(f"命令执行异常: {e}")
            if check:
                raise
            return -1, "", str(e)
    
    @classmethod
    async def aexec(cls, 
                   cmd: Union[str, List[str]], 
                   cwd: Optional[str] = None,
                   env: Optional[Dict[str, str]] = None,
                   timeout: Optional[float] = None,
                   shell: bool = False,
                   encoding: str = 'utf-8',
                   log_level: int = logging.INFO,
                   detach: bool = False,
                   window_title: Optional[str] = None,
                   errors: str = 'replace',
                   detect_encoding: bool = True,
                   use_wt: bool = False,
                   shell_type: str = "powershell",
                   terminal_script: bool = False,
                   wt_args: Optional[Dict[str, Any]] = None
                   ) -> Union[Tuple[int, str, str], Optional[subprocess.Popen]]:
        """
        异步执行命令

        Args:
            cmd: 要执行的命令，可以是字符串或字符串列表
            cwd: 工作目录
            env: 环境变量
            timeout: 超时时间（秒）
            shell: 是否使用shell执行
            encoding: 输出编码
            log_level: 日志级别
            detach: 是否分离进程（不等待完成）
            window_title: 窗口标题（仅Windows有效）
            errors: 编码错误处理方式：'strict'、'ignore'、'replace'
            detect_encoding: 是否自动检测编码（失败时尝试系统编码）
            use_wt: 是否使用Windows Terminal（仅Windows有效）
            shell_type: shell类型（cmd、powershell、pwsh等）
            terminal_script: 是否作为脚本在终端中启动
            wt_args: Windows Terminal特有参数，可包含：
                     - window: 窗口ID或名称 (-w 参数)
                     - profile: 配置文件名称 (-p 参数)
                     - dir: 工作目录 (-d 参数)
                     - new_tab: 是否创建新标签页 (nt 参数)
                     - split_pane: 拆分窗格方向 (-H/-V 参数)
                     - command_line: 完整的wt命令行参数

        Returns:
            正常执行返回元组 (返回码, 标准输出, 标准错误)
            detach=True或terminal_script=True时返回进程对象或None（出错时）
        """
        logger = logging.getLogger(__name__)
        
        # 如果要求分离进程或作为终端脚本，则直接使用同步方法启动
        if detach or terminal_script:
            return cls.exec(
                cmd=cmd,
                cwd=cwd,
                env=env,
                shell=shell,
                log_level=log_level,
                detach=True,
                window_title=window_title,
                use_wt=use_wt,
                shell_type=shell_type,
                terminal_script=terminal_script,
                wt_args=wt_args
            )
        
        # 正常异步执行
        if isinstance(cmd, str) and not shell:
            cmd = shlex.split(cmd)
        
        logger.log(log_level, f"异步执行命令: {cmd}")
        
        try:
            process = await asyncio.create_subprocess_shell(
                cmd if shell and isinstance(cmd, str) else " ".join(cmd) if shell else cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
                shell=shell
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                # 解码输出，添加错误处理
                stdout_str, stderr_str = "", ""
                
                # 尝试使用指定编码解码
                if stdout:
                    try:
                        stdout_str = stdout.decode(encoding, errors=errors)
                    except UnicodeDecodeError as e:
                        if detect_encoding:
                            # 在Windows上尝试使用系统默认编码
                            if sys.platform == 'win32':
                                try:
                                    # 尝试使用系统ANSI代码页
                                    import locale
                                    system_encoding = locale.getpreferredencoding(False)
                                    logger.info(f"尝试使用系统编码: {system_encoding}")
                                    stdout_str = stdout.decode(system_encoding, errors=errors)
                                except Exception as sub_e:
                                    # 最后尝试几种常见编码
                                    for enc in ['gbk', 'cp936', 'gb18030', 'latin1']:
                                        try:
                                            stdout_str = stdout.decode(enc, errors=errors)
                                            logger.info(f"成功使用编码 {enc} 解码输出")
                                            break
                                        except:
                                            pass
                                    else:
                                        # 所有尝试都失败，使用二进制表示
                                        logger.warning(f"无法解码输出: {e}")
                                        stdout_str = f"[二进制数据，无法解码: {str(e)}]"
                        else:
                            logger.warning(f"使用 {encoding} 无法解码输出: {e}")
                            stdout_str = f"[二进制数据，无法解码: {str(e)}]"
                
                # 解码stderr
                if stderr:
                    try:
                        stderr_str = stderr.decode(encoding, errors=errors)
                    except UnicodeDecodeError as e:
                        if detect_encoding:
                            # 在Windows上尝试使用系统默认编码
                            if sys.platform == 'win32':
                                try:
                                    import locale
                                    system_encoding = locale.getpreferredencoding(False)
                                    stderr_str = stderr.decode(system_encoding, errors=errors)
                                except Exception:
                                    # 最后尝试几种常见编码
                                    for enc in ['gbk', 'cp936', 'gb18030', 'latin1']:
                                        try:
                                            stderr_str = stderr.decode(enc, errors=errors)
                                            break
                                        except:
                                            pass
                                    else:
                                        # 所有尝试都失败，使用二进制表示
                                        stderr_str = f"[二进制数据，无法解码: {str(e)}]"
                        else:
                            stderr_str = f"[二进制数据，无法解码: {str(e)}]"
                
                return process.returncode or 0, stdout_str, stderr_str
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except:
                    pass
                logger.error(f"异步命令执行超时")
                return -1, "", "命令执行超时"
        except Exception as e:
            logger.error(f"异步命令执行异常: {e}")
            return -1, "", str(e)
            
    @classmethod
    def _start_terminal_script(cls,
                              script_path: Union[str, Path], 
                              cwd: Optional[Union[str, Path]] = None, 
                              shell_type: str = "cmd", 
                              use_wt: bool = True,
                              window_title: Optional[str] = None,
                              env: Optional[Dict[str, str]] = None,
                              extra_args: Optional[List[str]] = None,
                              wt_args: Optional[Dict[str, Any]] = None) -> Optional[subprocess.Popen]:
        """
        内部方法：在终端中启动脚本，支持Windows Terminal或传统控制台
        """
        logger = logging.getLogger(__name__)
        
        # 确保路径对象正确
        script_path = Path(script_path)
        if cwd is None:
            # 如果未指定工作目录，使用脚本所在目录
            cwd = script_path.parent
        else:
            cwd = Path(cwd)
        
        command = []
        
        # 根据平台选择启动方式
        if platform.system() == "Windows":
            if use_wt:
                logger.info("🔓 启用Windows Terminal模式启动(用户友好界面)")
                if shutil.which("wt"):
                    logger.info("✅ Windows Terminal 已安装")
                    command.append("wt")
                    
                    # 处理Windows Terminal特定参数
                    if wt_args:
                        # 如果提供了完整命令行，直接使用
                        if "command_line" in wt_args:
                            command = ["wt"]
                            command.extend(shlex.split(wt_args["command_line"]))
                            # 添加脚本路径（如果需要）
                            if not any(arg.endswith(str(script_path)) for arg in command):
                                command.append(str(script_path))
                                if extra_args:
                                    command.extend(extra_args)
                            return subprocess.Popen(
                                command,
                                cwd=str(cwd),
                                env=env,
                                shell=False,
                                start_new_session=True,
                                close_fds=True
                            )
                        
                        # 窗口参数
                        if "window" in wt_args:
                            command.extend(["-w", str(wt_args["window"])])
                        elif window_title:
                            command.extend(["--title", window_title])
                            
                        # 配置文件参数
                        if "profile" in wt_args:
                            command.extend(["-p", str(wt_args["profile"])])
                            
                        # 目录参数
                        if "dir" in wt_args:
                            command.extend(["-d", str(wt_args["dir"])])
                        else:
                            command.extend(["-d", str(cwd)])
                            
                        # 新标签页
                        if wt_args.get("new_tab", False):
                            command.append("nt")
                            
                        # 拆分窗格
                        if "split_pane" in wt_args:
                            command.extend(["sp", "-" + str(wt_args["split_pane"]).upper()])
                    else:
                        # 使用默认配置
                        # 添加标题（如果提供了）
                        if window_title:
                            command.extend(["--title", window_title])
                            
                        # 添加工作目录
                        command.extend(["-d", str(cwd)])
                    
                    # 如果未指定配置文件，添加shell_type
                    if "profile" not in (wt_args or {}):
                        # 添加shell命令
                        command.append(shell_type)
                        
                        # 添加shell特定参数和命令
                        if shell_type == "cmd":
                            logger.info(" shell : cmd ")
                            command.extend(["/k", str(script_path)])
                        else:  # powershell 或 pwsh
                            logger.info(f" shell : {shell_type} ")
                            # 直接添加命令，不使用-Command参数
                            command.append(f"cd '{cwd}'; & '{script_path}'")
                    else:
                        # 如果指定了配置文件，直接添加脚本路径
                        if "dir" not in (wt_args or {}):
                            command.extend(["-d", str(cwd)])
                        command.append(str(script_path))
                else:
                    logger.warning("⚠️ Windows Terminal 未安装，使用cmd模式启动")
                    use_wt = False
            
            if not use_wt:
                logger.info("🔒 禁用Windows Terminal模式启动(远古界面)")
                if shell_type == "cmd":
                    command = ["start", "cmd", "/k", f"cd /d {cwd}", "&&", str(script_path)]
                else:  # powershell 或 pwsh
                    logger.info(f" shell : {shell_type} ")
                    # 不使用-Command参数
                    command = ["start", shell_type, f"cd '{cwd}'; & '{script_path}'"]
        else:
            # 非Windows系统
            logger.info(f"在 {platform.system()} 上启动终端")
            
            if platform.system() == "Darwin":  # macOS
                # 在macOS上使用Terminal.app
                term_script = f"cd '{cwd}' && '{script_path}'"
                command = ["open", "-a", "Terminal", term_script]
            else:
                # Linux，尝试常见终端模拟器
                terminal_emulators = ["gnome-terminal", "xterm", "konsole", "terminator"]
                term_cmd = None
                
                for emulator in terminal_emulators:
                    if shutil.which(emulator):
                        term_cmd = emulator
                        break
                
                if term_cmd:
                    if term_cmd == "gnome-terminal":
                        command = [term_cmd, "--", "bash", "-c", f"cd '{cwd}' && '{script_path}'; exec bash"]
                    else:
                        command = [term_cmd, "-e", f"bash -c 'cd \"{cwd}\" && \"{script_path}\"; exec bash'"]
                else:
                    logger.warning("⚠️ 找不到支持的终端模拟器，直接执行脚本")
                    command = [str(script_path)]
        
        # 添加额外参数
        if extra_args and not (wt_args and "command_line" in wt_args):
            if isinstance(extra_args, list):
                command.extend(extra_args)
        
        logger.info(f"执行命令: {command}")
        
        try:
            # 创建进程
            process = subprocess.Popen(
                command,
                cwd=str(cwd),
                env=env,
                shell=False,
                start_new_session=True,
                close_fds=True
            )
            return process
        except Exception as e:
            logger.error(f"启动终端失败: {e}")
            return None
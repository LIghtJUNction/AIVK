# -*- coding: utf-8 -*-
"""
AIVK 虚拟环境上下文管理器
"""

import os
import sys
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from .fs import AivkFS
from logging import getLogger
import atexit

logger = getLogger("aivk.base.context")

# Aivk 虚拟环境上下文
class AivkContext:
    """
    AIVK 虚拟环境上下文
    """    
    def __init__(self):
        """初始化上下文"""
        self.current_fs = None
        self.active_venvs: dict[str, dict[str, Any]] = {}  # 跟踪激活的虚拟环境
        self._atexit_registered = False
        self._unloaded = False
        self._register_atexit()

    def _register_atexit(self):
        if not self._atexit_registered:
            def _atexit_hook():
                try:
                    self.unload_aivk_modules(allow_atexit=True)
                except Exception as e:
                    logger.debug(f"atexit 卸载 AIVK 模块时异常: {e}")
            atexit.register(_atexit_hook)
            self._atexit_registered = True
            logger.debug("已注册 atexit 钩子: 自动卸载 AIVK 扩展模块")

    def _create_venv(self, venv_path: Path, python_version: str | None = None) -> bool:
        """创建虚拟环境（使用 uv）"""
        if venv_path.exists():
            logger.info(f"虚拟环境已存在: {venv_path}")
            return True
            
        try:
            # 优先使用 uv 创建虚拟环境
            try:
                cmd = ["uv", "venv", str(venv_path)]
                if python_version:
                    cmd.extend(["--python", python_version])
                
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                logger.info(f"虚拟环境创建成功 (uv): {venv_path}")
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 如果 uv 不可用，回退到传统方法
                logger.warning("uv 不可用，回退到标准 venv")
                python_exe = python_version or sys.executable
                subprocess.run([
                    python_exe, "-m", "venv", str(venv_path)
                ], check=True, capture_output=True, text=True)
                logger.info(f"虚拟环境创建成功 (venv): {venv_path}")
                return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"创建虚拟环境失败: {e}")
            return False
    
    def _activate_venv(self, venv_path: Path, env_id: str) -> dict[str, str | list[str]]:
        """激活虚拟环境，返回原始环境状态"""
        # 保存原始环境状态
        original_state = {
            'PATH': os.environ.get('PATH', ''),
            'PYTHONPATH': os.environ.get('PYTHONPATH', ''),
            'VIRTUAL_ENV': os.environ.get('VIRTUAL_ENV', ''),
            'sys_path': sys.path.copy()
        }        # 设置虚拟环境路径
        if os.name == 'nt':  # Windows
            scripts_path = venv_path / "Scripts"
            python_exe = scripts_path / "python.exe"
            pip_exe = scripts_path / "pip.exe"
            site_packages = venv_path / "Lib" / "site-packages"
        else:  # macOS/Linux
            scripts_path = venv_path / "bin"
            python_exe = scripts_path / "python"
            pip_exe = scripts_path / "pip"
            site_packages = venv_path / "lib" / "python3.*/site-packages"
        
        # 更新环境变量
        os.environ['PATH'] = str(scripts_path) + os.pathsep + os.environ['PATH']
        os.environ['VIRTUAL_ENV'] = str(venv_path)
        
        # 更新 sys.path (Windows 和 Linux 的 site-packages 路径不同)
        if os.name == 'nt':
            if site_packages.exists() and str(site_packages) not in sys.path:
                sys.path.insert(0, str(site_packages))
        else:
            # Linux/macOS 需要找到实际的 python 版本目录
            lib_path = venv_path / "lib"
            if lib_path.exists():
                for python_dir in lib_path.glob("python*"):
                    if python_dir.is_dir():
                        site_pkg_path = python_dir / "site-packages"
                        if site_pkg_path.exists() and str(site_pkg_path) not in sys.path:
                            sys.path.insert(0, str(site_pkg_path))
                            break        

        self.active_venvs[env_id] = {
            'path': venv_path,
            'python': python_exe,
            'pip': pip_exe,
            'original_state': original_state
        }
        
        logger.info(f"虚拟环境已激活: {venv_path}")
        return original_state
    
    def _ensure_uv_in_venv(self, venv_path: Path):
        """确保虚拟环境中有 uv"""
        if os.name == 'nt':
            uv_exe = venv_path / "Scripts" / "uv.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            uv_exe = venv_path / "bin" / "uv"
            pip_exe = venv_path / "bin" / "pip"
        
        # 如果虚拟环境中没有 uv，但系统有 uv，则安装它
        if not uv_exe.exists():
            try:
                # 检查系统是否有 uv
                subprocess.run(["uv", "--version"], capture_output=True, check=True)
                
                # 在虚拟环境中安装 uv
                subprocess.run([
                    str(pip_exe), "install", "uv"
                ], check=True, capture_output=True, text=True)
                logger.info(f"已在虚拟环境中安装 uv: {venv_path}")
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.debug("系统未安装 uv，跳过在虚拟环境中安装")
    
    def _deactivate_venv(self, env_id: str):
        """停用虚拟环境"""
        if env_id not in self.active_venvs:
            return
            
        venv_info = self.active_venvs[env_id]
        original_state = venv_info['original_state']
        
        # 恢复环境变量
        os.environ['PATH'] = original_state['PATH']
        if original_state['PYTHONPATH']:
            os.environ['PYTHONPATH'] = original_state['PYTHONPATH']
        else:
            os.environ.pop('PYTHONPATH', None)
            
        if original_state['VIRTUAL_ENV']:
            os.environ['VIRTUAL_ENV'] = original_state['VIRTUAL_ENV']
        else:
            os.environ.pop('VIRTUAL_ENV', None)
        
        # 恢复 sys.path
        sys.path[:] = original_state['sys_path']
        
        del self.active_venvs[env_id]
        logger.info(f"虚拟环境已停用: {venv_info['path']}")    
    
    def install_packages(self, packages: list[str], env_id: str | None = None):
        """在当前或指定环境中安装包（使用系统的 uv）"""        
        if env_id and env_id in self.active_venvs:
            venv_info = self.active_venvs[env_id]
        else:
            # 如果没有提供环境ID，则使用默认的环境id: aivk
            default_env_id = env_id or "aivk"
            
            if default_env_id in self.active_venvs:
                venv_info = self.active_venvs[default_env_id]
            else:
                # 没有则新建默认环境
                logger.info(f"未找到环境 {default_env_id}，正在创建新的虚拟环境...")
                
                # 获取文件系统实例
                from .fs import AivkFS
                fs = AivkFS.getFS(default_env_id)
                fs.home.mkdir(parents=True, exist_ok=True)
                
                # 创建并激活虚拟环境
                venv_name = f"{default_env_id}_venv"
                venv_path = fs.home / venv_name
                
                if self._create_venv(venv_path):
                    self._activate_venv(venv_path, default_env_id)
                    venv_info = self.active_venvs[default_env_id]
                    logger.info(f"成功创建并激活环境: {default_env_id}")
                else:
                    logger.error(f"创建环境 {default_env_id} 失败")
                    return False
        
        venv_path = venv_info['path']
        
        for package in packages:
            try:
                # 检查系统是否有 uv
                try:
                    subprocess.run(["uv", "--version"], capture_output=True, check=True)
                    # 使用系统的 uv pip install
                    cmd = ["uv", "pip", "install", "--python", str(venv_path), package]
                    logger.info(f"使用系统 uv 安装包: {package}")
                    logger.info(f"📦 正在使用 uv 安装 {package}...")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # 如果系统没有 uv，使用虚拟环境的 pip
                    pip_exe = venv_info['pip']
                    cmd = [str(pip_exe), "install", package]
                    logger.info(f"使用 pip 安装包: {package}")
                logger.info(f"📦 正在使用 pip 安装 {package}...")
                  # 实时输出安装过程
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # 实时读取并输出
                if process.stdout:  # 确保 stdout 不为 None
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            logger.info(f"   {output.strip()}")
                
                return_code = process.poll()
                if return_code == 0:
                    logger.info(f"成功安装包: {package}")
                    logger.info(f"✅ {package} 安装成功！")
                else:
                    logger.error(f"安装包 {package} 失败，返回码: {return_code}")
                    logger.error(f"❌ {package} 安装失败！")
                    return False
                
            except Exception as e:
                logger.error(f"安装包 {package} 失败: {e}")
                logger.error(f"❌ {package} 安装失败: {e}")
                return False
        return True
    
    def uninstall_packages(self, packages: list[str], env_id: str | None = None):
        """在当前或指定环境中卸载包（使用系统的 uv）"""        
        if env_id and env_id in self.active_venvs:
            venv_info = self.active_venvs[env_id]
        else:
            # 如果没有提供环境ID，则使用默认的环境id: aivk
            default_env_id = env_id or "aivk"
            
            if default_env_id in self.active_venvs:
                venv_info = self.active_venvs[default_env_id]
            else:
                logger.error(f"未找到环境 {default_env_id}，无法卸载包")
                return False
        
        venv_path = venv_info['path']
        
        for package in packages:
            try:
                # 检查系统是否有 uv                
                try:
                    subprocess.run(["uv", "--version"], capture_output=True, check=True)
                    # 使用系统的 uv pip uninstall (不支持 -y 参数)
                    cmd = ["uv", "pip", "uninstall", "--python", str(venv_path), package]
                    logger.info(f"使用系统 uv 卸载包: {package}")
                    logger.info(f"🗑️ 正在使用 uv 卸载 {package}...")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # 如果系统没有 uv，使用虚拟环境的 pip
                    pip_exe = venv_info['pip']
                    cmd = [str(pip_exe), "uninstall", package, "-y"]
                    logger.info(f"使用 pip 卸载包: {package}")
                    logger.info(f"🗑️ 正在使用 pip 卸载 {package}...")
                
                # 实时输出卸载过程
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # 实时读取并输出
                if process.stdout:  # 确保 stdout 不为 None
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            logger.info(f"   {output.strip()}")
                
                return_code = process.poll()
                if return_code == 0:
                    logger.info(f"成功卸载包: {package}")
                    logger.info(f"✅ {package} 卸载成功！")
                else:
                    logger.error(f"卸载包 {package} 失败，返回码: {return_code}")
                    logger.error(f"❌ {package} 卸载失败！")
                    return False
                
            except Exception as e:
                logger.error(f"卸载包 {package} 失败: {e}")
                logger.error(f"❌ {package} 卸载失败: {e}")
                return False
        return True

    def list_packages(self, env_id: str | None = None) -> list[dict[str, str]]:
        """列出当前或指定环境中已安装的包"""        
        if env_id and env_id in self.active_venvs:
            venv_info = self.active_venvs[env_id]
        else:
            # 如果没有提供环境ID，则使用默认的环境id: aivk
            default_env_id = env_id or "aivk"
            
            if default_env_id in self.active_venvs:
                venv_info = self.active_venvs[default_env_id]
            else:
                logger.error(f"未找到环境 {default_env_id}，无法列出包")
                return []
        
        venv_path = venv_info['path']
        
        try:
            # 检查系统是否有 uv
            try:
                subprocess.run(["uv", "--version"], capture_output=True, check=True)
                # 使用系统的 uv pip list
                cmd = ["uv", "pip", "list", "--python", str(venv_path)]
                logger.info("使用系统 uv 列出包")
                logger.info("📋 正在使用 uv 列出已安装的包...")
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 如果系统没有 uv，使用虚拟环境的 pip
                pip_exe = venv_info['pip']
                cmd = [str(pip_exe), "list"]
            logger.info("📋 正在使用 pip 列出已安装的包...")            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            # 解析输出
            lines = result.stdout.strip().split('\n')
            packages: list[dict[str, str]] = []
            
            for line in lines[2:]:  # 跳过标题行
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        package_name = parts[0]
                        version = parts[1]
                        packages.append({'name': package_name, 'version': version})
                        logger.debug(f"  📦 {package_name} ({version})")  # 改为 DEBUG 级别

            logger.debug(f"列出 {len(packages)} 个包")  # 改为 DEBUG 级别
            logger.info(f"✅ 共找到 {len(packages)} 个已安装的包")
            return packages
        except subprocess.CalledProcessError as e:
            logger.error(f"列出包失败: {e}")
            logger.error(f"❌ 列出包失败: {e}")
            return []
        except Exception as e:
            logger.error(f"列出包失败: {e}")
            logger.error(f"❌ 列出包失败: {e}")
            return []
        
    def get_aivk_modules(self, packages: list[dict[str, str]], show_all_packages: bool = False) -> list[dict[str, str]]:
        """从包列表中获取 aivk_ 开头的模块列表"""
        aivk_modules: list[dict[str, str]] = []
        
        for package_info in packages:
            package_name = package_info['name']
            
            if show_all_packages:
                # -vvv 模式：显示所有包的详细信息
                logger.debug(f"检查包: {package_name} (版本: {package_info['version']})")
            else:
                # -vv 模式：只显示包名
                logger.debug(f"检查包: {package_name}")
            
            if package_name.startswith('aivk_') or package_name.startswith('aivk-'):
                # 尝试获取包的详细信息
                author, description = self._get_package_details(package_name)
                
                module_info = {
                    'name': package_name,
                    'version': package_info['version'],
                    'author': author,
                    'description': description,
                }
                aivk_modules.append(module_info)
                logger.info(f"发现 AIVK 模块: {package_name} ({package_info['version']})")
            elif show_all_packages and package_name.startswith('aivk'):
                # -vvv 模式：也显示其他 aivk 相关的包（不是扩展）
                logger.info(f"发现 AIVK 相关包: {package_name} ({package_info['version']}) - 非扩展模块")
        
        return aivk_modules

    def get_aivk_installed_modules(self, env_id: str = "aivk", show_all_packages: bool = False) -> list[dict[str, str]]:
        """获取已安装的 aivk_ 开头的模块列表"""
        try:
            logger.debug("正在获取 AIVK 模块列表...")
            with self.env(env_id, create_venv=True):
                logger.info("已进入虚拟环境，正在获取包列表...")
                # 获取虚拟环境中已安装的包                
                packages = self.list_packages(env_id)
                logger.info(f"获取到 {len(packages)} 个包，正在筛选 AIVK 模块...")
                
                return self.get_aivk_modules(packages, show_all_packages)
                
        except Exception as e:
            logger.error(f"获取 AIVK 模块列表失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []

    def _load_pth_paths(self, env_id: str = "aivk") -> None:
        """加载 .pth 文件中指定的路径到 sys.path"""
        if env_id not in self.active_venvs:
            return
            
        venv_info = self.active_venvs[env_id]
        venv_path = venv_info['path']
        
        # 找到 site-packages 目录
        if os.name == 'nt':  # Windows
            site_packages = venv_path / "Lib" / "site-packages"
        else:  # macOS/Linux
            lib_path = venv_path / "lib"
            site_packages = None
            if lib_path.exists():
                for python_dir in lib_path.glob("python*"):
                    if python_dir.is_dir():
                        site_packages = python_dir / "site-packages"
                        break
        
        if not site_packages or not site_packages.exists():
            return
            
        # 查找所有 .pth 文件
        for pth_file in site_packages.glob("*.pth"):
            try:
                logger.debug(f"处理 .pth 文件: {pth_file}")
                with open(pth_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 将路径添加到 sys.path
                            if line not in sys.path:
                                sys.path.insert(0, line)
                                logger.debug(f"添加路径到 sys.path: {line}")
            except Exception as e:
                logger.debug(f"读取 .pth 文件失败 {pth_file}: {e}")

    def load_single_module(self, module_name: str, env_id: str = "aivk", verbose_level: int = 0, in_env: bool = False) -> bool:
        """加载单个 AIVK 模块
        
        :param module_name: 模块名称（包名或导入名）
        :param env_id: 环境ID
        :param verbose_level: 详细级别 (0=默认, 1=-v, 2=-vv, 3=-vvv)
        :param in_env: 是否已在虚拟环境上下文中
        :return: 是否加载成功
        """
        import importlib
        import asyncio
        
        def _do_load():
            # 加载 .pth 文件中的路径（支持可编辑安装的包）
            self._load_pth_paths(env_id)
            import_name = module_name.replace('-', '_')
            try:
                if verbose_level >= 1:
                    logger.info(f"正在加载模块: {module_name}")
                logger.debug(f"尝试导入包: {import_name} (包名: {module_name})")
                module = importlib.import_module(import_name)
                if verbose_level >= 1:
                    logger.info(f"成功导入包: {module_name} -> {import_name}")
                else:
                    logger.info(f"✓ 加载 {module_name}")
                # 检查包是否有启动函数
                if hasattr(module, 'onLoad'):
                    if verbose_level >= 1:
                        logger.info(f"调用包的 onLoad 函数: {module_name}")
                    if asyncio.iscoroutinefunction(module.onLoad):
                        asyncio.run(module.onLoad())
                    else:
                        module.onLoad()
                elif hasattr(module, 'main'):
                    if verbose_level >= 1:
                        logger.info(f"调用包的 main 函数: {module_name}")
                    if asyncio.iscoroutinefunction(module.main):
                        asyncio.run(module.main())
                    else:
                        module.main()
                elif hasattr(module, 'start'):
                    if verbose_level >= 1:
                        logger.info(f"调用包的 start 函数: {module_name}")
                    if asyncio.iscoroutinefunction(module.start):
                        asyncio.run(module.start())
                    else:
                        module.start()
                else:
                    if verbose_level >= 2:
                        logger.info(f"包 {module_name} 已加载（无启动函数：onLoad/main/start）")
                return True
            except ImportError as e:
                logger.error(f"无法导入包 {import_name} (包名: {module_name}): {e}")
                logger.info(f"提示：包名为 '{module_name}' 的包应该在 site-packages 中有对应的 '{import_name}' 目录")
                logger.info("      或者通过 .pth 文件指向可编辑安装的源代码目录")
                logger.info("      请确保包的发布配置正确，或者包内有 __init__.py 文件")
                if verbose_level >= 2:
                    logger.debug("当前 sys.path 中的相关路径:")
                    for path in sys.path:
                        if 'aivk' in path.lower():
                            logger.debug(f"  - {path}")
                return False
            except Exception as e:
                logger.error(f"启动包 {import_name} (包名: {module_name}) 时出错: {e}")
                if verbose_level >= 2:
                    import traceback
                    logger.debug(traceback.format_exc())
                return False
        try:
            if in_env:
                return _do_load()
            else:
                with self.env(env_id, create_venv=True):
                    return _do_load()
        except Exception as e:
            logger.error(f"加载模块 {module_name} 失败: {e}")
            if verbose_level >= 2:
                import traceback
                logger.debug(traceback.format_exc())
            return False

    def unload_single_module(self, module_name: str, env_id: str = "aivk", verbose_level: int = 0, in_env: bool = False) -> bool:
        """卸载单个 AIVK 模块
        
        :param module_name: 模块名称（包名或导入名）
        :param env_id: 环境ID
        :param verbose_level: 详细级别 (0=默认, 1=-v, 2=-vv, 3=-vvv)
        :param in_env: 是否已在虚拟环境上下文中
        :return: 是否卸载成功
        """
        import asyncio
        import sys
        
        def _do_unload():
            import_name = module_name.replace('-', '_')
            try:
                if verbose_level >= 1:
                    logger.info(f"正在卸载模块: {module_name}")
                logger.debug(f"尝试卸载包: {import_name} (包名: {module_name})")
                if import_name in sys.modules:
                    module = sys.modules[import_name]
                    if hasattr(module, 'onUnload'):
                        if verbose_level >= 1:
                            logger.info(f"调用包的 onUnload 函数: {module_name}")
                        if asyncio.iscoroutinefunction(module.onUnload):
                            asyncio.run(module.onUnload())
                        else:
                            module.onUnload()
                    elif hasattr(module, 'stop'):
                        if verbose_level >= 1:
                            logger.info(f"调用包的 stop 函数: {module_name}")
                        if asyncio.iscoroutinefunction(module.stop):
                            asyncio.run(module.stop())
                        else:
                            module.stop()
                    elif hasattr(module, 'unload'):
                        if verbose_level >= 1:
                            logger.info(f"调用包的 unload 函数: {module_name}")
                        if asyncio.iscoroutinefunction(module.unload):
                            asyncio.run(module.unload())
                        else:
                            module.unload()
                    else:
                        if verbose_level >= 2:
                            logger.info(f"包 {module_name} 无卸载函数（onUnload/stop/unload）")
                    del sys.modules[import_name]
                    if verbose_level >= 1:
                        logger.info(f"成功卸载包: {module_name} -> {import_name}")
                    else:
                        print(f"✓ 卸载 {module_name}")
                    return True
                else:
                    if verbose_level >= 1:
                        logger.info(f"包 {module_name} 未加载，跳过卸载")
                    return True
            except Exception as e:
                logger.error(f"卸载包 {import_name} (包名: {module_name}) 时出错: {e}")
                if verbose_level >= 2:
                    import traceback
                    logger.debug(traceback.format_exc())
                return False
        try:
            if in_env:
                return _do_unload()
            else:
                with self.env(env_id, create_venv=True):
                    return _do_unload()
        except Exception as e:
            logger.error(f"卸载模块 {module_name} 失败: {e}")
            if verbose_level >= 2:
                import traceback
                logger.debug(traceback.format_exc())
            return False

    def load_aivk_modules(self, env_id: str = "aivk", verbose_level: int = 0) -> None:
        """依次启动 aivk_ 开头的模块
        
        :param env_id: 环境ID
        :param verbose_level: 详细级别 (0=默认, 1=-v, 2=-vv, 3=-vvv)
        """
        try:
            with self.env(env_id, create_venv=True):
                self._load_pth_paths(env_id)
                packages = self.list_packages(env_id)
                if verbose_level >= 2:
                    logger.info(f"获取到 {len(packages)} 个包，正在筛选 AIVK 模块...")
                aivk_modules = self.get_aivk_modules(packages, show_all_packages=(verbose_level >= 3))
                if verbose_level >= 1:
                    logger.info(f"找到 {len(aivk_modules)} 个 AIVK 扩展模块")
                elif aivk_modules:
                    print(f"找到 {len(aivk_modules)} 个 AIVK 扩展模块")
                for module_info in aivk_modules:
                    package_name = module_info['name']
                    success = self.load_single_module(package_name, env_id, verbose_level, in_env=True)
                    if not success and verbose_level >= 1:
                        logger.warning(f"模块 {package_name} 加载失败")
        except Exception as e:
            logger.error(f"加载 AIVK 模块失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())

    def unload_aivk_modules(self, env_id: str = "aivk", verbose_level: int = 0, allow_atexit: bool = False) -> None:
        """依次卸载 aivk_ 开头的模块
        
        :param env_id: 环境ID
        :param verbose_level: 详细级别 (0=默认, 1=-v, 2=-vv, 3=-vvv)
        :param allow_atexit: 是否允许 atexit 钩子调用（防止递归）
        """
        if self._unloaded and not allow_atexit:
            logger.debug("AIVK 模块已卸载，跳过重复卸载")
            return
        self._unloaded = True
        try:
            with self.env(env_id, create_venv=True):
                self._load_pth_paths(env_id)
                packages = self.list_packages(env_id)
                if verbose_level >= 2:
                    logger.info(f"获取到 {len(packages)} 个包，正在筛选 AIVK 模块...")
                aivk_modules = self.get_aivk_modules(packages, show_all_packages=(verbose_level >= 3))
                if verbose_level >= 1:
                    logger.info(f"找到 {len(aivk_modules)} 个 AIVK 扩展模块待卸载")
                elif aivk_modules:
                    print(f"找到 {len(aivk_modules)} 个 AIVK 扩展模块待卸载")
                for module_info in aivk_modules:
                    package_name = module_info['name']
                    success = self.unload_single_module(package_name, env_id, verbose_level, in_env=True)
                    if not success and verbose_level >= 1:
                        logger.warning(f"模块 {package_name} 卸载失败")
        except Exception as e:
            logger.error(f"卸载 AIVK 模块失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())

    def _get_package_details(self, package_name: str) -> tuple[str, str]:
        """获取包的详细信息（作者和描述）
        
        :param package_name: 包名
        :return: (作者, 描述) 的元组
        """
        try:
            # 尝试使用当前激活的虚拟环境中的 pip show
            for env_id, venv_info in self.active_venvs.items():
                try:
                    # 检查系统是否有 uv
                    try:
                        subprocess.run(["uv", "--version"], capture_output=True, check=True)
                        # 使用系统的 uv pip show
                        venv_path = venv_info['path']
                        cmd = ["uv", "pip", "show", "--python", str(venv_path), package_name]
                        logger.debug(f"使用系统 uv 获取包信息: {package_name}")
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # 如果系统没有 uv，使用虚拟环境的 pip
                        pip_exe = venv_info['pip']
                        cmd = [str(pip_exe), "show", package_name]
                        logger.debug(f"使用 pip 获取包信息: {package_name}")
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                    # 解析输出
                    author = "未知"
                    description = "无描述"
                    
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if line.startswith('Author:'):
                            author = line.split(':', 1)[1].strip() or "未知"
                        elif line.startswith('Summary:'):
                            description = line.split(':', 1)[1].strip() or "无描述"
                    
                    logger.debug(f"获取到包 {package_name} 的信息: 作者={author}, 描述={description}")
                    return author, description
                    
                except subprocess.CalledProcessError:
                    logger.debug(f"无法通过环境 {env_id} 获取包 {package_name} 的信息")
                    continue
                except Exception as e:
                    logger.debug(f"获取包 {package_name} 信息时出错: {e}")
                    continue
            
            # 如果所有虚拟环境都失败，返回默认值
            logger.debug(f"无法获取包 {package_name} 的详细信息，使用默认值")
            return "未知", "无描述"
            
        except Exception as e:
            logger.debug(f"获取包 {package_name} 详细信息失败: {e}")
            return "未知", "无描述"
    
    @contextmanager
    def env(self, id: str = "aivk", create_venv: bool = True, venv_name: str | None = None):
        """
        AIVK 虚拟环境上下文管理器
        
        :param id: AIVK ID
        :param create_venv: 是否创建并激活虚拟环境
        :param venv_name: 虚拟环境名称，默认使用 id
        :return: AIVK 文件系统实例
        """
        # 获取文件系统实例
        fs = AivkFS.getFS(id)
        
        # 确保必要的目录存在
        fs.home.mkdir(parents=True, exist_ok=True)
        fs.data.mkdir(parents=True, exist_ok=True)
        fs.cache.mkdir(parents=True, exist_ok=True)
        fs.tmp.mkdir(parents=True, exist_ok=True)
        fs.etc.mkdir(parents=True, exist_ok=True)
        
        # 保存当前文件系统
        previous_fs = self.current_fs
        self.current_fs = fs        # 虚拟环境处理
        venv_activated = False
        venv_path = None
        venv_name = venv_name or f"{id}_venv"
        venv_path = fs.home / venv_name  # 直接在 home 目录下创建虚拟环境
        
        if create_venv:
            # 创建模式：创建环境（如果不存在）并激活
            venv_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建虚拟环境
            if self._create_venv(venv_path):
                # 激活虚拟环境
                self._activate_venv(venv_path, id)
                venv_activated = True
        else:
            # 激活模式：激活已存在的环境（如果不存在则报错）
            if venv_path.exists():
                # 激活已存在的虚拟环境
                self._activate_venv(venv_path, id)
                venv_activated = True
                logger.info(f"激活已存在的虚拟环境: {venv_path}")
            else:
                logger.warning(f"虚拟环境不存在: {venv_path}，将在不激活虚拟环境的情况下继续")
        
        try:
            logger.info(f"进入 AIVK 环境: {id}")
            if venv_activated:
                logger.info(f"虚拟环境已激活: {venv_path}")
            yield fs
        finally:
            logger.info(f"退出 AIVK 环境: {id}")
            # 停用虚拟环境
            if venv_activated:
                self._deactivate_venv(id)
            self.current_fs = previous_fs

    @classmethod
    def getContext(cls):
        """
        获取 AIVK 上下文实例
        
        :return: AivkContext 实例
        """
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
            logger.info("AIVK 上下文已初始化")
        return cls._instance



__all__ = ["AivkContext"]
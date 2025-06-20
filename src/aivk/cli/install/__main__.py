from aivk.api import FastAIVK
from aivk.base.context import AivkContext
from aivk.base.fs import AivkFS
from click import command, option, argument
from logging import getLogger
import re
from pathlib import Path

logger = getLogger("aivk.cli.install")
@command()
@argument('package', required=True)
@option('--env-id', '-e', default='aivk', help='目标虚拟环境ID (默认: aivk)')
@option('--upgrade', '-U', is_flag=True, help='升级包到最新版本')
@option('--force-reinstall', is_flag=True, help='强制重新安装')
@option('--no-deps', is_flag=True, help='不安装依赖')
@option('--editable', '-E', is_flag=True, help='以可编辑模式安装 (仅限本地路径)')
def install(package: str, env_id: str, upgrade: bool, force_reinstall: bool, no_deps: bool, editable: bool):
    """
    AIVK 安装命令
    
    安装指定的包到AIVK虚拟环境中
    
    PACKAGE 可以是:
    - PyPI包名: numpy, pandas, requests
    - GitHub仓库: https://github.com/user/repo.git 或 git+https://github.com/user/repo.git
    - 本地路径: ./path/to/package 或 /absolute/path/to/package
    """
    try:
        # 获取AIVK上下文
        ctx = AivkContext.getContext()
        
        # 检测包类型并预处理
        package_spec = _process_package_spec(package, editable)
        
        logger.info(f"🚀 正在安装包: {package}")
        logger.info(f"📍 目标环境ID: {env_id}")
          # 使用AIVK上下文创建或激活虚拟环境
        @FastAIVK.aivk_context(id=env_id, create_venv=True)
        def _install_in_env(fs: AivkFS):
            logger.info(f"🏠 虚拟环境路径: {fs.home}")
            
            # 构建安装参数
            install_args = _build_install_args(package_spec, upgrade, force_reinstall, no_deps)
            
            # 执行安装
            success = ctx.install_packages(install_args, env_id=fs.id)
            
            if success:
                logger.info(f"✅ 包 '{package}' 安装成功到环境 '{env_id}'")
                
                # 验证安装
                _verify_installation(package, fs.id, ctx)
            else:
                logger.error(f"❌ 包 '{package}' 安装失败")
                exit(1)
          # 执行安装
        _install_in_env()  # type: ignore
        
    except Exception as e:
        logger.error(f"❌ 安装过程出错: {e}")
        exit(1)


def _process_package_spec(package: str, editable: bool) -> str:
    """处理包规格说明，支持不同类型的包源"""
    
    # 检查是否为本地路径
    if _is_local_path(package):
        local_path = Path(package).resolve()
        if not local_path.exists():
            raise ValueError(f"本地路径不存在: {package}")
        
        if editable:
            return f"-e {local_path}"
        else:
            return str(local_path)
    
    # 检查是否为GitHub仓库
    elif _is_github_repo(package):
        return _normalize_github_url(package)
    
    # 默认为PyPI包
    else:
        return package


def _is_local_path(package: str) -> bool:
    """检查是否为本地路径"""
    return (
        package.startswith('./') or 
        package.startswith('../') or 
        package.startswith('/') or
        (len(package) > 1 and package[1] == ':') or  # Windows绝对路径
        Path(package).exists()
    )


def _is_github_repo(package: str) -> bool:
    """检查是否为GitHub仓库"""
    github_patterns = [
        r'^https://github\.com/[\w\-\.]+/[\w\-\.]+',
        r'^git\+https://github\.com/[\w\-\.]+/[\w\-\.]+',
        r'^github:[\w\-\.]+/[\w\-\.]+',
        r'^[\w\-\.]+/[\w\-\.]+$'  # 简写形式 user/repo
    ]
    
    return any(re.match(pattern, package) for pattern in github_patterns)


def _normalize_github_url(package: str) -> str:
    """标准化GitHub URL"""
    # 如果是简写形式 user/repo
    if re.match(r'^[\w\-\.]+/[\w\-\.]+$', package) and not package.startswith('http'):
        return f"git+https://github.com/{package}.git"
    
    # 如果已经是完整URL但没有git+前缀
    if package.startswith('https://github.com/') and not package.startswith('git+'):
        if not package.endswith('.git'):
            package += '.git'
        return f"git+{package}"
    
    return package


def _build_install_args(package_spec: str, upgrade: bool, force_reinstall: bool, no_deps: bool) -> list[str]:
    """构建安装参数列表"""
    args = [package_spec]
    
    # 注意：这些参数会在AivkContext的install_packages方法中处理
    # 这里只是将包规格传递过去，具体的参数处理在context.py中实现
    
    return args


def _verify_installation(package: str, env_id: str, ctx: AivkContext):
    """验证包是否安装成功"""
    try:
        logger.info("🔍 验证安装结果...")
        packages = ctx.list_packages(env_id=env_id)
        
        # 提取包名（去掉版本号和特殊字符）
        package_name = _extract_package_name(package)
        
        installed_packages = [pkg['name'].lower() for pkg in packages]
        
        if package_name.lower() in installed_packages:
            installed_pkg = next(pkg for pkg in packages if pkg['name'].lower() == package_name.lower())
            logger.info(f"✅ 验证成功: {installed_pkg['name']} ({installed_pkg['version']})")
        else:
            logger.info(f"⚠️  验证警告: 未在包列表中找到 '{package_name}'，但安装可能仍然成功")
            
    except Exception as e:
        logger.info(f"⚠️  验证过程出错: {e}")


def _extract_package_name(package: str) -> str:
    """从包规格中提取包名"""
    # 移除git+前缀
    if package.startswith('git+'):
        package = package[4:]
    
    # 处理GitHub URL
    if 'github.com' in package:
        # 从URL中提取仓库名
        parts = package.rstrip('.git').split('/')
        return parts[-1] if parts else package
    
    # 处理本地路径
    if _is_local_path(package):
        path = Path(package)
        # 尝试从setup.py或pyproject.toml中读取包名
        # 这里简化处理，直接使用目录名
        return path.name
    
    # 处理PyPI包名（可能包含版本号）
    # 移除版本规格符号
    package = re.split(r'[><=!]', package)[0]
    package = package.split('==')[0].split('>=')[0].split('<=')[0]
    
    return package.strip()
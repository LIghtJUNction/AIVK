# -*- coding: utf-8 -*-
from aivk.api import FastAIVK
from aivk.base.context import AivkContext
from aivk.base.fs import AivkFS
from click import command, option, argument
import re
from logging import getLogger
logger = getLogger("aivk.cli.uninstall")

@command()
@argument('package', required=True)
@option('--env-id', '-e', default='aivk', help='目标虚拟环境ID (默认: aivk)')
@option('--yes', '-y', is_flag=True, help='跳过确认提示')
@option('--all', is_flag=True, help='卸载所有包')
def uninstall(package: str, env_id: str, yes: bool, all: bool):
    """
    AIVK 卸载命令
    
    从AIVK虚拟环境中卸载指定的包
    
    PACKAGE 可以是:
    - PyPI包名: numpy, pandas, requests
    - 多个包用空格分隔: "numpy pandas requests"
    - 使用 --all 标志卸载所有包
    """
    try:
        # 获取AIVK上下文
        ctx = AivkContext.getContext()
        
        logger.info(f"🗑️ 正在卸载包: {package}")
        logger.info(f"📍 目标环境ID: {env_id}")
          # 使用AIVK上下文连接到虚拟环境
        @FastAIVK.aivk_context(id=env_id, create_venv=True)
        def _uninstall_in_env(fs: AivkFS):
            logger.info(f"🏠 虚拟环境路径: {fs.home}")
            
            # 检查环境是否存在
            if not _check_env_exists(fs, env_id, ctx):
                logger.error(f"❌ 环境 '{env_id}' 不存在或未激活")
                exit(1)
            
            # 处理包列表
            packages_to_uninstall = _process_packages(package, all, fs.id, ctx)
            
            if not packages_to_uninstall:
                logger.error("❌ 没有找到要卸载的包")
                exit(1)
            
            # 确认卸载
            if not yes and not _confirm_uninstall(packages_to_uninstall, env_id):
                logger.error("❌ 用户取消卸载操作")
                exit(0)
            
            # 执行卸载
            success = ctx.uninstall_packages(packages_to_uninstall, env_id=fs.id)
            
            if success:
                logger.info(f"✅ 包卸载成功从环境 '{env_id}'")
                
                # 验证卸载
                _verify_uninstallation(packages_to_uninstall, fs.id, ctx)
            else:
                logger.error("❌ 包卸载失败")
                exit(1)
        
        # 执行卸载
        _uninstall_in_env()  # type: ignore
        
    except Exception as e:
        logger.error(f"❌ 卸载过程出错: {e}")
        exit(1)


def _check_env_exists(fs: AivkFS, env_id: str, ctx: AivkContext) -> bool:
    """检查虚拟环境是否存在"""
    try:
        # 尝试列出包来检查环境是否可用
        ctx.list_packages(env_id=env_id)
        return True
    except Exception:
        return False


def _process_packages(package: str, all_flag: bool, env_id: str, ctx: AivkContext) -> list[str]:
    """处理要卸载的包列表"""
    if all_flag:
        logger.warning("⚠️  将卸载环境中的所有包")
        # 获取所有已安装的包
        installed_packages = ctx.list_packages(env_id=env_id)
        # 过滤掉系统包（pip, setuptools等）
        system_packages = {'pip', 'setuptools', 'wheel', 'distribute'}
        return [pkg['name'] for pkg in installed_packages 
                if pkg['name'].lower() not in system_packages]
    else:
        # 处理单个或多个包
        # 支持空格分隔的多个包
        packages = [pkg.strip() for pkg in package.split() if pkg.strip()]
          # 验证包是否已安装
        installed_packages = ctx.list_packages(env_id=env_id)
        installed_names = [pkg['name'].lower() for pkg in installed_packages]
        
        valid_packages: list[str] = []
        for pkg in packages:
            pkg_name = _extract_package_name(pkg)
            if pkg_name.lower() in installed_names:
                valid_packages.append(pkg_name)
            else:
                logger.warning(f"⚠️  包 '{pkg_name}' 未安装在环境 '{env_id}' 中")
        
        return valid_packages


def _confirm_uninstall(packages: list[str], env_id: str) -> bool:
    """确认卸载操作"""
    logger.info(f"\n📋 将从环境 '{env_id}' 中卸载以下包:")
    for pkg in packages:
        logger.info(f"  - {pkg}")

    logger.info(f"\n总共 {len(packages)} 个包")

    try:
        response = input("\n❓ 确认继续卸载吗? [y/N]: ").strip().lower()
        return response in ['y', 'yes', '是']
    except KeyboardInterrupt:
        logger.error("\n❌ 用户中断操作")
        return False


def _verify_uninstallation(packages: list[str], env_id: str, ctx: AivkContext):
    """验证包是否卸载成功"""
    try:
        logger.info("🔍 验证卸载结果...")
        remaining_packages = ctx.list_packages(env_id=env_id)
        remaining_names = [pkg['name'].lower() for pkg in remaining_packages]
        
        for package in packages:
            package_name = _extract_package_name(package)
            if package_name.lower() not in remaining_names:
                logger.info(f"✅ 验证成功: {package_name} 已被卸载")
            else:
                logger.warning(f"⚠️  验证警告: {package_name} 仍然存在，卸载可能未完成")

    except Exception as e:
        logger.error(f"⚠️  验证过程出错: {e}")


def _extract_package_name(package: str) -> str:
    """从包规格中提取包名"""
    # 移除版本规格符号
    package = re.split(r'[><=!]', package)[0]
    package = package.split('==')[0].split('>=')[0].split('<=')[0]
    
    return package.strip()


if __name__ == "__main__":
    uninstall()


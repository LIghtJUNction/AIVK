# -*- coding: utf-8 -*-
import asyncio
from logging import getLogger
from aivk.api import AivkContext, AivkFS , AivkLoader , AivkMod
from click import command

logger = getLogger("aivk.run")
@command()
def run():
    """
    AIVK 运行命令
    :param style: 运行方式，支持 "cli" 或 "web"
    启动 AIVK CLI
    """
    async def run():
        try:
            logger.info("开始加载 AIVK 模块...")
            ctx = AivkContext.getContext()
            logger.debug("AivkContext 获取完成: %s", ctx)
            async with ctx.env("aivk", create_venv=True) as fs:
                logger.debug("已进入 ctx.env 上下文, fs=%s", fs)
                loader = AivkLoader.getLoader()
                logger.debug("AivkLoader 获取完成: %s", loader)
                aivk_modules = await loader.ls(fs)  # 获取所有 AIVK 模块列表
                logger.debug("模块列表: %s", aivk_modules)
                await loader.load(fs, "aivk", aivk_modules)  # 加载 AIVK 模块
                logger.debug("AIVK 模块加载完成")
                # 加载其他组件 -- 如果未禁用
                await loader.load(fs, "*", aivk_modules)  # 加载其他所有组件
                logger.debug("所有组件加载完成")
                AivkLoader.aivk_box.to_toml(AivkFS.aivk_cache / "aivk_box.toml")  # type: ignore
                logger.debug("aivk_box 已保存")
                # 开始执行
                await AivkMod.exec("aivk", "onLoad")  # 执行 AIVK 的 onLoad 钩子
                logger.debug("AIVK onLoad 执行完成")
                await AivkMod.exec("web", "onLoad")  # 执行 Web 的 onLoad 钩子
                logger.debug("Web onLoad 执行完成")

        except Exception as e:
            logger.error(f"运行 AIVK 时发生错误: {e}")
            import traceback
            logger.error(traceback.format_exc(limit=20))

    asyncio.run(run())
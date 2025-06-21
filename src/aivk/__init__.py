# -*- coding: utf-8 -*-
from logging import getLogger
from .__about__ import __LOGO__, __BYE__
from .api import FastAIVK
logger = getLogger("aivk")
#region meta

#region aivk

@FastAIVK.meta
class AIVK():
    """
    AIVK 元模块
    Hello AIVK!
    """
    id = "aivk"
    level : int = 0

@AIVK.onLoad
async def onLoad():
    logger.info("HELLO AIVK!")
    logger.info(__LOGO__)

@AIVK.onUnload
async def onUnload():
    logger.info("GOODBYE AIVK!")
    logger.info(__BYE__)


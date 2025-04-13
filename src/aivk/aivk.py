# -*- coding: utf-8 -*-
import logging
from mcp.server.fastmcp import FastMCP

from typing import Dict, Any, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 请导出到__init__.py ! 并重命名为 mcp!
# please export to __init__.py ! and rename to mcp!
aivk = FastMCP(name="AIVK")

pass



if __name__ == "__main__":
    aivk.run(transport="stdio")
# 主模块: aivk
from datetime import datetime
from .aivk_impl import Aivk
# agents
from .agents.agents_impl import Agents
# kernel
from .kernel.router.router_impl import Router
from .kernel.analyzer.analyzer_impl import Analyzer
from .kernel.tee.tee_impl import Tee
# llms
from .llms.llms_impl import Llms
# tools
from .tools.tools_impl import Tools

# agents = Agents()
# router = Router()
# analyzer = Analyzer()
# tee = Tee()
# llms = Llms()
# tools = Tools()
# 
# objs = [ agents, router, analyzer, tee, llms, tools ]
# 
# for obj in objs:
#     print(obj.meta)
# 
# print(llms.meta.Metadata.__name__)

tee = Tee()
llms = Llms(tee)



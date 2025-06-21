from click import group , option, pass_context , Context
from aivk.cli.amcp import aivk_mcp
from aivk.cli.run import run
from aivk.cli.shell import shell
from aivk.api.setlogger import set_logger_level_from_ctx, set_logger_style
from logging import getLogger
from aivk.base.aivk import AivkMod
debug = AivkMod.getMod("aivk")

logger = getLogger("aivk")
@group() 
@option("-v", "--verbose", count=True, default=2, help="详细程度，可以多次使用 (-v, -vv, -vvv)")
@pass_context
def cli(ctx: Context, verbose: int):
    """
    AIVK CLI
    """
    verbose = min(verbose, 3)  # 限制 verbose 最大值为 3
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    set_logger_level_from_ctx(ctx, logger)
    set_logger_style(logger, "fancy")  # 设置日志样式为 fancy

cli.add_command(aivk_mcp)
cli.add_command(run)
cli.add_command(shell)

cli.add_command(debug, name="debug")

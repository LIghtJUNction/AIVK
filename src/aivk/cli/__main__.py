from click import group
from aivk.cli.amcp import aivk_mcp
from aivk.cli.list import aivk_list
from aivk.cli.install import install
from aivk.cli.uninstall import uninstall
from aivk.cli.run import run


@group()
def cli():
    """
    AIVK CLI
    """
    pass

cli.add_command(aivk_mcp)
cli.add_command(aivk_list)
cli.add_command(install)
cli.add_command(uninstall)
cli.add_command(run)
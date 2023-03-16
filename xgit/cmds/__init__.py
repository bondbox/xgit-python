# coding:utf-8

import os
from typing import Optional
from typing import Sequence

from git.repo.base import Repo
from xarg import add_command
from xarg import argp
from xarg import chdir
from xarg import commands
from xarg import run_command

from ..utils import URL_PROG
from ..utils import __prog_name__
from ..utils import __version__
from .modify import add_cmd_modify_person
from .summary import add_cmd_csv_summary
from .tag import add_cmd_verify_tag
from .update import add_cmd_safe_sync


@add_command(__prog_name__)
def add_cmd(_arg: argp):
    _arg.add_argument("-w", "--workdir", type=str, nargs=1, metavar="DIR",
                      default=["."], help="Change to work directory")
    _arg.add_opt_on("--fetch", help="Fetch all remotes")


@run_command(add_cmd, add_cmd_csv_summary, add_cmd_verify_tag,
             add_cmd_modify_person, add_cmd_safe_sync)
def run_cmd(cmds: commands) -> int:
    if isinstance(cmds.args.workdir, list):
        chdir().pushd(cmds.args.workdir[0])
        cmds.logger.info(f"Entering directory {os.getcwd()}")
    if cmds.args.fetch:
        for remote in Repo().remotes:
            cmds.logger.debug(f"Fetch remote {remote.name}")
            remote.fetch()
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = commands()
    cmds.version = __version__
    return cmds.run(
        root=add_cmd,
        argv=argv,
        description="Git command enhancement",
        epilog=f"For more, please visit {URL_PROG}.")

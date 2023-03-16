# coding:utf-8

import sys
from typing import List

from git import Repo
from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ..utils.git import list_all_references


@add_command("csv-format-summary", help="list commit summary in CSV format")
def add_cmd_csv_summary(_arg: argp):
    grp = _arg.add_argument_group("Commit Formatting")
    grp.add_argument("--abbrev-commit", dest="commit_id_format",
                     action="store_const", const="%h", default="%H",
                     help="print abbreviated commit hash")
    grp.add_argument("--disable-author", action="store_true",
                     help="disable print author, default enable")
    grp.add_argument("--author-email", dest="author_format",
                     action="store_const", const="%an <%ae>", default="%an",
                     help="print author name and email, default only name")
    grp.add_argument("--enable-committer", action="store_true",
                     help="enable print committer, default disable")
    grp.add_argument("--committer-email", dest="committer_format",
                     action="store_const", const="%cn <%ce>", default="%cn",
                     help="print committer name and email, default only name")
    grp.add_argument("--datetime", dest="date_format", action="store_const",
                     const="format:%F %T", default="format:%F",
                     help="print datetime, default print date")
    grp.add_argument("--disable-ref-names", action="store_true",
                     help="disable print ref names, default enable")
    mgrp = grp.add_mutually_exclusive_group()
    mgrp.add_argument("--space-delimiter", dest="delimiter",
                      action="store_const", const=" ", default=", ",
                      help="separate with space, default comma-space(, )")
    mgrp.add_argument("--comma-delimiter", dest="delimiter",
                      action="store_const", const=",", default=", ",
                      help="separate with comma, default comma-space(, )")

    # TODO: filter file
    grp = _arg.add_argument_group("Commit Limiting")
    grp.add_argument("--max-count", type=int, nargs=1, metavar="NUMBER",
                     help="limit the number of commits to output")
    grp.add_argument("--authors", type=str, nargs="+",
                     metavar="AUTHOR", help="filter authors")
    grp.add_argument("--committers", type=str, nargs="+",
                     metavar="COMMITTER", help="filter committers")
    args = _arg.preparse_from_sys_argv()
    repo = Repo(path=args.workdir[0])
    grp.add_argument("--reference", type=str, nargs=1, metavar="REF",
                     choices=list_all_references(repo=repo),
                     help=f"specify reference, default '{repo.active_branch}'")


@run_command(add_cmd_csv_summary)
def run_cmd_csv_summary(cmds: commands) -> int:
    assert isinstance(cmds.args.delimiter, str)
    _format: List[str] = [cmds.args.commit_id_format]
    if not cmds.args.disable_author:
        _format.extend(["%ad", cmds.args.author_format])
    if cmds.args.enable_committer:
        _format.extend(["%cd", cmds.args.committer_format])
    _format.append("%s")  # subject
    if not cmds.args.disable_ref_names:
        # ref names, like the --decorate option of git-log
        _format.append("%d")

    repo = Repo(path=cmds.args.workdir[0])
    cmd = ["git", "log", f"--format={cmds.args.delimiter.join(_format)}",
           f"--date={cmds.args.date_format}"]
    if isinstance(cmds.args.max_count, list):
        cmd.append(f"--max-count={cmds.args.max_count[0]}")
    if isinstance(cmds.args.authors, list):
        authors = "\\|".join(cmds.args.authors)
        cmd.append(f"--author={authors}")
    if isinstance(cmds.args.committers, list):
        committers = "\\|".join(cmds.args.committers)
        cmd.append(f"--committer={committers}")
    if isinstance(cmds.args.reference, list):
        cmd.append(cmds.args.reference[0])
    cmds.logger.debug("command: {}".format(" ".join(f"'{i}'" for i in cmd)))
    repo.git.execute(cmd, output_stream=sys.stdout.buffer)  # type: ignore
    return 0

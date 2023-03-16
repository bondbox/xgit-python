# coding:utf-8

from typing import Dict
from typing import List

from git import Commit
from git import Repo
from tabulate import tabulate
from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command


@add_command("verify-tag", help="verify and list tags")
def add_cmd_verify_tag(_arg: argp):
    _arg.add_opt_on("--disable-commit-id", help="disable print commit id")
    _arg.add_opt_on("--enable-is-remote", help="enable print is_remote")
    _arg.add_opt_on("--enable-is-detached", help="enable print is_detached")


@run_command(add_cmd_verify_tag)
def run_cmd_verify_tag(cmds: commands) -> int:
    repo = Repo(path=cmds.args.workdir[0])

    tabular_head: List[str] = ["name"]
    if not cmds.args.disable_commit_id:
        tabular_head.append("commit")
    tabular_head.append("is_valid")
    if cmds.args.enable_is_remote:
        tabular_head.append("is_remote")
    if cmds.args.enable_is_detached:
        tabular_head.append("is_detached")
    tabular_data: List[List] = list()
    for tag in repo.tags:
        item: Dict = {"name": tag.name}
        if not cmds.args.disable_commit_id:
            commit = tag.commit
            cid = commit.hexsha if isinstance(commit, Commit) else None
            item["commit"] = cid
        item["is_valid"] = tag.is_valid()
        if cmds.args.enable_is_remote:
            item["is_remote"] = tag.is_remote()
        if cmds.args.enable_is_detached:
            item["is_detached"] = tag.is_detached
        tabular_data.append([item[k] for k in tabular_head])
    table = tabulate(tabular_data, headers=tabular_head)
    cmds.stdout(table)
    return 0

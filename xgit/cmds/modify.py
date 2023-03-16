# coding:utf-8

from git import Repo
from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ..utils.git import get_user_email
from ..utils.git import get_user_name


@add_command("modify-person",
             help="batch modify name and email of authors or committers")
def add_cmd_modify_person(_arg: argp):
    _arg.add_opt_on("--gc", help="GC before modify, accelerate batch")
    _arg.add_pos("name_or_email", type=str, nargs="+", metavar="NAME_OR_EMAIL",
                 help="any name or email to modify, full match mode")

    args = _arg.preparse_from_sys_argv()
    repo = Repo(path=args.workdir[0])
    user_name = get_user_name(repo=repo)
    user_email = get_user_email(repo=repo)
    default_name_str = ", default '{user_email}'" if user_name else ""
    default_email_str = ", default '{user_email}'" if user_email else ""

    grp = _arg.add_argument_group("modify options")
    grp.add_argument("--name", type=str, nargs=1, default=[user_name],
                     help="specify name" + default_name_str)
    grp.add_argument("--email", type=str, nargs=1, default=[user_email],
                     help="specify email" + default_email_str)
    mgrp = grp.add_mutually_exclusive_group()
    mgrp.add_argument("--only-authors", dest="modify_which",
                      action="store_const", const="authors", default="all",
                      help="only modify name and email of authors")
    mgrp.add_argument("--only-committers", dest="modify_which",
                      action="store_const", const="committers", default="all",
                      help="only modify name and email of committers")


@run_command(add_cmd_modify_person)
def run_cmd_modify_person(cmds: commands) -> int:
    repo = Repo(path=cmds.args.workdir[0])
    assert not repo.is_dirty(), "You have unstaged changes."

    if cmds.args.gc:
        cmds.logger.info("git gc")
        cmds.logger.debug(repo.git.gc())

    name = cmds.args.name[0]
    email = cmds.args.email[0]
    modify_which: str = cmds.args.modify_which
    assert isinstance(name, str), "Please specify the correct name"
    assert isinstance(email, str), "Please specify the correct email"
    name_or_email = " ".join([f'"{i}"' for i in cmds.args.name_or_email])
    cmds.logger.info(f"batch modify {modify_which}: {name_or_email}")

    ctx_author = f"""
if [ "$GIT_AUTHOR_NAME" = "$n" ]; then
 export GIT_AUTHOR_NAME="{name}"; export GIT_AUTHOR_EMAIL="{email}";
elif [ "$GIT_AUTHOR_EMAIL" = "$n" ]; then
 export GIT_AUTHOR_NAME="{name}"; export GIT_AUTHOR_EMAIL="{email}";
fi;""" if modify_which == "all" or modify_which == "authors" else ""
    ctx_committer = f"""
if [ "$GIT_COMMITTER_NAME" = "$n" ]; then
 export GIT_COMMITTER_NAME="{name}"; export GIT_COMMITTER_EMAIL="{email}";
elif [ "$GIT_COMMITTER_EMAIL" = "$n" ]; then
 export GIT_COMMITTER_NAME="{name}"; export GIT_COMMITTER_EMAIL="{email}";
fi;""" if modify_which == "all" or modify_which == "committers" else ""
    context = f"for n in {name_or_email}; do {ctx_author} {ctx_committer} done"
    command = [
        "git", "filter-branch", "--env-filter", context, "--tag-name-filter",
        "cat", "--force", "--", "--branches", "--tags",
    ]
    cmds.logger.debug(repo.git.execute(command))

    return 0

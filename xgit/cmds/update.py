# coding:utf-8

from errno import ENOEXEC
from typing import List
from typing import Optional

from git import Commit
from git import GitCommandError
from git import Reference
from git import RemoteReference
from git import Repo
from git import TagObject
from xarg import add_command
from xarg import argp
from xarg import commands
from xarg import run_command

from ..utils.git import list_all_references
from ..utils.git import list_all_remote_references


@add_command("safe-sync", help="safely sync with another reference",
             description="""safely sync the active branch to keep it
             up-to-date with another reference""")
def add_cmd_safe_sync(_arg: argp):
    args = _arg.preparse_from_sys_argv()
    repo = Repo(path=args.workdir[0])
    active_branch = repo.active_branch.name
    _arg.add_opt_on("--disable-fetch", help="disable fetch remote before sync")
    _arg.add_argument("--push-to-remote", type=str, nargs="?",
                      const="", default=None, metavar="REFERENCE",
                      choices=list_all_remote_references(repo=repo) + [""],
                      help="push active branch to remote after success")
    _arg.add_argument("--active-branch", type=str, nargs=1, metavar="BRANCH",
                      default=[active_branch], choices=repo.branches,
                      help=f"switch to branch, default '{active_branch}'")
    _arg.add_argument("sync_reference", type=str, nargs=1, metavar="REFERENCE",
                      choices=list_all_references(repo=repo),
                      help="specify another branch to sync with active branch")


@run_command(add_cmd_safe_sync)
def run_cmd_safe_sync(cmds: commands) -> int:
    repo = Repo(path=cmds.args.workdir[0])
    assert not repo.is_dirty(), "You have unstaged changes."

    ref_s = cmds.args.sync_reference[0]
    ref_a = cmds.args.active_branch[0]
    assert isinstance(ref_s, str), f"Unexpected type: {type(ref_s)}"
    assert isinstance(ref_a, str), f"Unexpected type: {type(ref_a)}"
    assert ref_s != ref_a, f"'{ref_s}' is active branch"
    if ref_a != repo.active_branch.name:
        cmds.logger.info(f"switch to branch: '{ref_a}'")
        cmds.logger.debug(repo.git.checkout(ref_a))

    reference: Reference = [_r for _r in repo.refs if _r.name == ref_s][0]
    push_to_remote: Optional[str] = cmds.args.push_to_remote
    push_ref: Optional[RemoteReference] = None
    if isinstance(push_to_remote, str):
        if push_to_remote == "":
            if isinstance(reference, RemoteReference):
                push_ref = reference
        else:
            for _r in repo.refs:
                if _r.name == push_to_remote:
                    push_ref = _r if isinstance(_r, RemoteReference) else None
                    break

    if not cmds.args.disable_fetch and isinstance(reference, RemoteReference):
        cmds.logger.info(f"fetch from repository: '{reference.remote_name}'")
        fetch_info = repo.remote(reference.remote_name).fetch()
        cmds.logger.info(f"remote references: {[r.name for r in fetch_info]}")

    commit_a = repo.rev_parse(ref_a)
    commit_s = repo.rev_parse(ref_s)
    assert isinstance(commit_a, Commit), f"Unexpected type: {type(commit_a)}"
    assert isinstance(commit_s, (Commit, TagObject)), \
        f"Unexpected type: {type(commit_s)}"
    shortid_a = repo.git.rev_parse("--short=10", commit_a.hexsha)
    shortid_s = repo.git.rev_parse("--short=10", commit_s.hexsha)
    cmds.logger.info(f"sync from {shortid_a}({ref_a}) to {shortid_s}({ref_s})")

    if commit_a.hexsha == commit_s.hexsha:
        cmds.logger.info(f"'{ref_a}' is up to date with '{ref_s}'")
        return 0

    res = repo.merge_base(commit_a.hexsha, commit_s.hexsha)
    assert isinstance(res, List), f"Unexpected type: {type(res)}"
    assert len(res) == 1, "no common ancestor, cannot sync"
    base_commit = res[0]
    assert isinstance(base_commit, Commit), \
        f"Unexpected type: {type(base_commit)}"
    base_hexsha = base_commit.hexsha
    cmds.logger.info(f"merge base: {base_hexsha}")

    def __iter_commits(rev: Commit) -> List[Commit]:
        _commits: List[Commit] = list()
        for _commit in repo.iter_commits(rev):
            if _commit.hexsha == base_hexsha:
                break
            _commits.append(_commit)
        return _commits

    before_base: List[Commit] = __iter_commits(commit_a)
    behind_sync: List[Commit] = __iter_commits(commit_s)

    num_before_base = len(before_base)
    num_behind_sync = len(behind_sync)
    if num_before_base == 0 and num_behind_sync == 0:
        cmds.logger.info("nothing to do")
        return 0

    compare: List[str] = list()
    if num_before_base > 0:
        compare.append("{} commit{} ahead of".format(
            num_before_base, "s" if num_before_base > 1 else ""))
    if num_behind_sync > 0:
        compare.append("{} commit{} behind".format(
            num_behind_sync, "s" if num_behind_sync > 1 else ""))
    cmds.logger.info(f"'{ref_a}' is {', '.join(compare)} '{ref_s}'")

    def __push() -> bool:
        if not push_ref:
            cmds.logger.info("disable push to remote")
            return True
        # repo.remote(remote_ref.remote_name).push(remote_ref.remote_head)
        try:
            cmds.logger.info(f"push '{ref_a}' to remote: '{push_ref.name}'")
            cmds.logger.debug(repo.git.push(push_ref.remote_name,
                                            f"{ref_a}:{push_ref.remote_head}"))
            return True
        except GitCommandError:
            return False

    if num_behind_sync == 0:
        if num_before_base > 0:
            return 0 if __push() else ENOEXEC
        return 0

    def __merge(ref: str) -> bool:
        try:
            cmds.logger.debug(repo.git.merge("--no-edit", ref))
            return True
        except GitCommandError:
            cmds.logger.debug(f"merge abort (merge {ref} failed)")
            cmds.logger.debug(repo.git.merge("--abort"))
            return False

    def __revert(hexsha: str) -> bool:
        try:
            cmds.logger.info(f"revert {hexsha}")
            cmds.logger.debug(repo.git.revert("--no-edit", hexsha))
            return True
        except GitCommandError:
            cmds.logger.info(f"revert abort (revert {hexsha} failed)")
            cmds.logger.debug(repo.git.revert("--abort"))
            return False

    if __merge(ref_s):
        cmds.logger.info(f"update to {shortid_s}({ref_s}) success")
        return 0

    for commit in before_base:
        if not __revert(commit.hexsha):
            return ENOEXEC

        if __merge(ref_s):
            cmds.logger.info(f"merge to {shortid_s}({ref_s}) success")
            return 0 if __push() else ENOEXEC

    return ENOEXEC

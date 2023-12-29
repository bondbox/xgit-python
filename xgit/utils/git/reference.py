# coding:utf-8

from typing import List
from typing import Optional

from git import Head
from git import RemoteReference
from git import Repo
from git import TagReference


def list_all_references(repo: Optional[Repo] = None,
                        workdir: Optional[str] = None) -> List[str]:
    try:
        _repo = repo or Repo(path=workdir)
        return [_ref.name for _ref in _repo.refs if isinstance(
            _ref, (Head, RemoteReference, TagReference))]
    except BaseException:
        return list()


def list_all_remote_references(repo: Optional[Repo] = None,
                               workdir: Optional[str] = None) -> List[str]:
    try:
        _repo = repo or Repo(path=workdir)
        return [_ref.name for _ref in _repo.refs if isinstance(
            _ref, RemoteReference)]
    except BaseException:
        return list()


def list_local_branches(repo: Optional[Repo] = None,
                        workdir: Optional[str] = None) -> List[str]:
    try:
        _repo = repo or Repo(path=workdir)
        return [_branch.name for _branch in _repo.branches]
    except BaseException:
        return list()


def list_all_branches(repo: Optional[Repo] = None,
                      workdir: Optional[str] = None) -> List[str]:
    try:
        _repo = repo or Repo(path=workdir)
        branches = [_branch.name for _branch in _repo.branches]
        for _remote in _repo.remotes:
            branches.extend([_ref.name for _ref in _remote.refs])
        return branches
    except BaseException:
        return list()

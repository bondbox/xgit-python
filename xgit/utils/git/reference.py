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


def list_all_branches(repo: Optional[Repo] = None,
                      workdir: Optional[str] = None) -> List[str]:
    try:
        _repo = repo or Repo(path=workdir)
        branches = ["HEAD"]
        branches.extend([branch.name for branch in _repo.branches])
        for remote in _repo.remotes:
            branches.extend([ref.name for ref in remote.refs])
        return branches
    except BaseException:
        return list()

# coding:utf-8

import os
from typing import Dict
from typing import Optional
from typing import Sequence

from git import Git
from git import GitCommandError

_git_exc_cache: Dict[str, Dict[str, str]] = dict()


def cache_execute(_git: Git, _cmd_array: Sequence[str]) -> Optional[str]:
    working_dir: str = str(_git.working_dir or os.getcwd())
    if working_dir not in _git_exc_cache:
        _git_exc_cache.setdefault(working_dir, dict())

    _cmd: str = " ".join(_cmd_array)
    _cmd_cache = _git_exc_cache[working_dir]
    if _cmd in _cmd_cache:
        print(working_dir, "cache", _cmd_cache[_cmd])
        return _cmd_cache[_cmd]
    print(working_dir, "no cache")

    try:
        out = _git.execute(_cmd_array)
        assert isinstance(out, str)
        _cmd_cache[_cmd] = out
        return out
    except GitCommandError:
        pass

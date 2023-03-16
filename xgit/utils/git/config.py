# coding:utf-8

from typing import Optional

from git import Repo


def get_user_name(repo: Optional[Repo] = None,
                  workdir: Optional[str] = None) -> Optional[str]:
    _repo = repo or Repo(path=workdir)
    _conf = _repo.config_reader()
    return _conf.get("user", "name") if _conf.has_section("user") else None


def get_user_email(repo: Optional[Repo] = None,
                   workdir: Optional[str] = None) -> Optional[str]:
    _repo = repo or Repo(path=workdir)
    _conf = _repo.config_reader()
    return _conf.get("user", "email") if _conf.has_section("user") else None

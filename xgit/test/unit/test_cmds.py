# coding:utf-8

import os
from tempfile import TemporaryDirectory
import unittest
import uuid

from git import Repo

from xgit.cmds import main

TESTURL = "https://github.com/bondbox/xgit-test.git"
TESTSSH = "git@github.com:bondbox/xgit-test.git"


class test_cmds(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.path = os.path.join(self.temp.name, uuid.uuid4().hex)
        self.repo = Repo.clone_from(TESTURL, self.path)

    def tearDown(self):
        pass

    def test_fetch(self):
        ret = main(argv=["-w", self.path, "--fetch"])
        self.assertEqual(ret, 0)

    def test_csv_format_summary(self):
        ret = main(argv=["-w", self.path, "csv-format-summary",
                         "--reference=origin/HEAD", "--abbrev-commit",
                         "--max-count=10", "--author-email",
                         "--enable-committer", "--committer-email",
                         "--authors=Mingzhe Zou", "--committers=Mingzhe Zou"])
        self.assertEqual(ret, 0)

    def test_modify_person(self):
        ret = main(argv=["-w", self.path, "modify-person", "--gc",
                         "--name=Mingzhe Zou", "--email=zoumingzhe@qq.com",
                         "root", "root@example.com",
                         "test", "test@example.com"])
        self.assertEqual(ret, 0)

    def test_verify_tag(self):
        ret = main(argv=["-w", self.path, "verify-tag",
                         "--enable-is-remote", "--enable-is-detached"])
        self.assertEqual(ret, 0)

    def test_safe_sync_A_to_X(self):
        self.repo.git.checkout("-b", "A", "--track", "origin/A")
        self.repo.git.reset("--hard", "tag-A")
        self.repo.git.checkout("master")
        ret = main(argv=["-w", self.path, "safe-sync", "--disable-fetch",
                         "--active-branch=A", "origin/X"])
        self.assertEqual(ret, 0)

    def test_safe_sync_B_to_A(self):
        self.repo.git.checkout("-b", "B", "--track", "origin/B")
        self.repo.git.reset("--hard", "tag-B")
        self.repo.git.push("-f", "origin", "master:B")
        self.repo.git.checkout("master")
        ret = main(argv=["-w", self.path, "safe-sync", "--push-to-remote",
                         "--active-branch=B", "tag-A"])
        self.assertEqual(ret, 0)

    def test_safe_sync_X_to_B(self):
        self.repo.git.reset("--hard", "tag-init")
        self.repo.git.push("-f", "origin", "master:init", "master:Y")
        self.repo.git.checkout("-b", "X", "--track", "origin/X")
        self.repo.git.reset("--hard", "tag-X")
        self.repo.git.checkout("master")
        ret = main(argv=["-w", self.path, "safe-sync",
                         "--push-to-remote=origin/Y",
                         "--active-branch=X", "tag-B"])
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()

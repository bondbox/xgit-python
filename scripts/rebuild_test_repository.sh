#!/usr/bin/env bash
git checkout master && git reset --hard origin/master

# reset remote
git reset --hard tag-A && git push -f origin master:A
git reset --hard tag-B && git push -f origin master:B
git reset --hard tag-X && git push -f origin master:X
git reset --hard tag-init && git push -f origin master:init master:Y

# reset branch
git checkout A && git reset --hard tag-A
git checkout B && git reset --hard tag-B
git checkout X && git reset --hard tag-X

git checkout master && git reset --hard origin/master

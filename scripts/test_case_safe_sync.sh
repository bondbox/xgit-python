#!/usr/bin/env bash


echo "------------------------------------------------------------"
xgit verify-tag --enable-is-remote --enable-is-detached && sleep 1
echo "------------------------------------------------------------"

echo "summary: A -> origin/X, disable fetch, disable push"
xgit safe-sync --stdout --info --disable-fetch --active-branch A origin/X

echo "------------------------------------------------------------"
xgit csv-format-summary --abbrev-commit && sleep 1
echo "------------------------------------------------------------"

echo "summary: B -> origin/A, enable fetch, push to origin/A"
xgit safe-sync --stdout --info --push-to-remote --active-branch B origin/A

echo "------------------------------------------------------------"
xgit csv-format-summary --abbrev-commit && sleep 1
echo "------------------------------------------------------------"

echo "summary: X -> origin/B, enable fetch, push to origin/Y"
xgit safe-sync --stdout --info --push-to-remote origin/Y --active-branch X origin/B

echo "------------------------------------------------------------"
xgit csv-format-summary --abbrev-commit && sleep 1
echo "------------------------------------------------------------"

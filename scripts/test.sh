#!/usr/bin/env bash
pushd $(dirname $0)
CWD=$PWD

for test_case in $(ls -1 test_case_*.sh); do
    pushd ${CWD}/../test
    ${CWD}/rebuild_test_repository.sh
    echo "${test_case}"
    ${CWD}/${test_case}
    popd
done

popd

#!/bin/bash
set -e           # Exit on errors...

cd "$(dirname "$0")"


for dir in *; do
    if test -f "./$dir/testAll.sh"; then
        echo -e "\n--------------------\nEvaluating $dir\n--------------------\n\n"
        "./$dir/testAll.sh"
        echo -e "\n--------------------\nFinished $dir\n--------------------\n\n"
    fi
done

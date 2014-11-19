#!/bin/bash
set -e           # Exit on errors...

# Use GNU readlink on Mac OS.
if which greadlink >/dev/null 2>&1; then
    readlink() { greadlink "$@"; }
fi

DIR="$(readlink -f "$(dirname "$0")")"
cd "$DIR"

for dir in *; do
    if test -f "./$dir/testAll.sh"; then
        echo -e "\n--------------------\nEvaluating $dir\n--------------------\n\n"
        "./$dir/testAll.sh"
        echo -e "\n--------------------\nFinished $dir\n--------------------\n\n"
    fi
done

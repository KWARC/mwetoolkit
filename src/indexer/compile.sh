#!/bin/bash
cd "$(dirname "$0")"
[[ -d autoheaders ]] || mkdir autoheaders
./genheader.sh *.c
gcc -Wall -Wno-deprecated -Wno-parentheses -I . -I autoheaders -o c-indexer *.c

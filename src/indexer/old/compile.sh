#!/bin/bash
cd "$(dirname "$0")"
[[ -d autoheaders ]] || mkdir autoheaders
#./genheader.sh *.c
gcc -Wall -Wno-parentheses -I . -I include -o c-indexer *.c

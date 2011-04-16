#!/bin/bash
cd "$(dirname "$0")"
[[ -d autoheaders ]] || mkdir autoheaders
./genheader.sh *.c
gcc -I . -I autoheaders -o index *.c

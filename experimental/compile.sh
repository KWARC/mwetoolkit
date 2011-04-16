#!/bin/bash
cd "$(dirname "$0")"
./genheader.sh *.c
gcc -I . -I autoheaders -o index *.c

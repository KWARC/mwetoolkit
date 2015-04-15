#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Error: specify username"
    exit -1
fi

echo "Warning: not showing directory permission modifications"

rsync -rlptC --stats --compress --del --progress -i htdocs $1,mwetoolkit@web.sf.net: | sed '/^\.d\.\.\.p\.\.\.\.\./d'

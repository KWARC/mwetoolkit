#!/bin/bash
set -e           # Exit on errors...
exec </dev/null  # Don't hang if a script tries to read from stdin.

testgread=`which greadlink` || true  # Adaptation for MAC OS, because readlink for
if [ -z $testgread ]; then           # MAC OS does not accept the -f opt
	DIR="$(readlink -f "$(dirname "$0")")"
else
	DIR="$(greadlink -f "$(dirname "$0")")"
fi

TOOLKITDIR="$DIR/../.."
OUTDIR="$DIR/output"

cd "$DIR"
[[ -d output ]] && rm -R output

"$TOOLKITDIR/bin/mweconsole.sh" -y <<EOF
	create-project output -n    # Don't enter project directory
	corpus corpus.xml
	patterns patterns.xml
	extract
	index
	extract
	count
	association
EOF

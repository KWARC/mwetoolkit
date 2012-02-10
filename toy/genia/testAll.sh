#!/bin/bash

set -e           # Exit on errors.
exec </dev/null  # Don't hang if a script tries to read from stdin.
testgread=`which greadlink`   # Adaptation for MAC OS, because readlink for
if [ -z $testgread ]; then    # MAC OS does not accept the -f opt
	alias greadlink="readlink"; 
fi

DIR="$(greadlink -f $(dirname "$0"))"
TOOLKITDIR="$DIR/../.."
OUTDIR="$DIR/output"

run() {
	local script="$1"; shift
	python "$TOOLKITDIR/bin/$script" "$@"
}

dotest() {
	[[ $# -eq 3 ]] || { echo "dotest: Invalid arguments: $*" >&2; exit 2; }
	local name="$1" run="$2" verify="$3"

	((testnum++ < tests_to_skip)) && return 0		

	printf "\e[1m%d. %s\e[0m\n" "$testnum" "$name"
	printf "\e[1;33m%s\e[0m\n" "$run"

	if eval time "$run" && eval "$test"; then
		printf "\e[1;32mOK\e[0m\n"
	else
		printf "\e[1;31mFAILED!\e[0m\n"
		exit 1
	fi
}

diff-sorted() {
	diff <(sort "$1") <(sort "$2")
}

main() {
	cd "$DIR"
	[[ -e dtd ]] || ln -s "$TOOLKITDIR/dtd" .
	[[ -d $OUTDIR ]] || mkdir "$OUTDIR"

	cd "$OUTDIR"
	[[ -e dtd ]] || ln -s "$TOOLKITDIR/dtd" .

	testnum=0
	tests_to_skip=0

	while [[ $# -gt 0 ]]; do
		case "$1" in
			-s) tests_to_skip="$2"; shift ;;
			*) echo "Unknown option \"$1\"!" >&2; return 1 ;;
		esac
		shift
	done

	dotest "Corpus indexing" \
		'run index.py -v -i corpus "$DIR/corpus.xml"' \
		'true'

	dotest "Extraction from index" \
		'run candidates.py -s -v -p "$DIR/patterns.xml" -i corpus >candidates-from-index.xml' \
		true

	dotest "Extraction from XML" \
		'run candidates.py -s -v -p "$DIR/patterns.xml" "$DIR/corpus.xml" >candidates-from-corpus.xml' \
		true

	dotest "Comparison of candidate extraction outputs" \
		'diff-sorted candidates-from-index.xml candidates-from-corpus.xml' \
		true

	dotest "Individual word frequency counting" \
		'run counter.py -s -v -i corpus candidates-from-index.xml >candidates-counted.xml' \
		true

	dotest "Association measures" \
		'run feat_association.py -v -m "mle:pmi:t:dice" candidates-counted.xml >candidates-featureful.xml' \
		true

}

main "$@"

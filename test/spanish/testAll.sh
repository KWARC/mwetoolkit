#!/bin/bash
set -e           # Exit on errors...
exec </dev/null  # Don't hang if a script tries to read from stdin.

# Use GNU readlink on Mac OS.
if which greadlink >/dev/null 2>&1; then
	readlink() { greadlink "$@"; }
fi

DIR="$(readlink -f "$(dirname "$0")")"

TOOLKITDIR="$DIR/../.."
OUTDIR="$DIR/output"

run() {
	local script="$1"; shift
	eval python "$TOOLKITDIR/bin/$script" --debug "$@"
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
	[[ -e corpus.xml ]] || cp ../corpus.xml .

	testnum=0
	tests_to_skip=0

	while [[ $# -gt 0 ]]; do
		case "$1" in
			-s) tests_to_skip="$(($2-1))"; shift ;;
			*) echo "Unknown option \"$1\"!" >&2; return 1 ;;
		esac
		shift
	done

	dotest "Corpus indexing" \
		'run index.py -v -i corpus "corpus.xml"' \
		'true'

	dotest "Extraction from index" \
		'run candidates.py -v -p "$DIR/patterns.xml" -i corpus >candidates-from-index.xml' \
		true

	dotest "Extraction from XML" \
		'run candidates.py -v -p "$DIR/patterns.xml" "corpus.xml" >candidates-from-corpus.xml' \
		true
	
	dotest "Extraction from XML" \
		'run candidates.py -v -n 2 "corpus.xml" >candidates-bigram.xml' \
		true
	
	dotest "Extraction from XML" \
		'run candidates.py -v -n 3 "corpus.xml" >candidates-trigram.xml' \
		true

	dotest "Comparison of candidate extraction outputs" \
		'diff-sorted candidates-from-index.xml candidates-from-corpus.xml' \
		true

	dotest "Individual word frequency counting" \
		'run counter.py -v -i corpus candidates-from-index.xml >candidates-counted.xml' \
		true

	dotest "Association measures" \
		'run feat_association.py -v -m "mle:pmi:t:dice:ll" candidates-counted.xml >candidates-featureful.xml' \
		true

	#dotest "Evaluation" \
		'run eval_automatic.py -v -r "$DIR/reference.xml" -g candidates-featureful.xml >eval.xml 2>eval-stats.txt' \
		true

	#dotest "Mean Average Precision" \
		'run map.py -v -f "mle_corpus:pmi_corpus:t_corpus:dice_corpus:ll_corpus" eval.xml >map.txt' \
		true
}

main "$@"

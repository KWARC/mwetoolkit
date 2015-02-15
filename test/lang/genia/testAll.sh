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
	eval python "${TOOLKITDIR}/bin/${script}" "$@"

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
		source "$DIR/../testlib.sh"
		t_backtrace
		printf "\e[1;31mTest $testnum FAILED!\e[0m\n"
		exit 1
	fi
}

diff-sorted() {
	diff <(sort "$1") <(sort "$2")
}

main() {
	cd "$DIR"
	[[ -d $OUTDIR ]] || mkdir "$OUTDIR"

	cd "$OUTDIR"

	testnum=0
	tests_to_skip=0

	while [[ $# -gt 0 ]]; do
		case "$1" in
			-s) tests_to_skip="$(($2-1))"; shift ;;
			*) echo "Unknown option \"$1\"!" >&2; return 1 ;;
		esac
		shift
	done

	dotest "Conversion from TreeTagger to XML" \
		'run treetagger2xml.py -v "$DIR/corpus-treetagger.txt" >corpus-ptb-tags.xml' \
		true

	dotest "POS tag simplification" \
		'run changepos.py -v corpus-ptb-tags.xml >corpus.xml' \
		true

	dotest "Corpus indexing" \
		'run index.py -v -i corpus "corpus.xml"' \
		'true'

	dotest "Extraction from index" \
		'run candidates.py -sD -v -p "$DIR/patterns.xml" -i corpus.info >candidates-from-index.xml' \
		true

	dotest "Extraction from XML" \
		'run candidates.py -s -v -p "$DIR/patterns.xml" "corpus.xml" >candidates-from-corpus.xml' \
		true

	dotest "Extraction with Longest match-distance" \
		'run candidates.py --match-distance=Longest -s -v -p "$DIR/patterns.xml" "corpus.xml" >long-candidates.xml' \
		true

	dotest "Extraction with Non-Overlapping Longest match-distance" \
		'run candidates.py --match-distance=Longest --non-overlapping -s -v -p "$DIR/patterns.xml" "corpus.xml" >long-candidates-nonoverlap.xml' \
		true

	dotest "Comparison of candidate extraction outputs" \
		'diff-sorted candidates-from-index.xml candidates-from-corpus.xml' \
		true

	dotest "Individual word frequency counting" \
		'run counter.py -s -v -i corpus.info candidates-from-index.xml >candidates-counted.xml' \
		true

	dotest "Association measures" \
		'run feat_association.py -v -m "mle:pmi:t:dice:ll" candidates-counted.xml >candidates-featureful.xml' \
		true

	dotest "Evaluation" \
		'run eval_automatic.py -v -r "$DIR/reference.xml" -g candidates-featureful.xml >eval.xml 2>eval-stats.txt' \
		true

	dotest "Mean Average Precision" \
		'run map.py -v -f "mle_corpus:pmi_corpus:t_corpus:dice_corpus:ll_corpus" eval.xml >map.txt' \
		true

	for format in csv arff evita owl ucs; do
		dotest "Conversion from XML to $format" \
			'run xml2$format.py -v candidates-featureful.xml >candidates-featureful.$format 2>warnings-$format.txt' \
			true
	done

	dotest "Take first 50 candidates" \
		'run head.py -v -n 50 candidates-featureful.xml >candidates-featureful-head.xml' \
		true

	dotest "Take last 50 candidates" \
		'run tail.py -v -n 50 candidates-featureful.xml >candidates-featureful-tail.xml' \
		true

	dotest "Take first 50 corpus sentences" \
		'run head.py -v -n 50 corpus.xml >corpus-head.xml' \
		true

	dotest "Take last 50 corpus sentences" \
		'run tail.py -v -n 50 corpus.xml >corpus-tail.xml' \
		true

	for base in candidates-featureful corpus; do
		for suffix in '' -head -tail; do
			dotest "Word count for $base$suffix" \
				"run wc.py $base$suffix.xml 2>&1 | tee wc-$base$suffix.txt" \
				true
		done
	done

	dotest "Removal of duplicated candidates" \
		'run uniq.py candidates-featureful.xml >candidates-uniq.xml' \
		true

	dotest "Removal of duplicated candidates ignoring POS" \
		'run uniq.py -g candidates-featureful.xml >candidates-uniq-nopos.xml' \
		true

	dotest "Filtering out candidates occurring less than twice" \
		'run filter.py -t 2 candidates-featureful.xml >candidates-twice.xml' \
		true

	dotest "Comparison against reference output" \
		compare-to-reference \
		true
}

compare-to-reference() {
	tar -C .. -xvf ../reference-output.tar.bz2
	countfail=0
	errorreport="`pwd`/../error-report.log"
	printf "" > $errorreport
	for file in *.*; do
		ref="../reference-output/$file"
		printf "  Comparing %s... " "$file"
		if [[ $file == *candidates* || $file == *eval* ]]; then
			cmp -s <(sort "$file") <(sort "$ref")
		elif [[ $file == *.suffix || $file == warning* || $file == *.corpus ]]; then
			echo "IGNORED"
			continue
		else
			cmp -s "$file" "$ref"
		fi			
		if [[ $? -eq 0 ]]; then
			echo "OK"
		else
			echo "FAILED!"
			difference=`diff <(sort "$file") <(sort "$ref")`
			echo -ne "\n-----------------------\nFile: ${file}\n${difference}" >> $errorreport
			#return 1
			(( countfail++ ))
		fi
	done
	if [[ countfail -gt 0 ]]; then
		printf "\n\e[1;31mWARNING: $countfail tests FAILED!\e[0m\n"
		printf "Please consult the detailed error report in $errorreport\n"
	fi
}


main "$@"

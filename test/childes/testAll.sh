#! /bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/../testlib.sh"

usage_exit() { {
    echo "Usage: $(basename "$0") [-h] [-s]"
    echo "Test Childes."
    exit 1
} 1>&2;
}


tests_to_skip=0

while test $# -gt 0; do
    case "$1" in
        -s) t_N_TESTS_LIMIT="$(($2-1))"; shift ;;
        *) echo "Unknown option \"$1\"!" >&2; return 1 ;;
    esac
    shift
done

test "$#" -ne 0  && usage_exit


##################################################


DIR="$(readlink -f "$(dirname "$0")")"

TOOLKITDIR="$DIR/../.."
OUTDIR="$DIR/output"
TESTNUM=0



diff-sorted() {
    diff <(sort "$1") <(sort "$2")
}


main() {
    cd "$DIR"
    mkdir -p "$OUTDIR"

    cd "$OUTDIR"
    [[ -e corpus.xml ]] || cp ../corpus.xml .

    t_testname "Corpus indexing"
    t_run "$t_BIN/index.py -v -i corpus corpus.xml"

    t_testname "Extraction from index"
    t_run "$t_BIN/candidates.py -f -v -p $DIR/patterns.xml corpus.info >candidates-from-index.xml"

    t_testname "Extraction from XML"
    t_run "$t_BIN/candidates.py -f -v -p $DIR/patterns.xml corpus.xml >candidates-from-corpus.xml"

    t_testname "Comparison of candidate extraction outputs"
    t_run "diff-sorted candidates-from-index.xml candidates-from-corpus.xml"

    t_testname "Individual word frequency counting"
    t_run "$t_BIN/counter.py -v -J -i corpus.info candidates-from-index.xml >candidates-counted.xml"

    t_testname "Association measures"
    t_run "$t_BIN/feat_association.py -v -m mle:pmi:t:dice:ll candidates-counted.xml >candidates-featureful.xml"

    t_testname "Evaluation"
    t_run "$t_BIN/eval_automatic.py -v -r $DIR/reference.xml -g candidates-featureful.xml >eval.xml 2>eval-stats.txt"

    t_testname "Mean Average Precision"
    t_run "$t_BIN/map.py -v -f mle_corpus:pmi_corpus:t_corpus:dice_corpus:ll_corpus eval.xml >map.txt"

    for format in csv arff evita owl ucs; do
        t_testname "Conversion from XML to $format"
        t_run "$t_BIN/xml2$format.py -v candidates-featureful.xml >candidates-featureful.$format 2>warnings-$format.txt"
    done

    t_testname "Take first 50 candidates"
    t_run "$t_BIN/head.py -v -n 50 candidates-featureful.xml >candidates-featureful-head.xml"

    t_testname "Take last 50 candidates"
    t_run "$t_BIN/tail.py -v -n 50 candidates-featureful.xml >candidates-featureful-tail.xml"

    t_testname "Take first 50 corpus sentences"
    t_run "$t_BIN/head.py -v -n 50 corpus.xml >corpus-head.xml"

    t_testname "Take last 50 corpus sentences"
    t_run "$t_BIN/tail.py -v -n 50 corpus.xml >corpus-tail.xml"

    for base in candidates-featureful corpus; do
        for suffix in '' -head -tail; do
            t_testname "Word count for $base$suffix"
            t_run "$t_BIN/wc.py $base$suffix.xml 2>&1 | tee wc-$base$suffix.txt"
        done
    done

    t_testname "Removal of duplicated candidates"
    t_run "$t_BIN/uniq.py candidates-featureful.xml >candidates-uniq.xml"

    t_testname "Removal of duplicated candidates ignoring POS"
    t_run "$t_BIN/uniq.py -g candidates-featureful.xml >candidates-uniq-nopos.xml"

    t_testname "Filtering out candidates occurring less than twice"
    t_run "$t_BIN/filter.py -t 2 candidates-featureful.xml >candidates-twice.xml"

    t_testname "Comparison against reference output"
    compare-to-reference
}


compare() {
    local file="$1"; shift
    local ref="$1"; shift
    if [[ $file == *candidates* || $file == *eval* ]]; then
        cmp -s <(sort "$file") <(sort "$ref")
    elif [[ $file == *.suffix || $file == warning* || $file == *.corpus ]]; then
        echo "IGNORED"
        continue
    else
        cmp -s "$file" "$ref"
    fi          
}


compare-to-reference() {
    tar -C .. -xvf ../reference-output.tar.bz2
    countfail=0
    errorreport="`pwd`/../error-report.log"
    printf "" > $errorreport
    for file in *.*; do
        ref="../reference-output/$file"
        printf "  Comparing %s... " "$file"
        local ERROR=0
        compare "$file" "$ref" || ERROR=1
        if test "$ERROR" -eq 0; then
            echo "OK"
        else
            echo "FAILED!"
            difference=`diff <(sort "$file") <(sort "$ref")` || true
            echo -ne "\n-----------------------\nFile: ${file}\n${difference}" >> $errorreport
            countfail=$((countfail+1))
        fi
    done
    if [[ countfail -gt 0 ]]; then
        printf "\n\e[1;31mWARNING: $countfail tests FAILED!\e[0m\n"
        printf "Please consult the detailed error report in $errorreport\n"
    fi
}

main "$@"

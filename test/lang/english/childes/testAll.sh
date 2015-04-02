#! /bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/../../../testlib.sh"

usage_exit() { {
    echo "Usage: $(basename "$0") [-h] [-s]"
    echo "Test Childes."
    exit 1
} 1>&2;
}


while test $# -gt 0; do
    case "$1" in
        -s) t_N_TESTS_LIMIT="$(($2-1))"; shift ;;
        *) echo "Unknown option \"$1\"!" >&2; return 1 ;;
    esac
    shift
done

test "$#" -ne 0  && usage_exit

##################################################


main() {
    t_testname "Corpus indexing"
    t_run "$t_BIN/index.py -i $t_OUTDIR/corpus $t_LOCAL_INPUT/corpus.xml"
    for filepath in "$t_REFDIR/corpus."{lemma,surface,pos,syn}.* "$t_REFDIR/corpus.info"; do
        t_compare_with_ref "$(basename "$filepath")"
    done

    t_testname "Extraction from index"
    t_run "$t_BIN/candidates.py -f -p $t_LOCAL_INPUT/patterns.xml $t_OUTDIR/corpus.info >$t_OUTDIR/candidates-from-index.xml"
    t_compare_with_ref "candidates-from-index.xml"
    
    t_testname "Extraction from XML"
    t_run "$t_BIN/candidates.py -f -p $t_LOCAL_INPUT/patterns.xml $t_LOCAL_INPUT/corpus.xml >$t_OUTDIR/candidates-from-corpus.xml"
    t_compare_with_ref "candidates-from-corpus.xml"
    t_compare "$t_OUTDIR/candidates-from-index.xml" "$t_OUTDIR/candidates-from-corpus.xml" "Comparing from-corpus vs from-index"

    t_testname "Individual word frequency counting"
    t_run "$t_BIN/counter.py -J -i $t_OUTDIR/corpus.info $t_OUTDIR/candidates-from-index.xml >$t_OUTDIR/candidates-counted.xml"
    t_compare_with_ref "candidates-counted.xml"

    t_testname "Association measures"
    t_run "$t_BIN/feat_association.py -m mle:pmi:t:dice:ll $t_OUTDIR/candidates-counted.xml >$t_OUTDIR/candidates-featureful.xml"
    t_compare_with_ref "candidates-featureful.xml"

    t_testname "Evaluation"
    t_run "$t_BIN/eval_automatic.py -r $t_LOCAL_INPUT/reference.xml -g $t_OUTDIR/candidates-featureful.xml >$t_OUTDIR/eval.xml"
    t_compare_with_ref "eval.xml"

    t_testname "Mean Average Precision"
    t_run "$t_BIN/avg_precision.py -f mle_corpus:pmi_corpus:t_corpus:dice_corpus:ll_corpus $t_OUTDIR/eval.xml >$t_OUTDIR/avg_prec.txt"
    t_compare_with_ref "avg_prec.txt"

    #for format in csv arff evita owl ucs; do
    #    t_testname "Conversion from XML to $format"
    #    t_run "$t_BIN/xml2$format.py candidates-featureful.xml >candidates-featureful.$format 2>warnings-$format.txt"
    #done

    t_testname "Take first 50 candidates"
    t_run "$t_BIN/head.py -n 50 $t_OUTDIR/candidates-featureful.xml >$t_OUTDIR/candidates-featureful-head.xml"
    t_compare_with_ref "candidates-featureful-head.xml"

    t_testname "Take last 50 candidates"
    t_run "$t_BIN/tail.py -n 50 $t_OUTDIR/candidates-featureful.xml >$t_OUTDIR/candidates-featureful-tail.xml"
    t_compare_with_ref "candidates-featureful-tail.xml"

    t_testname "Take first 50 corpus sentences"
    t_run "$t_BIN/head.py -n 50 $t_LOCAL_INPUT/corpus.xml >$t_OUTDIR/corpus-head.xml"
    t_compare_with_ref "corpus-head.xml"

    t_testname "Take last 50 corpus sentences"
    t_run "$t_BIN/tail.py -n 50 $t_LOCAL_INPUT/corpus.xml >$t_OUTDIR/corpus-tail.xml"
    t_compare_with_ref "corpus-tail.xml"

    ln -s "$t_LOCAL_INPUT/corpus.xml" "$t_OUTDIR/corpus.xml"
    for base in candidates-featureful corpus; do
        for suffix in '' -head -tail; do
            t_testname "Word count for $base$suffix"
            t_run "$t_BIN/wc.py $t_OUTDIR/${base}${suffix}.xml >$t_OUTDIR/wc-${base}${suffix}.txt"
            t_compare_with_ref "wc-${base}${suffix}.txt"
        done
    done

    t_testname "Removal of duplicated candidates"
    t_run "$t_BIN/uniq.py $t_OUTDIR/candidates-featureful.xml >$t_OUTDIR/candidates-uniq.xml"
    t_compare_with_ref "candidates-uniq.xml"

    t_testname "Removal of duplicated candidates ignoring POS"
    t_run "$t_BIN/uniq.py -g $t_OUTDIR/candidates-featureful.xml >$t_OUTDIR/candidates-uniq-nopos.xml"
    t_compare_with_ref "candidates-uniq-nopos.xml"

    t_testname "Filtering out candidates occurring less than twice"
    t_run "$t_BIN/filter.py -t 2 $t_OUTDIR/candidates-featureful.xml >$t_OUTDIR/candidates-twice.xml"
    t_compare_with_ref "candidates-twice.xml"
}


main "$@"

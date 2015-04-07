#! /bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/../testlib.sh"

usage_exit() { {
    echo "Usage: $(basename "$0") [-h]"
    echo "Test MWE annotation."
    exit 1
} 1>&2;
}

test "$#" -ne 0  && usage_exit


########################################


# test_bidir <filetype> <input-file>
#   Converts <input-file> to XML and compare to reference.
#   Then convert it back and compare with <input-file>.
test_bidir() {
    local filetype="$1"; shift
    local input1="$t_OUTDIR/$1"; shift
    local output="$t_OUTDIR/$(basename "$input1").xml"

    t_run "$t_BIN/convert.py --from=$filetype --to=XML $input1 >$output"
    t_compare_with_ref "$(basename "$output")"

    local input2="$output"
    local output="${output}.${input1##*.}"
    t_run "$t_BIN/convert.py --from=XML --to=$filetype $input2 >$output"
    t_compare "$output" "$input1" "Comparing \"$(basename "$output")\" against original"
}

# test_outputOnly <filetype> <input-xml-file> <suffix-output>
#   Converts <input-xml-file> to <filetype> and compare against original.
test_outputOnly() {
    local filetype="$1"; shift
    local basename="$1"; shift
    local suffix_output="$1"; shift
    local input="$t_OUTDIR/$basename"
    local output="$t_OUTDIR/${basename}${suffix_output}"

    local reference="${input%.xml}"
    t_run "$t_BIN/convert.py --to=$filetype $input >$output"
    t_compare_with_ref "${basename}${suffix_output}"
}


# Create copy into $t_OUTDIR to simplify the code below
ln -s "$t_LOCAL_INPUT"/* "$t_OUTDIR"/


##################################################

t_testname "Check CONLL format"
test_bidir CONLL "corpus.conll"

t_testname "Check FactoredMoses format"
test_bidir FactoredMoses "corpus.moses"

t_testname "Check PlainCorpus format"
test_bidir PlainCorpus "corpus.PlainCorpus"

t_testname "Check pWaC format"
# TODO add a source_url directive so that the whole conversion works
t_STOP_ON_ERROR=false test_bidir pWaC "corpus.pwac"

t_testname "Check PlainCandidates format"
test_bidir PlainCandidates "candidates.PlainCandidates"

t_testname "Check TreeTagger format"
test_bidir TreeTagger "corpus.treetagger"


t_testname "Check CSV format"
test_outputOnly CSV "candidates.xml" ".csv"

t_testname "Check ARFF format"
test_outputOnly ARFF "candidates.xml" ".arff"

t_testname "Check HTML format"
test_outputOnly HTML "corpus.xml" ".html"


# (For XML, test_outputOnly will end up automatically testing
# both parser and printer, because we use XML itself as input):
t_testname "Check XML format (corpus)"
test_outputOnly  XML "corpus.xml" ".xml"
t_testname "Check XML format (candidates)"
test_outputOnly  XML "candidates.xml" ".xml"
t_testname "Check XML format (patterns)"
test_outputOnly  XML "patterns.xml" ".xml"
test_outputOnly  XML "patterns_deprecated.xml" ".xml"
test_outputOnly  XML "patterns_deprecated2.xml" ".xml"



# TODO
# Implement parser/printer: corpus.palavras
# Implement parser/printer: corpus.treetagger

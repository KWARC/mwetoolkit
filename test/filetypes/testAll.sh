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


# test_parser <filetype> <original-file> <xml-file>
#   Converts <original-file> to XML and compare to <xml-file>.
test_parser() {
    local filetype="$1"; shift
    local file_path_original="$1"; shift
    local file_path_xml_ref="$1"; shift
    local file_path_output="./output/$(basename "$file_path_original").xml"

    t_run "$t_BIN/convert.py --from=$filetype --to=XML $file_path_original >$file_path_output"
    t_compare "$file_path_output" "$file_path_xml_ref"
}

# test_printer <filetype> <original-file> <xml-file>
#   Converts <xml-file> to <filetype> and compare to <original-file>.
test_printer() {
    local filetype="$1"; shift
    local file_path_original="$1"; shift
    local file_path_xml_ref="$1"; shift
    local file_path_output="./output/$(basename "$file_path_original")"

    t_run "$t_BIN/convert.py --to=$filetype --from=XML $file_path_xml_ref >$file_path_output"
    t_compare "$file_path_output" "$file_path_original"
}


cd "$HERE"
rm -rf ./output
mkdir -p ./output

t_testname "Check XML format"
test_parser  XML "xml-ref/corpus.conll.xml" "xml-ref/corpus.conll.xml"
# (For XML, test_parser will end up automatically testing printer)

t_testname "Check CONLL format"
test_parser  CONLL "corpus.conll" "xml-ref/corpus.conll.xml"
#test_printer CONLL "corpus.conll" "xml-ref/corpus.conll.xml"

t_testname "Check FactoredMoses format"
test_parser  FactoredMoses "corpus.moses" "xml-ref/corpus.moses.xml"
test_printer FactoredMoses "corpus.moses" "xml-ref/corpus.moses.xml"

t_testname "Check PlainCorpus format"
test_parser  PlainCorpus "corpus.PlainCorpus" "xml-ref/corpus.PlainCorpus.xml"
test_printer PlainCorpus "corpus.PlainCorpus" "xml-ref/corpus.PlainCorpus.xml"

t_testname "Check pukWaC format"
test_parser  pukWaC "corpus.pukwac" "xml-ref/corpus.pukwac.xml"
#test_printer pukWaC "corpus.pukwac" "xml-ref/corpus.pukwac.xml"

t_testname "Check PlainCandidates format"
test_parser  PlainCandidates "candidates.PlainCandidates" "xml-ref/candidates.PlainCandidates.xml"
test_printer PlainCandidates "candidates.PlainCandidates" "xml-ref/candidates.PlainCandidates.xml"


# TODO
# Implement parser/printer: corpus.palavras
# Implement parser/printer: corpus.treetagger

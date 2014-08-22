#! /bin/sh
HERE="$(cd "$(dirname "$0")" && pwd)"

set -o nounset    # Using "$UNDEF" var raises error
set -o errexit    # Exit on error, do not continue quietly

usage_exit() { {
    echo "Usage: $(basename "$0") [-h]"
    echo "Test MWE annotation."
    exit 1
} 1>&2;
}

test "$#" -ne 0  && usage_exit

########################################

BIN="$HERE/../../bin"
T="${TMPDIR:-/tmp}/annotate_mwe"
FIX="xmllint --noent -"
mkdir -p "$T"


rm -rf "./output"
mkdir -p "./output"

#python "$BIN/head.py" -n10 ContiguousLemma/corpus.xml | "$BIN/annotate_mwe.py" \
#        -c ContiguousLemma/candidates.xml >output/out.xml

python "$BIN/head.py" -n10 Sources/corpus.xml | "$BIN/annotate_mwe.py" \
        -S -c Sources/candidates.xml >output/out.xml


#test_from_xml() {
#    local TARGET="$1"
#    echo "==> Checking conversion from XML: $TARGET"
#    cat "$TARGET" | $FIX  >"$T/1"
#    cat "$T/1" | "$BIN/xml2conll.py"  >"$T/2"
#    cat "$T/2" | "$BIN/conll2xml.py" | $FIX  >"$T/3"
#    diff -u "$T/1" "$T/3" | wdiff ${WDIFF_ARGS:-} -d --terminal
#}
#test_from_conll() {
#    local TARGET="$1"
#    echo "==> Checking conversion from CONLL: $TARGET"
#    cat "$TARGET"  >"$T/1"
#    cat "$T/1" | "$BIN/conll2xml.py"  >"$T/2"
#    cat "$T/2" | "$BIN/xml2conll.py"  >"$T/3"
#    diff -u "$T/1" "$T/3" | wdiff ${WDIFF_ARGS:-} -d --terminal
#}
#
#test_from_xml "./test1.xml"
#test_from_conll "./test2-simple.conll"
#test_from_conll "./test3-complex-small.conll"
##test_from_conll "./test3-complex-big.conll"

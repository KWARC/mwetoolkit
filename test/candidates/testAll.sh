#! /bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/../testlib.sh"

usage_exit() { {
    echo "Usage: $(basename "$0") [-h]"
    echo "Test MWE candidate extraction"
    exit 1
} 1>&2;
}

test "$#" -ne 0  && usage_exit

########################################


find_candidates() {
    local args="$1"
    local out_fname="$2"

    mkdir -p "$DIR_OUT/txt"
    local xml_out="$DIR_OUT/${out_fname}.xml"
    local txt_out="$DIR_OUT/txt/${out_fname}.txt"
    local txt_ref="$DIR_REF/${out_fname}.txt"

    t_run "python $t_BIN/candidates.py --debug -s -v $args \
-p $DIR_IN/patterns.xml $DIR_IN/corpus.xml >$xml_out"

    quiet=1 t_xml_to_sorted_txt "$xml_out" "$txt_out"
    t_compare "$txt_ref" "$txt_out"
}



cd "$HERE"
rm -rf ./output


for DATADIR in NounCompound VerbParticle; do
    DIR_IN="$DATADIR"
    DIR_OUT="./output/$DATADIR"
    DIR_REF="./reference-txt/$DATADIR"
    mkdir -p "$DIR_OUT"

    t_testname "Find all matches"
    find_candidates '-d All' "all-candidates"

    t_testname "Find longest matches"
    find_candidates '-d Longest' "longest-candidates"

    t_testname "Find longest matches (non-overlapping)"
    find_candidates '-N -d Longest' "longest-nonoverlap-candidates"

    t_testname "Find shortest matches"
    find_candidates '-d Shortest' "shortest-candidates"

    t_testname "Find shortest matches (non-overlapping)"
    find_candidates '-N -d Shortest' "shortest-nonoverlap-candidates"
done

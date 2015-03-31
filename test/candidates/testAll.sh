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

    mkdir -p "$t_OUTDIR/$datadir/txt"
    local txt_out="$t_OUTDIR/$datadir/${out_fname}.txt"

    t_run "$t_BIN/candidates.py -s -v $args -p $t_LOCAL_INPUT/$datadir/patterns.xml \
--to=PlainCandidates $t_LOCAL_INPUT/$datadir/corpus.xml | tail -n +2 | sort >$txt_out"
    t_compare_with_ref "$datadir/${out_fname}.txt"
}



cd "$HERE"
ln -sf "$t_INPUT/ted500.xml" "$t_LOCAL_INPUT/VerbParticle/corpus.xml"


for datadir in NounCompound VerbParticle; do
    mkdir -p "$t_OUTDIR/$datadir"

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

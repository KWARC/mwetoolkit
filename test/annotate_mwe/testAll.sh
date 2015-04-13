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


annotate() {
    local args="$1"
    local name_input="$2"
    local name_output="$3"

    local xml_out="$t_OUTDIR/${name_output}.xml"
    local txt_out="$t_OUTDIR/${name_output}.txt"
    local txt_ref="$t_REFDIR/${name_output}.txt"

    local corpus="$t_LOCAL_INPUT/${name_input}/corpus.xml"
    local candidates="$t_LOCAL_INPUT/${name_input}/candidates.xml"

    #t_run "$t_BIN/annotate_mwe.py -v $args -c $candidates $corpus >$xml_out"
    t_run "$t_BIN/annotate_mwe.py -v $args --to=TaggedPlainCorpus -c $candidates $corpus >$txt_out"
    t_compare_with_ref "${name_output}.txt"
}


t_testname "Annotate candidates with ContiguousLemma's"
annotate '' "ContiguousLemma" "ContigLemma"

t_testname "Annotate gappy candidates (up to 3 gaps)"
annotate '-g 3' "ContiguousLemma" "Gapped3ContigLemma"

t_testname "Annotate candidates from Source information"
annotate '-S' "Source" "FromSource"

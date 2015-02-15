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

    local xml_out="./output/${name_output}.xml"
    local txt_out="./output/${name_output}.txt"
    local txt_ref="./reference/${name_output}.txt"

    t_run "$t_BIN/annotate_mwe.py -v $args \
-c ${HERE}/$name_input/candidates.xml ${HERE}/$name_input/corpus.xml >$xml_out"

    t_run "$t_BIN/annotate_mwe.py -v $args --to=MosesText \
-c ${HERE}/$name_input/candidates.xml ${HERE}/$name_input/corpus.xml >$txt_out"

    t_compare "$txt_ref" "$txt_out"
}


cd "$HERE"
rm -rf ./output
mkdir -p ./output

t_testname "Annotate candidates with ContiguousLemma's"
annotate '' "ContiguousLemma" "ContigLemma"

t_testname "Annotate gappy candidates (up to 3 gaps)"
annotate '-g 3' "ContiguousLemma" "Gapped3ContigLemma"

t_testname "Annotate candidates from Source information"
annotate '-S' "Source" "FromSource"

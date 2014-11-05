#! /bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"

source ../testlib.sh

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

    t_run "$t_BIN/annotate_mwe.py --debug $args \
-c $name_input/candidates.xml $name_input/corpus.xml >$xml_out"

    t_run "$t_BIN/annotate_mwe.py --debug $args -o Text \
-c $name_input/candidates.xml $name_input/corpus.xml >$txt_out"

    t_compare "$txt_ref" "$txt_out"
}



rm -rf ./output
mkdir -p ./output

t_testname "Annotate candidates with ContiguousLemma's"
annotate '' "ContiguousLemma" "ContigLemma"

t_testname "Annotate candidates with up to 3 gaps"
annotate '-g 3' "ContiguousLemma" "Gapped3ContigLemma"

t_testname "Annotate candidates from Source information"
annotate '-S' "Source" "FromSource"

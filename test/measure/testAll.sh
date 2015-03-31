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


cd "$HERE"

t_testname "Measure using ExactMatch"
t_run "$t_BIN/measure.py -e ExactMatch -r $t_LOCAL_INPUT/reference.xml $t_LOCAL_INPUT/prediction.xml >$t_OUTDIR/ExactMatch.txt"
t_compare_with_ref "ExactMatch.txt"

t_testname "Measure using LinkBased"
t_run "$t_BIN/measure.py -e LinkBased -r $t_LOCAL_INPUT/reference.xml $t_LOCAL_INPUT/prediction.xml >$t_OUTDIR/LinkBased.txt"
t_compare_with_ref "LinkBased.txt"

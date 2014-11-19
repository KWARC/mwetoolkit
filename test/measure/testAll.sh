#! /bin/bash
here="$(cd "$(dirname "$0")" && pwd)"

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

t_testname "Diff reference vs prediction"
t_run "colordiff reference.xml prediction.xml" || true

t_testname "Measure using ExactMatch"
t_run "$t_BIN/measure.py -e ExactMatch -r reference.xml prediction.xml"

t_testname "Measure using LinkBased"
t_run "$t_BIN/measure.py -e LinkBased -r reference.xml prediction.xml"

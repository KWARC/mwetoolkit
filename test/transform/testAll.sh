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


"$t_BIN/head.py" "$t_INPUT/ted500.xml">"$t_OUTDIR/smallTed.xml"

t_testname "Bracketing word surfaces"
t_run "$t_BIN/transform.py --to=PlainCorpus --each-word 'word.surface = \"[\"+word.surface+\"]\"' $t_OUTDIR/smallTed.xml >$t_OUTDIR/Bracket.PlainCorpus"
t_compare_with_ref "Bracket.PlainCorpus"

t_testname "Replacing surface by surface/POS-tag"
t_run "$t_BIN/transform.py --to=PlainCorpus --begin 'print(\"BEGIN-STRING\")' --end 'print(\"END-STRING\")'  --each-word 'word.surface = word.surface+\"/\"+word.pos' $t_OUTDIR/smallTed.xml >$t_OUTDIR/SurfaceSlashPOS.PlainCorpus"
t_compare_with_ref "SurfaceSlashPOS.PlainCorpus"

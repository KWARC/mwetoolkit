#!/bin/bash

# Simplified version of testAll.sh script present in test/genia

dotest(){
    name=$1; run=$2
    echo -e "\n\n$name"
    printf "\e[1;33mpython $TOOLKITDIR/bin/%s\e[0m\n" "$run"
    eval python $TOOLKITDIR/bin/$run
}

# Automatically configure paths

# Use GNU readlink on Mac OS.
if which greadlink >/dev/null 2>&1; then
	readlink() { greadlink "$@"; }
fi

DIR="$(readlink -f "$(dirname "$0")")"
TOOLKITDIR="$DIR/../.."
OUTDIR="$DIR/output"

cd "$DIR"

# Create output folder if not exists
[[ -d $OUTDIR ]] || mkdir "$OUTDIR"
cd "$OUTDIR"
# If there's no link to DTD folder, create one
[[ -e dtd ]] || ln -s "$TOOLKITDIR/dtd" .
[[ -e index ]] || mkdir index
[[ -e corpus.xml ]] || cp $DIR/*.xml .

dotest "Corpus indexing" \
"index.py -v -i index/corpus corpus.xml"

dotest "Candidate extraction from index" \
"candidates.py -p patterns.xml -i index/corpus > candidates.xml"

dotest "Individual and joint word frequency counting" \
"counter.py -i index/corpus candidates.xml > candidates-counted.xml"

dotest "Association measures" \
"feat_association.py -m mle:pmi:t:dice:ll candidates-counted.xml > candidates-featureful.xml"

dotest "Sort the resulting list" \
"sort.py -f t_corpus candidates-featureful.xml > candidates-sorted.xml"

dotest "Keeping only the 100 MWEs with maximal t score value" \
"head.py -n 100 candidates-sorted.xml > candidates-crop.xml"

dotest "Evaluation: compare with gold standard" \
"eval_automatic.py -r reference.xml -g candidates-crop.xml > eval.xml 2> eval-stats.txt"

echo "Results available in files $OUTDIR/eval.xml and $OUTDIR/eval-stats.txt"


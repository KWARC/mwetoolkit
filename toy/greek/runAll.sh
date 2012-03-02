#!/bin/sh

# This file runs the whole pipeline of MWE extraction with mwetoolkit on a small
# example corpus of Greek sentences.

path_mwttoolkit="../../bin"
python="/usr/bin/python"

# INITIAL FILES

# The corpus is a small subset of 325 sentences taken from the Europarl Greek 
# corpus
corpus_name="gr_toy"

the_corpus="${corpus_name}.xml"

# gr_patterns.xml is a set of POS patterns defined by Evita Linardaki, cf. LREC
# 2010 workshop on south-eastern european languages.
the_patterns="gr_patterns.xml"

echo "0) Corpus statistics"
#${python} ${path_mwttoolkit}/wc.py ${the_corpus}

${python} ${path_mwttoolkit}/tail.py -n 2000 ${the_corpus}

echo "1) Generate the initial list of candidates using the POS patterns"

#${python} ${path_mwttoolkit}/candidates.py -p ${the_patterns} ${the_corpus} > candidates.xml
#${python} ${path_mwttoolkit}/wc.py candidates.xml

#echo "2) Filter out candidates occurring less than threshold (2)"

#${python} ${path_mwttoolkit}/filter.py -t ${the_corpus}:2 candidates.xml > candidates-filter.xml
#${python} ${path_mwttoolkit}/wc.py candidates-filter.xml

#echo "2) Generate the index files"

#${python} ${path_mwttoolkit}/index.py -i corpus.index ${the_corpus}

#echo "4) Count individual word frequencies"

#${python} ${path_mwttoolkit}/counter.py -i corpus.index candidates-filter.xml > candidates-filter-fCorpus.xml

#echo "5) Count words in Yahoo"

#${python} ${path_mwttoolkit}/counter.py -y candidates-filter-fCorpus.xml > candidates-filter-fCorpus-fYahoo.xml

#echo "6) Extract descriptive features"

#${python} ${path_mwttoolkit}/feat_pattern.py candidates-filter-fCorpus.xml > feat-pos.xml

#echo "7) Extract Association Measure features"

#${python} ${path_mwttoolkit}/feat_association.py feat-pos.xml > feat-pos-am.xml

#echo "8) Sort the candidates according to Dice, and crop top-30 candidates"

#${python} ${path_mwttoolkit}/sort.py -f dice_gr_toy feat-pos-am.xml > tmp
#${python} ${path_mwttoolkit}/filter.py -c 30 tmp > feat-pos-am-dice.xml
#rm tmp


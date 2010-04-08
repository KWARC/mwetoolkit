#!/bin/sh

# This file runs the whole pipeline of MWT extraction with mwttoolkit. The
# result is a file called candidates.arff that can be treated by the WEKA
# machine learning package. Some examples of models are in the "models" folder.

path_mwttoolkit="../../bin"
python="/usr/bin/python"

# INITIAL FILES

# corpus.xml is a small subset of the Genia corpus containing 34 sentences 
# chosen randomly among the ~18K sentences of the corpus.

corpus_name="gr_toy"

the_corpus="${corpus_name}.xml"

# patterns.xml is a set of POS patterns generated empirically to extract 
# biomedical MWTs

the_patterns="gr_patterns.xml"

# A subset of the Genia reference list, which was created by looking at all
# manually annotated MWTs in the corpus. The reference is the Gold Standard
# against which we compare our results.

the_reference="reference.xml"

echo "1) Generate the initial list of candidates using the POS patterns"

${python} ${path_mwttoolkit}/candidates.py -p ${the_patterns} ${the_corpus} > candidates.xml

echo "2) Generate the index file"

${python} ${path_mwttoolkit}/index.py -i corpus.index ${the_corpus}

echo "3) Filter out candidates occurring less than threshold (2)"

${python} ${path_mwttoolkit}/filter.py -t ${the_corpus}:2 candidates.xml > candidates-filter.xml

echo "4) Count individual word frequencies"

${python} ${path_mwttoolkit}/counter.py -i corpus.index candidates-filter.xml > candidates-filter-fCorpus.xml

#echo "5) Count words in Yahoo"

#${python} ${path_mwttoolkit}/counter.py -y candidates-filter-fCorpus.xml > candidates-filter-fCorpus-fYahoo.xml

echo "6) Extract descriptive features"

${python} ${path_mwttoolkit}/feat_pattern.py candidates-filter-fCorpus.xml > feat-pos.xml

echo "7) Extract Association Measure features"

${python} ${path_mwttoolkit}/feat_association.py feat-pos.xml > feat-pos-am.xml

echo "8) Sort the candidates according to Dice, and crop top-30 candidates"

${python} ${path_mwttoolkit}/sort.py -f dice_gr_toy feat-pos-am.xml > tmp
${python} ${path_mwttoolkit}/filter.py -c 30 tmp > feat-pos-am-dice.xml
rm tmp

#echo "8) Automatic evaluation"

#${python} ${path_mwttoolkit}/eval_automatic.py -r ${the_reference} feat-pos-am.xml > feat-pos-am-class.xml

#echo "9) Convert to WEKA format"

#${python} ${path_mwttoolkit}/xml2arff.py feat-pos-am-class.xml > feat-pos-am-class.arff


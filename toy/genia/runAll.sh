#!/bin/bash

# This file runs the whole pipeline of MWE extraction with mwetoolkit. The
# result is a file called candidates.arff that can be treated by the WEKA
# machine learning package. Some examples of models are in the "models" folder.
# All the results are compared to standard results in the test folder, to verify
# consistency.

path_mwttoolkit="../../bin"
python="/usr/bin/python"

# INITIAL FILES

# corpus.xml is a small subset of the Genia corpus containing 500 sentences 
# chosen randomly among the ~18K sentences of the corpus.

corpus_name="corpus"

the_corpus="${corpus_name}.xml"

# patterns.xml is a set of POS patterns generated empirically to extract 
# biomedical MWTs

the_patterns="patterns.xml"

# A subset of the Genia reference list, which was created by looking at all
# manually annotated MWEs in the corpus. The reference is the Gold Standard
# against which we compare our results.

the_reference="reference.xml"

echo "0) Statistics"
echo "----Corpus----"
${python} ${path_mwttoolkit}/wc.py -v ${the_corpus}
echo "----Patterns----"
${python} ${path_mwttoolkit}/wc.py -v ${the_patterns}
echo "----Reference----"
${python} ${path_mwttoolkit}/wc.py -v ${the_reference}

echo "1) Generate the initial list of candidates using the POS patterns"

${python} ${path_mwttoolkit}/candidates.py -s -v -n 2:3 ${the_corpus} > candidates.xml
echo "----Initial candidates----"
${python} ${path_mwttoolkit}/wc.py candidates.xml



echo "2) Filter out candidates occurring less than threshold (2)"

${python} ${path_mwttoolkit}/filter.py -v -t ${corpus_name}:2 candidates.xml > candidates-filter.xml
echo "----Filtered candidates----"
${python} ${path_mwttoolkit}/wc.py candidates-filter.xml


echo "3) Generate the index file"

${python} ${path_mwttoolkit}/index.py -s -i corpus.index ${the_corpus}



echo "4) Count individual word frequencies"

${python} ${path_mwttoolkit}/counter.py -i corpus.index candidates-filter.xml > candidates-filter-fCorpus.xml

echo "5) Count words in Yahoo"

${python} ${path_mwttoolkit}/counter.py -y candidates-filter-fCorpus.xml > candidates-filter-fCorpus-fYahoo.xml

echo "6) Extract descriptive features"

${python} ${path_mwttoolkit}/feat_pattern.py candidates-filter-fCorpus-fYahoo.xml > feat-pos.xml

echo "7) Extract Association Measure features"

${python} ${path_mwttoolkit}/feat_association.py feat-pos.xml > feat-pos-am.xml

echo "8) Automatic evaluation"

${python} ${path_mwttoolkit}/eval_automatic.py -r ${the_reference} feat-pos-am.xml > feat-pos-am-class.xml

echo "9) Convert to WEKA format"

${python} ${path_mwttoolkit}/xml2arff.py feat-pos-am-class.xml > feat-pos-am-class.arff

fi


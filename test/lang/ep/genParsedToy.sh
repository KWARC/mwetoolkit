#!/usr/bin/bash
# Parses the toy Europarl corpus
# REQUIRES the Stanford Parser to be installed somewhere. The parser is freely
# available, just google it, unzip it and correct the hardcoded path below

mwe_scripts="../../bin"
stan_parser="/home/ceramisch/Work/tools/stanford-parser-2011-04-20"

python ${mwe_scripts}/xml2csv.py -s ep-demo-mwe2011.xml | awk 'BEGIN{FS="\t"}{print $2 " </s>"}' | sed 's/&quot;/"/g' > ep-demo-mwe2011.txt
python ${mwe_scripts}/xml2csv.py ep-demo-mwe2011.xml | awk 'BEGIN{FS="\t"}{print $2 " </s>"}' > ep-demo-mwe2011-lemmas.txt
java -mx550m -cp "${stan_parser}/stanford-parser.jar:" edu.stanford.nlp.parser.lexparser.LexicalizedParser -tokenized -sentences '</s>' -outputFormat "wordsAndTags,penn,typedDependencies" ${stan_parser}/englishPCFG.ser.gz ep-demo-mwe2011.txt > ep-demo-mwe2011-parsed.txt
python join_data.py ep-demo-mwe2011-parsed.txt ep-demo-mwe2011-lemmas.txt > ep-demo-mwe2011-parsed-join.xml


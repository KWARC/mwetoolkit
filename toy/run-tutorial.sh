#!/bin/bash
# This script contains all the commands used in the tutorial. You can run the
# script as it is, or copy-paste the commands you're interested in. Each command
# is explained and you can try and adapt the options to your corpus, MWE 
# patterns, and so on.

MWETK=".."
MWETKBIN="${MWETK}/bin"

echo -e "\nStep 1 - Installing the mwetoolkit"

# The mwetoolkit is composed of python scripts, so you do not need to do 
# anything to compile it. As long as you have a python 2.6+ interpreter, it's
# fine. However, part of it is written in C for increased speed, so we recommend
# that you compile the C indexer before getting started. Therefore, simply run
# "make" in the root mwetoolkit folder.

make -C ${MWETK}

# For the next steps, remember that you can always run a script passing option
# -h, to obtain a detailed list of its functionalities, arguments and options.
# For example :
${MWETKBIN}/index.py -h

echo -e "\nStep 2 - Indexing the corpus"

# In this tutorial, we use the TED English corpus, an excerpt from the bilingual
# English-French TED talks from https://wit3.fbk.eu/mt.php?release=2014-01
# The corpus was parsed using RASP and then converted to CONLL format. This 
# format contains one word per line, and one word information per column. Take
# a look at the file to see what it contains.
zcat ted-en-sample.conll.gz | head

# You can uncompress the file so that it is easier to inspect it using command 
# line tools or a text editor like nano, vim, gedit or emacs
gunzip -c ted-en-sample.conll.gz > ted-en-sample.conll

# Let us now generate an index for fast corpus access. This is not required for
# most scripts, but since we want to count n-grams, we will need it (counter.py)
# Since our corpus contains around half a million words, this will take some 
# time (30 secs to a couple of minutes, depending on your computer)
#mkdir -p index TODO: UNCOMMENT
#rm -rf index/*  TODO: UNCOMMENT
#${MWETKBIN}/index.py -v -i index/ted ted-en-sample.conll  TODO: UNCOMMENT

# If you look at the index folder, you will notice the creation of many files
# prefixed by "ted". This is because you specified that the index should be
# created with prefix index/ted using -i option. We recommend always creating
# a folder and storing all index files in this folder.
ls index

echo -e "\nStep 3 - Candidate extraction\n"
# Once you have indexed the corpus, you are ready for candidate extraction. You 
# must first define the pattern you are interested in. For instance, we use the
# file pat_nn.xml which describes sequences of nouns and prepositional phrases
# that start with a noun. This corresponds roughly to noun phrases in English. 
# You can look at the example pattern to get familiarised with the XML format 
# used to describe it. The online documentation on the XML format and on 
# defining patterns should also help.
cat pat_nn.xml

# Then, you can run the candidates.py script to extract from the indexed corpus.
# the candidates that match the pattern. It takes as argument the pattern file 
# (-p), the corpus file format (--from) and the corpus file, which in our case 
# is the .info file corresponding to a BinaryIndex. Option -S will keep 
# information about the source sentences in which the candidates were found
#${MWETKBIN}/candidates.py -p pat_nn.xml -S -v --from=BinaryIndex index/ted.info > cand.xml TODO: UNCOMMENT

# The resulting file is in XML format, each lemmatised candidate containing some 
# information about its occurrences and source sentences.
head cand.xml

# You can count how many candidates were extracted using the wc.py script
# ${MWETKBIN}/wc.py cand.xml TODO: UNCOMMENT

# We can now count the number of occurrences of each candidate, and also of each
# word contained in a candidate. Therefore, we run the counter.py script which
# internally uses the index to obtain n-gram counts very fast.
${MWETKBIN}/counter.py -v -i index/ted.info cand.xml > cand-count.xml

# We can now remove the corpus and keep only the gzipped version, if we want
rm ted-en-sample.conll


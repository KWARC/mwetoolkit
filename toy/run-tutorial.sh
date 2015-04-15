#!/bin/bash
# This script contains all the commands used in the tutorial. You can run the
# script as it is, or copy-paste the commands you're interested in. Each command
# is explained and you can try and adapt the options to your corpus, MWE 
# patterns, and so on.

MWETK=".."
MWETKBIN="${MWETK}/bin"

echo -e "\nChapter 1 - Installing the mwetoolkit"

# The mwetoolkit is composed of python scripts, so you do not need to do 
# anything to compile it. As long as you have a python 2.6+ interpreter, it's
# fine. However, part of it is written in C for increased speed, so we recommend
# that you compile the C indexer before getting started. Therefore, simply run
# "make" in the root mwetoolkit folder.

make -C ${MWETK}

echo -e "\nChapter 2 - Indexing the corpus"

# In this tutorial, we use the TED English corpus, an excerpt from the bilingual
# English-French TED talks from https://wit3.fbk.eu/mt.php?release=2014-01
# The corpus was parsed using RASP and then converted to CONLL format. This 
# format contains one word per line, and one word information per column. Take
# a look at the file to see what it contains.
zcat ted-en-sample.conll.gz | head
# You can uncompress the file so that it is easier to inspect it using command 
# line tools or a text editor like nano, vim, gedit or emacs
gunzip -c ted-en-sample.conll.gz > ted-en-sample.conll

# We can now remove the corpus and keep only the gzipped version, if we want
rm ted-en-sample.conll


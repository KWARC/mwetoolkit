#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# localmaxs_shelve.py is part of mwetoolkit
#
# mwetoolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mwetoolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mwetoolkit.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
    This script extract Multiword Expression candidates from a raw corpus in 
    valid XML (mwetoolkit-corpus.dtd) and generates a candidate list in valid 
    XML (mwetoolkit-candidates.dtd), using the LocalMaxs algorithm
    (http://www.di.ubi.pt/~ddg/publications/epia1999.pdf).

    This version supports the --shelve option to use disk storage instead of
    an in-memory data structure to keep the candidates, thus allowing
    extraction from corpora too large for the data to fit in memory.

    For more information, call the script with no parameter and read the
    usage instructions.
"""


import sys
import os
import xml.sax
import shelve
import tempfile

from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.__common import WILDCARD, \
                                        TEMP_PREFIX, \
                                        TEMP_FOLDER, \
                                        XML_HEADER, \
                                        XML_FOOTER, \
                                        WORD_SEPARATOR

from xmlhandler.classes.feature import Feature
from xmlhandler.classes.meta import Meta
from xmlhandler.classes.meta_feat import MetaFeat
from xmlhandler.classes.corpus_size import CorpusSize
from xmlhandler.classes.frequency import Frequency
from xmlhandler.classes.candidate import Candidate
from xmlhandler.classes.ngram import Ngram
from xmlhandler.classes.word import Word
from xmlhandler.classes.entry import Entry
from util import usage, read_options, treat_options_simplest, \
                 verbose, interpret_ngram

from libs.indexlib import Index

usage_string = """Usage:

python %(program)s OPTIONS <corpus>

OPTIONS may be:

-n <min>:<max> OR --ngram <min>:<max>
    The length of ngrams to extract. For instance, "-n 3:5" extracts ngrams 
    that have at least 3 words and at most 5 words. If you define only <min> or
    only <max>, the default is to consider that both have the same value, i.e. 
    if you call the program with the option "-n 3", you will extract only 
    trigrams while if you call it with the options "-n 3:5" you will extract 
    3-grams, 4-grams and 5-grams. Default "2:8".

-i OR --index
     Read the corpus from an index instead of an XML file. Default false.

-s OR --surface
    Counts surface forms instead of lemmas. Default false.

-G <glue> OR --glue <glue>
    Use <glue> as the glue measure. Currently only 'scp' is supported.

-f <freq> OR --freq <freq>
    Output only candidates with a frequency of at least <freq>. Default 2.

-h OR --shelve
    Use a shelve (disk storage) rather than an in-memory data structure for
    storing candidate counts. Uses less memory, but is slower.

%(common_options)s

    By default, <corpus> must be a valid XML file (mwetoolkit-corpus.dtd). If
the -i option is specified, <corpus> must be the basepath for an index generated
by index.py.
"""


ngram_counts = {}
selected_candidates = {}
corpus_size = 0
sentence_count = 0

################################################################################

def key(ngram):
    """
        Returns a string key for the given list of words (strings).
        (Shelves can only be indexed by strings and integers.)
    """
    return WORD_SEPARATOR.join(ngram)

################################################################################

def unkey(str):
    """
        Returns a list of words for the given key.
    """
    return str.split(WORD_SEPARATOR)

################################################################################

def treat_sentence(sentence):
    """
        Count all ngrams being considered in the sentence.
    """
    global corpus_size, sentence_count

    # 'shelve' does not speak Unicode; we must convert Unicode strings back to
    # plain bytestrings to use them as keys.
    words = [getattr(w, base_attr).encode('utf-8') for w in sentence.word_list]

    sentence_count += 1
    if sentence_count % 100 == 0:
        verbose("Processing sentence %d" % sentence_count)

    for ngram_size in range(1, max_ngram + 2):
        for i in range(len(words) - ngram_size + 1):
            ngram = words[i : i+ngram_size]
            ngram_key = key(ngram)
            count = ngram_counts.get(ngram_key, 0)
            ngram_counts[ngram_key] = count + 1
            selected_candidates[ngram_key] = True

    corpus_size += len(words)
    
################################################################################

def localmaxs():
    """
        The LocalMaxs algorithm. Check whether each of the extracted ngrams
        is a local maximum in terms of glue value.
    """
    for ngram_key in ngram_counts:
        ngram = unkey(ngram_key)
        if len(ngram) >= min_ngram and len(ngram) <= max_ngram + 1:
            left = ngram[:-1]
            right = ngram[1:]
            this_glue = glue(ngram)

            for subgram in [left, right]:
                subglue = glue(subgram)
                subkey = key(subgram)
                if this_glue < subglue:
                    selected_candidates[ngram_key] = False
                elif subglue < this_glue:
                    selected_candidates[subkey] = False
        else:
            selected_candidates[ngram_key] = False
            
################################################################################

def main():
    """
        Main function.
    """
    global corpus_size_f
    global use_shelve, ngram_counts, selected_candidates

    if use_shelve:
        verbose("Making temporary file...")
        (ngram_counts, ngram_counts_tmpfile) = make_shelve()
        (selected_candidates, selected_candidates_tmpfile) = make_shelve()

    verbose("Counting ngrams...")
    if corpus_from_index:
        index = Index(corpus_path)
        index.load_main()
        for sentence in index.iterate_sentences():
            treat_sentence(sentence)
    else:
        input_file = open(corpus_path)    
        parser = xml.sax.make_parser()
        parser.setContentHandler( CorpusXMLHandler( treat_sentence ) ) 
        parser.parse( input_file )
        input_file.close()

    corpus_size_f = float(corpus_size)

    verbose("Selecting ngrams through LocalMaxs...")
    localmaxs()

    verbose("Outputting candidates file...")
    print XML_HEADER % { "root": "candidates", "ns": "" }
    

    meta = Meta([CorpusSize("corpus", corpus_size)],
                [MetaFeat("glue", "real")], [])
    print meta.to_xml().encode('utf-8')

    id = 0

    for ngram_key in selected_candidates:
        if selected_candidates[ngram_key] and ngram_counts[ngram_key] >= min_frequency:
            dump_ngram(ngram_key, id)
            id += 1

    print XML_FOOTER % { "root": "candidates" }

    if use_shelve:
        verbose("Removing temporary files...")
        destroy_shelve(ngram_counts, ngram_counts_tmpfile)
        destroy_shelve(selected_candidates, selected_candidates_tmpfile)
        
################################################################################

def dump_ngram(ngram_key, id):
    """
        Print an ngram as XML.
    """
    ngram = unkey(ngram_key)
    cand = Candidate(id, [], [], [], [], [])
    for value in ngram:
        word = Word(WILDCARD, WILDCARD, WILDCARD, WILDCARD, [])
        setattr(word, base_attr, value.decode('utf-8'))
        cand.append(word)
    freq = Frequency('corpus', ngram_counts[ngram_key])
    cand.add_frequency(freq)
    cand.add_feat(Feature('glue', glue(ngram)))

    print cand.to_xml().encode('utf-8')

################################################################################

def prob(ngram):
    """
        Returns the frequency of the ngram in the corpus.
    """
    return ngram_counts[key(ngram)] / corpus_size_f

################################################################################

def scp_glue(ngram):
    """
        Computes the Symmetrical Conditional Probability of the ngram.
    """
    square_prob = prob(ngram) ** 2
    if len(ngram) == 1:
        return square_prob

    avp = 0
    for i in range(1, len(ngram)):
        avp += prob(ngram[:i]) * prob(ngram[i:])
    avp = avp / (len(ngram) - 1)

    if avp == 0:
        return 0
    else:
        return square_prob / avp

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global surface_instead_lemmas
    global glue
    global corpus_from_index
    global base_attr
    global min_ngram
    global max_ngram
    global min_frequency
    global ngram_counts
    global selected_candidates
    global use_shelve

    treat_options_simplest( opts, arg, n_arg, usage_string )

    mode = []
    for ( o, a ) in opts:
        if o in ("-s", "--surface") : 
            surface_instead_lemmas = True
            base_attr = 'surface'
        elif o in ("-f", "--freq") :
            min_frequency = int(a)
        elif o in ("-n", "--ngram") :
            (min_ngram, max_ngram) = interpret_ngram(a)
        elif o in ("-i", "--index") :
            corpus_from_index = True
        elif o in ("-G", "--glue"):
            if a == "scp":
                glue = scp_glue
            else:
                print >>sys.stderr, "Unknown glue function '%s'" % a
                sys.exit(1)
        elif o in ("-h", "--shelve"):
            use_shelve = True

################################################################################

def make_shelve():
    """
        Makes a temporary shelve. Returns the shelve and its pathname.
    """
    path = tempfile.mktemp()
    shlv = shelve.open(path, 'n', writeback=True)
    return (shlv, path)

################################################################################

def destroy_shelve(shlv, path):
    """
        Destoys a shelve and removes its file.
    """
    shlv.clear()
    shlv.close()
    try:
        os.remove(path)
    except OSError:
        os.remove(path + ".db")
    except Exception, err:
        print >>sys.stderr, "Error removing temporary file:", err

################################################################################

corpus_from_index = False
base_attr = 'lemma'
glue = scp_glue
min_ngram = 2
max_ngram = 8
min_frequency = 2
use_shelve = False

longopts = ["surface", "glue=", "ngram=", "freq=", "index", "shelve"]
arg = read_options("sG:n:f:ih", longopts, treat_options, 1, usage_string)
corpus_path = arg[0]

main()

#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# localmaxs.py is part of mwetoolkit
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

    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import xml.sax

from libs.corpusXMLHandler import CorpusXMLHandler
from libs.base.__common import WILDCARD, XML_HEADER, XML_FOOTER
from libs.base.feature import Feature
from libs.base.meta import Meta
from libs.base.meta_feat import MetaFeat
from libs.base.corpus_size import CorpusSize
from libs.base.frequency import Frequency
from libs.base.candidate import Candidate
from libs.base.word import Word
from libs.util import read_options, treat_options_simplest, verbose,\
    interpret_ngram, error
from libs.indexlib import Index

################################################################################

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

%(common_options)s

    By default, <corpus> must be a valid XML file (mwetoolkit-corpus.dtd). If
the -i option is specified, <corpus> must be the basepath for an index generated
by index.py.
"""

ngram_counts = {}
select = {}
candidates = set()
corpus_size = 0

################################################################################

def treat_sentence(sentence):
    """
        Count all ngrams being considered in the sentence.
    """
    global corpus_size

    words = tuple([getattr(w, base_attr) for w in sentence])

    for ngram_size in range(1, max_ngram + 2):
        for i in range(len(words) - ngram_size + 1):
            ngram = words[i : i+ngram_size]
            count = ngram_counts.get(ngram, 0)
            ngram_counts[ngram] = count + 1
            select[ngram] = True

    corpus_size += len(words)

################################################################################

def localmaxs():
    """
        The LocalMaxs algorithm. Check whether each of the extracted ngrams
        is a local maximum in terms of glue value.
    """
    for ngram in ngram_counts:
        if len(ngram) >= min_ngram and len(ngram) <= max_ngram + 1:
            left = ngram[:-1]
            right = ngram[1:]
            this_glue = glue(ngram)

            for subgram in [left, right]:
                subglue = glue(subgram)
                if this_glue < subglue:
                    select[ngram] = False
                elif subglue < this_glue:
                    select[subgram] = False
                    
################################################################################

def main():
    """
        Main function.
    """
    global corpus_size_f

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

    localmaxs()


    verbose("Outputting candidates file...")
    print(XML_HEADER % { "category": "candidates", "ns": "" })
    

    meta = Meta([CorpusSize("corpus", corpus_size)],
                [MetaFeat("glue", "real")], [])
    print(meta.to_xml().encode('utf-8'))

    id = 0

    for ngram in select:
        if (len(ngram) >= min_ngram and len(ngram) <= max_ngram and
            select[ngram] and ngram_counts[ngram] >= min_frequency):
                dump_ngram(ngram, id)
                id += 1

    print(XML_FOOTER % { "category": "candidates" })

################################################################################

def dump_ngram(ngram, id):
    """
        Print an ngram as XML.
    """
    cand = Candidate(id, [], [], [], [], [])
    for value in ngram:
        word = Word(WILDCARD, WILDCARD, WILDCARD, WILDCARD, [])
        setattr(word, base_attr, value)
        cand.append(word)
    freq = Frequency('corpus', ngram_counts[ngram])
    cand.add_frequency(freq)
    cand.add_feat(Feature('glue', glue(ngram)))

    print(cand.to_xml().encode('utf-8'))

################################################################################

def prob(ngram):
    """
        Returns the frequency of the ngram in the corpus.
    """
    return ngram_counts[ngram] / corpus_size_f

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
                error("Unknown glue function '%s'" % a)

################################################################################

corpus_from_index = False
base_attr = 'lemma'
glue = scp_glue
min_ngram = 2
max_ngram = 8
min_frequency = 2

longopts = ["surface", "glue=", "ngram=", "freq=", "index"]
arg = read_options("sG:n:f:i", longopts, treat_options, 1, usage_string)
corpus_path = arg[0]

main()

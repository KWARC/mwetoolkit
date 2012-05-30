#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# xmlcorpus2txt.py is part of mwetoolkit
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
    This script converts an XML corpus into plain-text, one word per line,
    with a blank line ending each sentence.  Only the word attributes specified
    by the -a option are output.
    
    All specified attributes of a word are output in the same line, separated by
    the ATTRIBUTE_SEPARATOR character. The produced output is suitable as input
    for the C indexer.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.sentence import Sentence
from xmlhandler.classes.word import Word, WORD_ATTRIBUTES
from xmlhandler.classes.__common import ATTRIBUTE_SEPARATOR
from util import usage, read_options, treat_options_simplest, verbose

usage_string = """Usage:

python %(program)s -a <attributes> <corpus.xml>

-a <attributes> OR --attributes <attributes>
   A colon-separated list of attributes to output. The possibles attributes are
   surface:lemma:pos	 

%(common_options)s

<corpus.xml> must be a valid XML file (mwetoolkit-corpus.dtd).
"""

attributes = None

################################################################################

def xml2txt(corpus, outfile, attributes):

    def print_sentence(sentence):
        for word in sentence.word_list:
            vals = [getattr(word, attr) for attr in attributes]
            print >>outfile, ATTRIBUTE_SEPARATOR.join(vals),
        print >> outfile, ""

    parser = xml.sax.make_parser()
    parser.setContentHandler(CorpusXMLHandler(print_sentence))
    parser.parse(corpus)

################################################################################

def treat_options(opts, arg, n_arg, usage_string):
    """
    """
    global attributes

    treat_options_simplest( opts, arg, n_arg, usage_string )
    
    for (o, a) in opts:
        if o in ("-a", "--attributes"):
            attributes = a.split(":")
            for attr in attributes:
                if attr not in WORD_ATTRIBUTES:
                    print >>sys.stderr, "Unknown attribute '%s'!" % attr
                    sys.exit(2)

    if attributes is None:
        print >>sys.stderr, "The option -a <attributes> is mandatory."
        usage(usage_string)
        sys.exit(2)

################################################################################

longopts = ["atttibutes="]
arg = read_options("a:", longopts, treat_options, 1, usage_string)

xml2txt(arg[0], sys.stdout, attributes)

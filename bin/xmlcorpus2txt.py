#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
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

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys

from libs.base.__common import ATTRIBUTE_SEPARATOR
from libs.base.word import WORD_ATTRIBUTES
from libs.util import usage, read_options, treat_options_simplest, verbose, parse_xml, error
from libs import filetype


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

class TxtGeneratorHandler(filetype.InputHandler):
    def __init__(self):
        self.entity_counter = 0

    def handle_sentence(self, sentence, info={}):
        """TODO: doc"""
        global attributes
        if self.entity_counter % 100 == 0 :
            verbose( "Processing ngram number %(n)d" % { "n":self.entity_counter } )
        for word in sentence:
            vals = [getattr(word, attr) for attr in attributes]
            print(ATTRIBUTE_SEPARATOR.join(vals),end="")
        print("")
        self.entity_counter += 1


################################################################################

def treat_options(opts, arg, n_arg, usage_string):
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.
        
        @param usage_string The usage string for the current script.    
    """
    global attributes

    treat_options_simplest( opts, arg, n_arg, usage_string )
    
    for (o, a) in opts:
        if o in ("-a", "--attributes"):
            attributes = a.split(":")
            for attr in attributes:
                if attr not in WORD_ATTRIBUTES:
                    error("Unknown attribute '%s'!" % attr)

    if attributes is None:
        print >>sys.stderr, "The option -a <attributes> is mandatory."
        usage(usage_string)
        sys.exit(2)


################################################################################
# MAIN SCRIPT    

longopts = ["atttibutes="]
arg = read_options("a:", longopts, treat_options, -1, usage_string)
filetype.parse(arg, TxtGeneratorHandler())

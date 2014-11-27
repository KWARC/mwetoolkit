#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# xml2conll.py is part of mwetoolkit
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
    This script converts an XML corpus (mwetoolkit-corpus.dtd)
    into a corresponding representation in the CONLL file format.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys

from libs.genericXMLHandler import GenericXMLHandler
from libs.util import read_options, treat_options_simplest, parse_xml, verbose
from libs.base.__common import WILDCARD
     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s OPTIONS <file.xml>

OPTIONS may be:

-s OR --space-sep
    Separate output by spaces, not tabs.

%(common_options)s

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""   
space_separators = False
sentence_counter = 0
            
################################################################################     
       
def treat_entity(entity) :
    """Called for each `Sentence`.
    Prints a line with the following 10 values
    (or "_", when unavailable), separated by tabs:

    0. ID      -- word index in sentence (starting at 1).
    1. FORM    -- equivalent to `surface` in XML.
    2. LEMMA   -- equivalent to `lemma` in XML.
    3. CPOSTAG -- equivalent to `pos` in XML.
    4. POSTAG  -- simplified version of `pos` in XML.
                  Currently, same as CPOSTAG.
    5. FEATS   -- currently, "_".
    6. HEAD    -- equivalent to second part of `syn` in XML
                  (that is, the parent of this word)
    7. DEPREL  -- equivalent to the first part of `syn` in XML
                  (that is, the relation between this word and HEAD).
    8. PHEAD   -- currently, "_".
    9. PDEPREL -- currently, "_".

    @param entity The `Sentence` that is being read from the XML file.
    """
    global sentence_counter
    if sentence_counter % 100 == 0:
        verbose("Processing sentence number %(n)d" % {"n": sentence_counter})
    if sentence_counter != 0:
        print("")

    for i,w in enumerate(entity):
        # TODO escape this output
        FORM = w.surface
        LEMMA = handle_wildcard(w.lemma)
        CPOSTAG = handle_wildcard(w.pos)
        POSTAG = CPOSTAG

        if ":" in w.syn:
            DEPREL, HEAD = w.syn.split(":", 1)
        else:
            DEPREL, HEAD = handle_wildcard(w.syn), "_"

        print_line(i+1, FORM, LEMMA, CPOSTAG, POSTAG,
                "_", HEAD, DEPREL, "_", "_")

    sentence_counter += 1


def handle_wildcard(argument):
    r"""Transform WILDCARD into CONLL "_"."""
    if argument == WILDCARD:
        return "_"
    return argument


def print_line(ID, FORM, LEMMA, *args):
    if space_separators:
        CPOSTAG, POSTAG, args = args[0], args[1], args[2:]
        print("%2d  %-20s  %-20s  %-5s  %-5s  %s" \
                % (ID,FORM,LEMMA, CPOSTAG, POSTAG, "  ".join(args)))
    else:
        print(ID, FORM, LEMMA, *args, sep="\t")

################################################################################     

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    treat_options_simplest(opts, arg, n_arg, usage_string)

    for o, a in opts:        
        if o in ("s", "--space-sep"):
            global space_separators
            space_separators = True
        else:
            sys.exit(1)

################################################################################     
# MAIN SCRIPT

longopts = ["space-sep"]
arg = read_options("s:", longopts, treat_options, -1, usage_string)
handler = GenericXMLHandler(treat_entity=treat_entity, gen_xml=False)
parse_xml(handler, arg)

#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010 Carlos Ramisch
# 
# changepos.py is part of mwetoolkit
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
   Simplifies the POS tags of the words from Penn Treebank format to simple tags
"""

import sys
import pdb
import xml.sax

from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import read_options, treat_options_simplest, verbose

################################################################################
# GLOBALS

usage_string = """Usage:

python %(program)s OPTIONS <corpus.xml>

OPTIONS may be:

-v OR --verbose
    Print friendly messages that explain what is happening.

    The <corpus.xml> file must be valid XML (dtd/mwetoolkit-corpus.dtd).
"""
sentence_counter = 0
# This table contains mainly exceptions that need special treatment
conv_table = { "MD": "V",    # modal verb is a verb
               "IN": "P",    # Preposition in is a preposition
               "TO": "P",    # Preposition to is a preposition
               "RP": "P",
               "EX": "P",
               "CT": "DT", 
               "XT": "DT",
               "CD": "NUM",
               "POS": "PP",
               "FW": "FW",   # Foreign word stays foreign word
               "SYM": "PCT", # Special symbol is a punctuation sign
               "LS": "PCT",  # List symbol is a punctuation sign
               "``": "PCT",  # Quotes are a punctuation sign
               "''": "PCT",  # Quotes are a punctuation sign
               "SENT":"PCT", # Sentence delimiter is a punctuation sign
               "UH":"UH",  } # Interjection stays interjectio

################################################################################

def treat_meta( meta ) :
    """
        Simply prints the meta header to the output without modifications.

        @param meta The `Meta` header that is being read from the XML file.
    """

    print meta.to_xml().encode( 'utf-8' )

################################################################################

def treat_entity( entity ) :
    """
        For each sentence in the corpus, simplify the POS tags using simple
        heuristics.

        @param sentence A `Sentence` that is being read from the XML file.
    """
    global conv_table, sentence_counter
    if sentence_counter % 100 == 0 :
        verbose( "Processing sentence number %(n)d" % { "n":sentence_counter } )
    for w in entity :
        # The "split" part is to avoid that multiple POS like NNS|JJ are not 
        # converted. We simply take the first POS, ignoring the second one
        w.pos = w.pos.split("|")[0]
        if w.pos.startswith( "N" ) or w.pos.startswith( "V" ) : # NOUNS / VERBS
            w.pos = w.pos[ 0 ]
        elif w.pos.startswith( "J" ) : # ADJECTIVES
            w.pos = "A"
        elif "RB" in w.pos : # ADVERBS
            w.pos = "R"
        elif "DT" in w.pos : # DETERMINERS
            w.pos = "DT"
        elif "CC" in w.pos : # CONJUNCTIONS
            w.pos = "CC"
        elif w.pos.startswith( "PRP" ) or w.pos.startswith( "PP" ) or w.pos.startswith( "WP" ) : # PRONOUNS
            w.pos = "PP"
        elif w.pos in "\"()':?-/$.," : # ADVERBS
            w.pos = "PCT"
        else :
            try :
                w.pos = conv_table[ w.pos ]
            except Exception :
                print >> sys.stderr, "WARNING: part of speech " + str( w.pos ) + \
                                  " not converted."
    print entity.to_xml().encode( 'utf-8' )
    sentence_counter += 1

################################################################################
# MAIN SCRIPT


arg = read_options( "v", ["verbose"], treat_options_simplest, -1, usage_string )
try :
    parser = xml.sax.make_parser()
    handler = GenericXMLHandler( treat_meta=treat_meta,
                                 treat_entity=treat_entity,
                                 gen_xml=True )
    parser.setContentHandler( handler )
    if len( arg ) == 0 :
        parser.parse( sys.stdin )
        print handler.footer
    else :
        for a in arg :
            input_file = open( a )
            parser.parse( input_file )
            footer = handler.footer
            handler.gen_xml = False
            input_file.close()
            entity_counter = 0
        print footer
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid XML file," +\
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-*.dtd)"


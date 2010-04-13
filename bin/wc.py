#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# wc.py is part of mwetoolkit
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
    This script simply gives some stats about a XML file, such as number
    of words, etc. Output is written on stderr.

    This script is DTD independent, that is, it might be called on a corpus
    file, on a list of candidates or on a dictionary.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import pdb

from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import read_options, treat_options_simplest, verbose
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s OPTIONS <file.xml>

    OPTIONS may be:


-v OR --verbose
    Print messages that explain what is happening.

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""    
char_counter = 0
word_counter = 0
entity_counter = 0
 
################################################################################     
       
def treat_entity( entity ) :
    """
        For each candidate/sentence, counts the number of occurrences, the 
        number of words and the number of characters (except spaces and XML).
        
        @param ngram A subclass of `Ngram` that is being read from the XML.
    """
    global char_counter, word_counter, entity_counter
    
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )

    for word in entity :
        word_counter += 1
        char_counter += len( word )
    entity_counter += 1

################################################################################     
# MAIN SCRIPT

arg = read_options( "v", ["verbose"], treat_options_simplest, 1, usage_string )
try :    
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    
    handler = GenericXMLHandler( treat_entity=treat_ngram )
    
    parser.setContentHandler( handler )
    parser.parse( input_file )
    input_file.close()
    print >> sys.stderr, str( entity_counter ) + " entities in "   + arg[ 0 ]
    print >> sys.stderr, str( word_counter )   + " words in "      + arg[ 0 ]
    print >> sys.stderr, str( char_counter )   + " characters in " + arg[ 0 ]    
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid XML file," +\
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-*.dtd)"

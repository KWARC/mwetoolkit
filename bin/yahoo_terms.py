#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# yahoo_terms.py is part of mwetoolkit
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
"""

import sys
import xml.sax

import install
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.__common import XML_HEADER, XML_FOOTER
from util import usage, read_options, treat_options_simplest
from xmlhandler.classes.yahooTerms import YahooTerms
from xmlhandler.classes.candidate import Candidate
from xmlhandler.classes.ngram import Ngram
from xmlhandler.classes.word import Word
from config import WILDCARD

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s <corpus.xml>

    The <corpus.xml> file must be valid XML (dtd/mwetoolkit-corpus.dtd).
"""
sentences_buffer = []
BUFFER_LIMIT = 10
domain = ""
yahooTerms = YahooTerms()
terms = set([])

################################################################################

def treat_sentence( sentence ) :
    """
        For each sentence in the corpus, 
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """
    
    global sentences_buffer, domain, BUFFER_LIMIT, yahooTerms, terms
    
    sentences_buffer.append( sentence.to_surface() )
    if len( sentences_buffer ) > BUFFER_LIMIT :     
        sent_terms = yahooTerms.search_terms(" ".join(sentences_buffer),domain)   
        terms = terms | set(sent_terms)        
        sentences_buffer = []
    
################################################################################

def print_terms() :
    """
    """
    global terms
    id_number = 0
    for term in terms :
        words = []
        for word in term.split( " " ) :
            words.append( Word( word, WILDCARD, WILDCARD, [] ) )
        if len( words ) > 1 :
            base_form = Ngram( words, [] )
            c = Candidate( base_form, id_number, [], [], [] )
            id_number += 1
            print c.to_xml().encode( "utf-8" )
    
################################################################################
# MAIN SCRIPT


arg = read_options( "v", ["verbose"], treat_options_simplest, 1, usage_string )

try :    
    print XML_HEADER % { "root" : "candidates" }
    print "<meta></meta>"
    input_file = open( arg[ 0 ] )    
    parser = xml.sax.make_parser()
    parser.setContentHandler( CorpusXMLHandler( treat_sentence ) ) 
    parser.parse( input_file )
    input_file.close()
    print_terms()
    print XML_FOOTER % { "root" : "candidates" }
except IOError, err :  
    print err
    print "Error reading corpus file. Please verify __common.py configuration"        
    sys.exit( 2 )      
except Exception, err :
    print err
    print "You probably provided an invalid corpus file, please " + \
          "validate it against the DTD (dtd/mwetoolkit-corpus.dtd)"

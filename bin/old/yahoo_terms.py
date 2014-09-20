#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
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

from bin.libs.xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.__common import XML_HEADER, XML_FOOTER
from util import read_options, treat_options_simplest
from xmlhandler.classes.yahooTerms import YahooTerms
from xmlhandler.classes.candidate import Candidate
from xmlhandler.classes.word import Word
from config import WILDCARD



################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s <corpus.xml>

%(common_options)s

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
        terms = terms | set( sent_terms )        
        sentences_buffer = []
    
################################################################################

def print_terms() :
    """
    """
    global terms
    global sentences_buffer, domain, yahooTerms
    
    if len( sentences_buffer ) > 0 :
        #pdb.set_trace()
        sent_terms = yahooTerms.search_terms(" ".join(sentences_buffer),domain)   
        terms = terms | set( sent_terms )        
        sentences_buffer = []
    
    id_number = 0

    for term in terms :
        c = Candidate( id_number, [], [], [], [], [] )    
        for word in term.split( " " ) :
            c.append( Word( WILDCARD, word, WILDCARD, WILDCARD, [] ) )
        if len( c ) > 1 :
            id_number = id_number + 1
            print c.to_xml().encode( "utf-8" )
    
################################################################################
# MAIN SCRIPT

arg = read_options( "", [], treat_options_simplest, -1, usage_string )

parser = xml.sax.make_parser()
handler = CorpusXMLHandler( treat_sentence )
parser.setContentHandler( handler )
print XML_HEADER % { "root" : "candidates", "ns" : "" }
print "<meta></meta>"    
if len( arg ) == 0 :
    parser.parse( sys.stdin )
    print_terms()
    print XML_FOOTER % { "root" : "candidates" }
else :
    for a in arg :
        input_file = open( a )
        parser.parse( input_file )
        footer = handler.footer
        handler.gen_xml = False
        input_file.close()
        entity_counter = 0
    print_terms()
    print XML_FOOTER % { "root" : "candidates" }

#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# corpusDTDHandler.py is part of mwetoolkit
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
    This module provides the `CorpusXMLHandler` class. This class is a SAX 
    parser for XML documents that are valid corpora according to 
    mwetoolkit-corpus.dtd.
"""

import xml.sax

from classes.__common import WILDCARD, XML_HEADER, XML_FOOTER
from classes.word import Word
from classes.sentence import Sentence
from util import strip_xml

################################################################################

class CorpusXMLHandler( xml.sax.ContentHandler ) :
    """
        SAX parser for corpus file. The XML corpus file must be valid according 
        to mwetoolkit-corpus.dtd. The class works by calling a callback function
        that is passed to the constructor when a sentence is read, so you should 
        define and implement the correct callback and then parse the document.
    """

######################################################################
    
    def __init__( self, treat_sentence=lambda x:None, gen_xml="" ) :
        """
            Creates a new corpus handler. The argument is a callback function 
            that will treat the XML information.
            
            @param treat_sentence Callback function that receives as argument an 
            object of type `Sentence`, default is dummy function that does 
            nothing. You should implement your own function to treat a sentence.
            
            @return A new instance of a `xml.sax.ContentHandler` with the 
            specified callback function. This content handler should be used to 
            parse the XML file.
        """
        self.treat_sentence = treat_sentence       
        self.s_id = -1
        self.gen_xml = gen_xml
        self.footer = ""
            
################################################################################

    def startElement( self, name, attrs ) :  
        """
            Treats starting tags in corpus XML file, overwrites default SAX 
            dummy function.
            
            @param name The name of the opening element.
            
            @param attrs Dictionary containing the attributes of this element.
        """      
        if name == "s" :
            if( "s_id" in attrs.keys() ) :
                self.s_id = int( strip_xml( attrs[ "s_id" ] ) )
            self.sentence = Sentence( [], self.s_id )
        elif name == "w" :
            surface = strip_xml( attrs[ "surface" ] ) # Mandatory in the corpus
            if( "lemma" in attrs.keys() ) :
                lemma = strip_xml( attrs[ "lemma" ] )
            else :
                lemma = WILDCARD
            if( "pos" in attrs.keys() ) :
                pos = strip_xml( attrs[ "pos" ] )
            else :
                pos = WILDCARD
            if( "syn" in attrs.keys() ) :
                syn = strip_xml( attrs[ "syn" ] )
            else :
                syn = WILDCARD
            # Add word to the sentence that is currently bein read
            self.sentence.append( Word( surface, lemma, pos, syn, [] ) )
        elif name == "corpus" and self.gen_xml :
            print XML_HEADER % { "root" : self.gen_xml, "ns" : "" }
            

################################################################################

    def endElement( self, name ) :
        """
            Treats ending tags in corpus XML file, overwrites default SAX dummy 
            function.
            
            @param name The name of the closing element.            
        """       
        if name == "s" :
            # A complete sentence was read, call the callback function
            self.treat_sentence( self.sentence )
        elif name == "corpus" and self.gen_xml :
            # Must only be printed at the end of the main script. Some scripts
            # only print the result after the XML was 100% read, and this
            # makes it necessary a temporary buffer for the footer. Not really a
            # perfect solution but it will do for now
            self.footer = XML_FOOTER % { "root" : self.gen_xml }

     
 ################################################################################

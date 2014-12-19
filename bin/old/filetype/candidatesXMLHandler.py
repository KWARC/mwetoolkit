#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# candidatesDTDHandler.py is part of mwetoolkit
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
    This module provides the `CandidatesXMLHandler` class. This class is a SAX 
    parser for XML documents that are valid candidate lists according to 
    mwetoolkit-candidates.dtd.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import xml.sax

from libs.base.__common import WILDCARD, XML_HEADER, XML_FOOTER
from libs.base.meta import Meta
from libs.base.corpus_size import CorpusSize
from libs.base.meta_feat import MetaFeat
from libs.base.meta_tpclass import MetaTPClass
from libs.base.candidate import Candidate
from libs.base.ngram import Ngram
from libs.base.word import Word
from libs.base.frequency import Frequency
from libs.base.feature import Feature
from libs.base.tpclass import TPClass
from libs.util import strip_xml

################################################################################

class CandidatesXMLHandler( xml.sax.ContentHandler ) :
    """
        SAX parser for candidates file. The XML candidates file must be valid 
        according to mwetoolkit-candidates.dtd. The class works by calling
        callback functions that are passed to the constructor when an entity is 
        read, so you should define and implement the correct callbacks and then
        parse the document.
    """

################################################################################
    
    def __init__( self,
                  treat_meta=lambda x:None, 
                  treat_candidate=lambda x:None,
                  gen_xml="" ) :
        """
            Creates a new candidate handler. The arguments are two callback 
            functions that will treat the XML information.
            
            @param treat_meta Callback function that receives as argument an 
            object of type `Meta`, default is dummy function that does nothing. 
            You should implement your own function to treat the meta element.
            
            @param treat_candidate Callback function that receives as argument 
            an object of type `Candidate`, default is dummy function that does 
            nothing. You should implement yout own function to treat a 
            candidate.
            
            @return A new instance of a `xml.sax.ContentHandler` with the 
            specified callback functions. This content handler should be used to 
            parse the XML file.
        """
        self.treat_candidate = treat_candidate
        self.treat_meta = treat_meta
        self.candidate = None 
        self.ngram = None  
        self.word = None
        self.freq = None   
        self.id_number_counter = 0
        self.meta = None
        self.gen_xml = gen_xml
        self.footer = ""
        self.inbigram = False
        self.inoccurs = False
        self.invars = False
           
################################################################################

    def startElement( self, name, attrs ) :
        """
            Treats starting tags in candidates XML file, overwrites default SAX 
            dummy function.
            
            @param name The name of the opening element.
            
            @param attrs Dictionary containing the attributes of this element.
        """
        if name == "cand" :  
            # Get the candidate ID or else create a new ID for it          
            if "candid" in attrs.keys() :
                id_number = strip_xml( attrs[ "candid" ] )
            else :
                id_number = self.id_number_counter
                self.id_number_counter = self.id_number_counter + 1
            # Instanciates an empty mwe candidate that will be treated
            # when the <cand> tag is closed
            self.candidate = Candidate( id_number, None, [], [], [], [] )
        elif name == "ngram" :
            # Instanciates a new ngram. We do not know which words it
            # contains, so for the moment we just keep it on the stack
            self.ngram = Ngram( [], [] )
        elif name == "bigrams" :
            self.inbigram = True
        elif name == "occurs" :
            self.inoccurs = True
        elif name == "vars" :
            self.invars = True
        elif name == "w" :
            # Instanciates a word. Missing attribute values are 
            # assigned to a wildcard string, meaning "uninformed" for
            # candidates or "any" for patterns
            if "surface" in attrs.keys() :
                surface = strip_xml( attrs[ "surface" ] )
            else :
                surface = WILDCARD
            if "lemma" in attrs.keys() :
                lemma = strip_xml( attrs[ "lemma" ] )
            else :
                lemma = WILDCARD
            if "pos" in attrs.keys() :
                pos = strip_xml( attrs[ "pos" ] )
            else :
                pos = WILDCARD
            self.word = Word( surface, lemma, pos, WILDCARD, [] )
            # Add the word to the ngram that is on the stack
            self.ngram.append( self.word )
        elif name == "freq" :
            self.freq = Frequency( strip_xml( attrs[ "name" ] ), 
                                   int( strip_xml( attrs[ "value" ] ) ) )
            # If <freq> is inside a word element, then it's the word's
            # frequency, otherwise it corresponds to the frequency of
            # the ngram that is being read
            if self.word :
                self.word.add_frequency( self.freq )            
            else :
                self.ngram.add_frequency( self.freq )

        elif name == "sources":
            self.ngram.add_sources(attrs["ids"].split(';'))

        elif name == "feat" :
            feat_name = strip_xml( attrs[ "name" ] )
            feat_value = strip_xml( attrs[ "value" ] )
            feat_type = self.meta.get_feat_type( feat_name )
            if feat_type == "integer" :
                feat_value = int( feat_value )
            elif feat_type == "real" :
                feat_value = float( feat_value )                
            f = Feature( feat_name, feat_value )
            self.candidate.add_feat( f ) 
        elif name == "tpclass" :
            tp = TPClass( strip_xml( attrs[ "name" ] ), 
                          strip_xml( attrs[ "value" ] ) )
            self.candidate.add_tpclass( tp )
            
        # Meta section and elements, correspond to meta-info about the
        # candidates lists. Meta-info are important for generating
        # features and converting to arff files, and must correspond
        # to the info in the candidates (e.g. meta-feature has the 
        # same name as actual feature)      
        elif name == "meta" :
            self.meta = Meta( [], [], [] )
        elif name == "corpussize" :      
            cs = CorpusSize( attrs[ "name" ], attrs[ "value" ] )      
            self.meta.add_corpus_size( cs )
        elif name == "metafeat" :      
            mf = MetaFeat( attrs[ "name" ], attrs[ "type" ] )     
            self.meta.add_meta_feat( mf )  
        elif name == "metatpclass" :    
            mtp = MetaTPClass( attrs[ "name" ], attrs[ "type" ] )        
            self.meta.add_meta_tpclass( mtp )
        elif name == "candidates" and self.gen_xml :
            print(XML_HEADER % { "root" : self.gen_xml, "ns" : "" })

################################################################################

    def endElement( self, name ) :
        """
            Treats ending tags in candidates XML file, overwrites default SAX 
            dummy function.
            
            @param name The name of the closing element.            
        """    
        if name == "cand" :
            # Finished reading the candidate, call callback
            self.treat_candidate( self.candidate ) 
        elif name == "ngram" :
            if self.inoccurs :
                self.candidate.add_occur( self.ngram )
            elif self.inbigram :
                self.candidate.add_bigram( self.ngram )
            elif self.invars :
                self.candidate.add_var( self.ngram )
            else :
                self.candidate.word_list = self.ngram.word_list
                self.candidate.freqs = self.ngram.freqs
        elif name == "w" :  
            # Set word to none, otherwise I cannot make the difference between
            # the frequency of a word and the frequency of a whole ngram
            self.word = None        
        elif name == "meta" :
            # Finished reading the meta header, call callback        
            self.treat_meta( self.meta )
        elif name == "candidates" and self.gen_xml :
            # Must only be printed at the end of the main script. Some scripts
            # only print the result after the XML was 100% read, and this
            # makes it necessary a temporary buffer for the footer. Not really a
            # perfect solution but it will do for now
            self.footer = XML_FOOTER % { "root" : self.gen_xml }
        elif name == "bigram" :
            self.inbigram = False
        elif name == "occurs" :
            self.inoccurs = False
        elif name == "vars" :
            self.invars = False

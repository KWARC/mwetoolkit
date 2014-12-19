#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# dictDTDHandler.py is part of mwetoolkit
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
    This module provides the `DictXMLHandler` class. This class is a SAX
    parser for XML documents that are valid pattern or reference lists according 
    to mwetoolkit-dict.dtd.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import xml.sax

from libs.base.word import Word
from libs.base.entry import Entry
from libs.base.meta import Meta
from libs.base.feature import Feature
from libs.base.frequency import Frequency
from libs.base.corpus_size import CorpusSize
from libs.base.meta_feat import MetaFeat
from libs.base.__common import WILDCARD, XML_HEADER, XML_FOOTER
from libs.util import strip_xml

################################################################################

class DictXMLHandler( xml.sax.ContentHandler ) :
    """
        SAX parser for dict (patterns, reference) files. The XML file must be
        valid according to mwetoolkit-dict.dtd. The class works by calling a
        callback function that is passed to the constructor when an entry is
        read, so you should define and implement the correct callback and then 
        parse the document.
    """

################################################################################
    
    def __init__( self,
                  treat_meta=lambda x:None,
                  treat_entry=lambda x:None,
                  gen_xml="" ) :
        """
            Creates a new dict file handler. The argument is a
            callback function that will treat the XML information.
            
            @param treat_entry Callback function that receives as argument an
            object of type `Entry`, default is dummy function that does
            nothing. You should implement your own function to treat an entry.
            
            @return A new instance of a `xml.sax.ContentHandler` with the 
            specified callback function. This content handler should be used to 
            parse the XML file.
        """
        self.treat_entry = treat_entry
        self.treat_meta = treat_meta
        self.entry = None
        self.id_number_counter = 0
        self.gen_xml = gen_xml
        self.footer = ""
        self.meta = None

################################################################################

    def startElement( self, name, attrs ) :  
        """
            Treats starting tags in dictionary XML file, overwrites
            default SAX dummy function.
            
            @param name The name of the opening element.
            
            @param attrs Dictionary containing the attributes of this element.
        """
        if name == "entry" :
            # Get the candidate ID or else create a new ID for it
            if "entryid" in attrs.keys() :
                id_number = strip_xml( attrs[ "entryid" ] )
            else :
                id_number = self.id_number_counter
                self.id_number_counter = self.id_number_counter + 1
            # Instanciates an empty dict entry that will be treated
            # when the <entry> tag is closed
            self.entry = Entry( id_number, [], [], [] )
        elif name == "w" :
            if( "surface" in attrs.keys() ) :
                surface = strip_xml( attrs[ "surface" ] )
            else :
                surface = WILDCARD
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
            self.word = Word( surface, lemma, pos, syn, [] )
            self.entry.append( self.word )
        elif name == "freq" :
            self.freq = Frequency( strip_xml( attrs[ "name" ] ),
                                   int( strip_xml( attrs[ "value" ] ) ) )
            # If <freq> is inside a word element, then it's the word's
            # frequency, otherwise it corresponds to the frequency of
            # the ngram that is being read
            if self.word :
                self.word.add_frequency( self.freq )
            else :
                self.entry.add_frequency( self.freq )
        elif name == "feat" :
            feat_name = strip_xml( attrs[ "name" ] )
            feat_value = strip_xml( attrs[ "value" ] )
            feat_type = self.meta.get_feat_type( feat_name )
            if feat_type == "integer" :
                feat_value = int( feat_value )
            elif feat_type == "real" :
                feat_value = float( feat_value )
            f = Feature( feat_name, feat_value )
            self.entry.add_feat( f )
        # Meta section and elements, correspond to meta-info about the
        # reference lists. Meta-info are important for generating
        # features and converting to arff files, and must correspond
        # to the info in the dictionary (e.g. meta-feature has the
        # same name as actual feature)
        elif name == "meta" :
            self.meta = Meta( [], [], [] )
        elif name == "corpussize" :
            cs = CorpusSize( attrs[ "name" ], attrs[ "value" ] )
            self.meta.add_corpus_size( cs )
        elif name == "metafeat" :
            mf = MetaFeat( attrs[ "name" ], attrs[ "type" ] )
            self.meta.add_meta_feat( mf )
        elif name == "dict" and self.gen_xml :
            print(XML_HEADER % { "root" : self.gen_xml, "ns" : "" })
            
################################################################################

    def endElement( self, name ) :
        """
            Treats ending tags in dictionary XML file, overwrites
            default SAX dummy function.
            
            @param name The name of the closing element.            
        """      
        if name == "entry" :
            self.treat_entry( self.entry )
            self.entry = None
        elif name == "w" :
            self.word = None
        elif name == "meta" :
            # Finished reading the meta header, call callback 
            self.treat_meta( self.meta )
        elif name == "dict" and self.gen_xml :
                # Must only be printed at the end of the main script. Some scripts
                # only print the result after the XML was 100% read, and this
                # makes it necessary a temporary buffer for the footer. Not really a
                # perfect solution but it will do for now
                self.footer = XML_FOOTER % { "root" : self.gen_xml }

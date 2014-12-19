#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
# 
# genericXMLHandler.py is part of mwetoolkit
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
    This handler is aimed at processing any type of XML that contains a sequence
    of ngrams. It will apply exactly the same callback function to all ngrams,
    independently of the fact that they are mwe candidates, dictionary entries
    or corpus sentences. Since XML format differs (some have an explicit "ngram"
    element, others have not), we need to identify the file format at the
    beginning. This is done through the document's root element.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from .candidatesXMLHandler import CandidatesXMLHandler
from .corpusXMLHandler import CorpusXMLHandler
from .dictXMLHandler import DictXMLHandler
import xml.sax


################################################################################

class GenericXMLHandler( xml.sax.ContentHandler ) :
    """
        SAX parser for the three XML files supported by mwetoolkit. The XML
        file must be valid according to one of the DTDs provided by the toolkit.
        The class works by calling a callback function that is passed to the
        constructor when an entity (ngram) is read, so you should define and
        implement the correct callback and then parse the document. WARNING: the
        callback cannot make reference to any specific attribute of a type of
        entity. It must rather treat it as a generic ngram.
    """

################################################################################

    def __init__( self,
                  treat_meta=lambda x:None,
                  treat_entity=lambda x:None,
                  gen_xml=False ) :
        """
            Creates a new generic file handler. The argument is a
            callback function that will treat the XML information.

            @param treat_meta: Callback function that receives as argument an
            object of type `Meta`, default is dummy function that does nothing.
            You should implement your own function to treat the meta element.

            @param treat_entity: Callback function that receives as argument an
            object subtype of `Ngram`, default is dummy function that does
            nothing. You should implement your own function to treat an entity.

            @return A new instance of a `xml.sax.ContentHandler` with the
            specified callback function. This content handler should be used to
            parse the XML file.
        """
        self.treat_meta = treat_meta
        self.treat_entity = treat_entity
        self.entry = None
        self.handler = None
        self.gen_xml = gen_xml
        self.footer = ""

################################################################################

    def startElement( self, name, attrs ) :
        """
            Treats starting tags in geneirc XML file. It decides to create a
            specific handler upon the root element, but since this is dynamic,
            callbacks cannot make assumptions on the specific type of the
            parameter and should rather consider it as a generic object that
            inherits from `Ngram`

            @param name: The name of the opening element.

            @param attrs: Dictionary containing the attributes of this element.
        """
        if self.gen_xml :
            xml_type = name
        else :
            xml_type = ""
        if name == "dict" :
            self.handler = DictXMLHandler( treat_entry=self.treat_entity,
                                           treat_meta = self.treat_meta,
                                           gen_xml=xml_type )
            self.footer = "</dict>"
        elif name == "corpus" :
            self.handler = CorpusXMLHandler( treat_sentence=self.treat_entity,
                                             gen_xml=xml_type )
            self.footer = "</corpus>"
        elif name == "candidates" :
            self.handler = CandidatesXMLHandler( treat_candidate=self.treat_entity,
                                                 treat_meta = self.treat_meta,
                                                 gen_xml=xml_type )
            self.footer = "</candidates>"
        self.handler.startElement(name, attrs)

################################################################################

    def endElement( self, name ) :
        """
            Treats ending tags in generic XML file, overwrites default SAX dummy
            function.

            @param name: The name of the closing element.
        """
        self.handler.endElement(name)        

################################################################################

    def characters( self, content ):
        """
            Treats character content in generic XML file, overwrites default SAX
            dummy function.

        @param content: The text found in the XML file
        """
        self.handler.characters(content)

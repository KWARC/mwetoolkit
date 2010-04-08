#!/usr/bin/python
"""
    This module provides the `PatternsXMLHandler` class. This class is a SAX 
    parser for XML documents that are valid pattern or reference lists according 
    to mwttoolkit-patterns.dtd.
"""

import sys
import xml.sax

from classes.word import Word
from classes.pattern import Pattern
from classes.__common import WILDCARD
from util import strip_xml

################################################################################

class PatternsXMLHandler( xml.sax.ContentHandler ) :
    """
        SAX parser for patterns or reference files. The XML file must be valid 
        according to mwttoolkit-patterns.dtd. The class works by calling a 
        callback function that is passed to the constructor when a pattern is 
        read, so you should define and implement the correct callback and then 
        parse the document.
    """

################################################################################
    
    def __init__( self, treat_pattern ) :
        """
            Creates a new patterns or reference handler. The argument is a 
            callback function that will treat the XML information.
            
            @param treat_pattern Callback function that receives as argument an 
            object of type `Pattern`, default is dummy function that does 
            nothing. You should implement your own function to treat a pattern.
            
            @return A new instance of a `xml.sax.ContentHandler` with the 
            specified callback function. This content handler should be used to 
            parse the XML file.
        """
        self.treat_pattern = treat_pattern
        self.pattern = None      
            
################################################################################

    def startElement( self, name, attrs ) :  
        """
            Treats starting tags in patterns or reference XML file, overwrites 
            default SAX dummy function.
            
            @param name The name of the opening element.
            
            @param attrs Dictionary containing the attributes of this element.
        """         
        if name == "pattern" :               
            self.pattern = Pattern( [], [] )
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
            self.pattern.append_word( Word( surface, lemma, pos, [] ) )
            
################################################################################

    def endElement( self, name ) :
        """
            Treats ending tags in patterns or reference XML file, overwrites 
            default SAX dummy function.
            
            @param name The name of the closing element.            
        """      
        if name == "pattern" :
            self.treat_pattern( self.pattern )      
     
################################################################################

if __name__ == "__main__" :
    import doctest
    doctest.testmod()

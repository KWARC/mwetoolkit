#!/usr/bin/python
"""
    This module provides the `CorpusXMLHandler` class. This class is a SAX 
    parser for XML documents that are valid corpora according to 
    mwttoolkit-corpus.dtd.
"""

import xml.sax

from classes.__common import WILDCARD
from classes.word import Word
from classes.sentence import Sentence
from util import strip_xml

################################################################################

class CorpusXMLHandler( xml.sax.ContentHandler ) :
    """
        SAX parser for corpus file. The XML corpus file must be valid according 
        to mwttoolkit-corpus.dtd. The class works by calling a callback function 
        that is passed to the constructor when a sentence is read, so you should 
        define and implement the correct callback and then parse the document.
    """

######################################################################
    
    def __init__( self, treat_sentence=lambda x:None ) :
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
            
################################################################################

    def startElement( self, name, attrs ) :  
        """
            Treats starting tags in corpus XML file, overwrites default SAX 
            dummy function.
            
            @param name The name of the opening element.
            
            @param attrs Dictionary containing the attributes of this element.
        """      
        if name == "s" :
            if( "s_id" in attrs ) :
                self.s_id = int( strip_xml( attrs[ "s_id" ] ) )
            self.sentence = Sentence( [], self.s_id )
        elif name == "w" :
            surface = strip_xml( attrs[ "surface" ] ) # Mandatory in the corpus
            if( "lemma" in attrs ) :
                lemma = strip_xml( attrs[ "lemma" ] )
            else :
                lemma = WILDCARD
            if( "pos" in attrs ) :
                pos = strip_xml( attrs[ "pos" ] )
            else :
                pos = WILDCARD
            # Add word to the sentence that is currently bein read
            self.sentence.append_word( Word( surface, lemma, pos, [] ) )
            

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
     
################################################################################

if __name__ == "__main__" :
    import doctest
    doctest.testmod()    

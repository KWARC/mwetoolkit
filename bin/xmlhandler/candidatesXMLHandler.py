#!/usr/bin/python
"""
    This module provides the `CandidatesXMLHandler` class. This class is a SAX 
    parser for XML documents that are valid candidate lists according to 
    mwttoolkit-candidates.dtd.
"""

import xml.sax

from classes.__common import WILDCARD
from classes.meta import Meta
from classes.corpus_size import CorpusSize
from classes.meta_feat import MetaFeat
from classes.meta_tpclass import MetaTPClass
from classes.candidate import Candidate
from classes.ngram import Ngram
from classes.word import Word
from classes.frequency import Frequency
from classes.feature import Feature
from classes.tpclass import TPClass
from util import strip_xml

################################################################################

class CandidatesXMLHandler( xml.sax.ContentHandler ) :
    """
        SAX parser for candidates file. The XML candidates file must be valid 
        according to mwttoolkit-candidates.dtd. The class works by calling 
        callback functions that are passed to the constructor when an entity is 
        read, so you should define and implement the correct callbacks and then
        parse the document.
    """

################################################################################
    
    def __init__( self,
                  treat_meta=lambda x:None, 
                  treat_candidate=lambda x:None ) : 
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
            if "id" in attrs.keys() :
                id_number = strip_xml( attrs[ "id" ] )
            else :
                id_number = self.id_number_counter
                self.id_number_counter = self.id_number_counter + 1
            # Instanciates an empty mwt candidate that will be treated
            # when the <cand> tag is closed
            self.candidate = Candidate( None, id_number, [], [], [] )
        elif name == "ngram" :
            # Instanciates a new ngram. We do not know which words it
            # contains, so for the moment we just keep it on the stack
            self.ngram = Ngram( [], [] )            
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
            self.word = Word( surface, lemma, pos, [] )
            # Add the word to the ngram that is on the stack
            self.ngram.append_word( self.word )
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
            # The candidate already has a base form, so the ngram that I just 
            # read is an occurrence
            if self.candidate.base :
                self.candidate.add_occur( self.ngram )
            # This is the first ngram that I read, so it has to be the base form                
            else :
                self.candidate.base = self.ngram
        elif name == "w" :  
            # Set word to none, otherwise I cannot make the difference between
            # the frequency of a word and the frequency of a whole ngram
            self.word = None        
        elif name == "meta" :
            # Finished reading the meta header, call callback        
            self.treat_meta( self.meta )  
     
################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()    

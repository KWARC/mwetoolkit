#!/usr/bin/python
"""
    This module provides the CorpusSize class. This class is a representation of 
    a meta-information about the number of tokens in a given corpus.
"""

from feature import Feature

################################################################################

class CorpusSize( Feature ) :
    """
        A `CorpusSize` object is a meta-information about a given corpus, it
        informs about the number of tokens in this corpus. For each corpus used
        to extract frequencies, there should be a <corpussize> element in the
        <meta> header, so that Association Measures can be calculated as 
        features for candidates. CorpusSize extends `Feature`, so the name 
        corresponds to the name that identifies the corpus while value is an
        integer containing (an approximation of) the number of tokens in the
        corpus.    
    """

################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <corpussize> with its 
            attributes, according to mwttoolkit-candidates.dtd.
        """
        return "<corpussize name=\"" + self.name + \
               "\" value=\"" + str(self.value) + "\" />"
        
################################################################################

if __name__ == "__main__" :
    import doctest
    doctest.testmod()

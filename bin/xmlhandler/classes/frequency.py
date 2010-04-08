#!/usr/bin/python
"""
    This module provides the `Frequency` class. This class represents a 
    frequency of occurrences of an element in a corpus, i.e. an integer for the
    number of times the element (word or ngram) appears in the corpus.
"""

from feature import Feature

################################################################################

class Frequency( Feature ) :
    """
        A `Frequency` is a count of occurrences of a certain element (a word or
        a ngram) in a certain corpus. Frequency extends `Feature`, so the name 
        corresponds to the name that identifies the corpus from which the 
        frequency was drawn while value is an integer containing (an 
        approximation of) the number of times the element occurs in the corpus.    
    """

################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <freq> with its 
            attributes, according to mwttoolkit-candidates.dtd.
        """
        return "<freq name=\"" + self.name + \
               "\" value=\"" + str(self.value) + "\" />"
        
################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()   

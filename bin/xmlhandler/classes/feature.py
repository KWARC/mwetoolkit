#!/usr/bin/python
"""
    This module provides the `Feature` class. This class represents a feature of
    the candidate, i.e. a pair attribute-value that describes it.
"""

################################################################################

class Feature :
    """
        A MWT candidate feature is a pair name-value that describes a specific
        aspect of the candidate, such as a measure, a lingustic property, a 
       count, etc.
    """

################################################################################

    def __init__( self, name, value ) :
        """
            Instanciates a new `Feature`, which is a general name for a pair
            attribute-value. A feature aims at the description of one aspect of
            the candidate, and is supposed to be an abstraction that allows a
            machine learning algorithm to create generalisations from instances.
            
            @param name String that identifies the `Feature`.
            
            @param value The value of the feature. A value is not typed, it can
            be an integer, a real number, a string or an element of an 
            enumeration (allowed types in WEKA).
            
            @return A new instance of `Feature`.
        """
        self.name = name
        self.value = value
        
################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <feat> with its
            attributes, according to mwttoolkit-candidates.dtd.
        """
        return "<feat name=\"" + self.name + "\" value=\"" + \
               str(self.value) + "\" />"
        
################################################################################

if __name__ == "__main__" :
    import doctest
    doctest.testmod()

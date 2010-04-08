#!/usr/bin/python
"""
    This module provides the `MetaFeat` class. This class represents the 
    meta-information about a `Feature`, specially its type.
"""

from feature import Feature

################################################################################

class MetaFeat( Feature ) :
    """
        A meta-feature is the meta-information about a candidate feature. 
        Meta-features are generally placed in the header of the XML file 
        (in the `Meta` element) and contain the type of a feature. MetaFeat 
        extends `Feature`, so the name corresponds to the name that uniquely 
        identifies the feature while value corresponds to the type of the
        feature. The type can be an "integer", a "real" number, a "string" or an 
        element of an enumeration e.g. "{class1,class2}". These are the allowed 
        types in WEKA's arff file format.
    """

################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <metafeat> with its 
            attributes, according to mwttoolkit-candidates.dtd.
        """
        return "<metafeat name=\"" + self.name + \
               "\" type=\"" + str(self.value) + "\" />"
        
################################################################################

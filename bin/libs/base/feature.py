#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# feature.py is part of mwetoolkit
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
    This module provides the `Feature` class. This class represents a feature of
    the candidate, i.e. a pair attribute-value that describes it.
"""

################################################################################

class Feature(object) :
    """
        A MWE candidate feature is a pair name-value that describes a specific
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

    def __eq__( self, a_feat ) :
        """
            TODO: doc
        """
        return self.name == a_feat.name and self.value == a_feat.value

################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <feat> with its
            attributes, according to mwetoolkit-candidates.dtd.
        """
        return "<feat name=\"" + self.name + "\" value=\"" + \
               str(self.value) + "\" />"
        
################################################################################

if __name__ == "__main__" :
    import doctest
    doctest.testmod()

#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# genericDTDHandler.py is part of mwetoolkit
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
    This module provides the `MetaTPClass` class. This class represents the 
    meta-information about a `TPClass`, specially the enumeration of possible 
    class values.
"""

from feature import Feature

######################################################################

class MetaTPClass( Feature ) :
    """
        A meta True Positive class is the meta-information about a TP class. 
        Meta-TP classes are generally placed in the header of the XML file 
        (in the `Meta` element) and contain the number of possible TP classes in 
        the form of an enumeration. MetaTPClass extends `Feature`, so the name 
        corresponds to the name that uniquely identifies the `TPClass` while 
        value corresponds to the type of the class, i.e. an enumeration of 
        possible classes e.g. "{class1,class2,class3}". The evaluation can be 
        2-classes, in which case MetaTPClass will probably have the type 
        "{True,False}", or multiclass, where a larger number of possible classes 
        is defined. In the case of multi-class evaluation, please be sure that 
        the corresponding class values are handled by the machine learning 
        algorithm that you plan to use. These are the allowed types in WEKA's 
        arff file format. 
    """

######################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <metatpclass> with its 
            attributes, according to mwttoolkit-candidates.dtd.
        """
        return "<metatpclass name=\"" + self.name + \
               "\" type=\"" + str(self.value) + "\" />"
        
######################################################################

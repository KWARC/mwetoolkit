#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# meta_feat.py is part of mwetoolkit
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
    This module provides the `MetaFeat` class. This class represents the 
    meta-information about a `Feature`, specially its type.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.base.feature import Feature

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
            attributes, according to mwetoolkit-candidates.dtd.
        """
        return "<metafeat name=\"" + self.name + \
               "\" type=\"" + str(self.value) + "\" />"

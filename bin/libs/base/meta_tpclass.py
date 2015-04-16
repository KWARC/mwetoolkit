#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# meta_tpclass.py is part of mwetoolkit
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

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from .meta_feat import MetaFeat

######################################################################

class MetaTPClass( MetaFeat ) :
    """
        A meta True Positive class is the meta-information about a TP class. 
        Meta-TP base are generally placed in the header of the XML file
        (in the `Meta` element) and contain the number of possible TP base in
        the form of an enumeration. MetaTPClass extends `MetaFeat`, so the name 
        corresponds to the name that uniquely identifies the `TPClass` while 
        type corresponds to the type of the class, i.e. an enumeration of 
        possible base e.g. "{class1,class2,class3}". The evaluation can be
        2-base, in which case MetaTPClass will probably have the type
        "{True,False}", or multiclass, where a larger number of possible base
        is defined. In the case of multi-class evaluation, please be sure that 
        the corresponding class values are handled by the machine learning 
        algorithm that you plan to use. These are the allowed types in WEKA's 
        arff file format. 
    """

######################################################################

    def __init__( self, name, feat_type, xml_class="metatpclass" ) :
        """
            @param name String that identifies the corresponding `Feature`.

            @param feat_type The type of the corresponding `Feature`'s
            `value`field.  This type can be an "integer", a "real" number,
            a "string" or an element of an enumeration (allowed types in WEKA).

            @param xml_class String that identifies what kind of meta-feature
            this is.  Subclasses MUST use a unique name.
        """
        super(MetaTPClass, self).__init__(name, feat_type, xml_class)

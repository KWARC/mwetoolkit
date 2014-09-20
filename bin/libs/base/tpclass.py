#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# tpclass.py is part of mwetoolkit
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
    This module provides the `TPClass` class. This class represents a True
    Positive judgment of a candidate, i.e. the evaluation of a candidate with
    respect to a reference, that can be a machine-readable gold standard 
    (automatic evaluation) or a human judge (manual evaluation).
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.base.feature import Feature

################################################################################

class TPClass( Feature ) :
    """
        A `TPClass` is a True Positive class of a candidate according to some
        reference, be it a machine-readable gold standard (automatic evaluation) 
        or a human judge (manual evaluation). TPClass extends `Feature`, so the 
        name corresponds to the name that identifies the gold standard, 
        reference list or human judge from which the TP evaluation class was 
        generated while value is taken from a set of possible judgements, e.g.
        True or False if the evaluation is 2-class. The value should conform to
        the `MetaTPClass` defined in the `Meta` header of the XML file, e.g. if
        the meta-TP class allows three base "{c1,c2,c3}", the value should
        equal one of these three values. If you use multi-class evaluation, 
        please be sure that the machine learning algorithm that you are going
        to use does support multi-class classification.
    """

################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <tpclass> with its 
            attributes, according to mwetoolkit-candidates.dtd.
        """
        return "<tpclass name=\"" + self.name + \
               "\" value=\"" + str(self.value) + "\" />"
        
################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod() 

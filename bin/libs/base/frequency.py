#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# frequency.py is part of mwetoolkit
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
    This module provides the `Frequency` class. This class represents a 
    frequency of occurrences of an element in a corpus, i.e. an integer for the
    number of times the element (word or ngram) appears in the corpus.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.base.feature import Feature
from xml.sax.saxutils import quoteattr

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
            attributes, according to mwetoolkit-candidates.dtd.
        """
        return "<freq name=" + quoteattr(self.name) + \
               " value=" + quoteattr(str(self.value)) + " />"
        
################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()   

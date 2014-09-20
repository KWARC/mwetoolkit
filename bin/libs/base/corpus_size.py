#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# corpus_size.py is part of mwetoolkit
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
    This module provides the CorpusSize class. This class is a representation of 
    a meta-information about the number of tokens in a given corpus.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.base.feature import Feature

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
            attributes, according to mwetoolkit-candidates.dtd.
        """
        return "<corpussize name=\"" + self.name + \
               "\" value=\"" + str(self.value) + "\" />"
        
################################################################################

if __name__ == "__main__" :
    import doctest
    doctest.testmod()

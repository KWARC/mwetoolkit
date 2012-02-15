#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# candidatesDTDHandler.py is part of mwetoolkit
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
    This package provides a set of XML handlers that convert the XML entities
    into Object Oriented representations that are used by mwetoolkit's scripts. 
    The classes provided in this package correspond to the DTDs that define
    mwetoolkit's intermediary XML formats:
    
    `CandidatesXMLHandler` - SAX parser for XML documents that are valid 
    candidate lists according to mwetoolkit-candidates.dtd.
    
    `CorpusXMLHandler` - SAX parser for XML documents that are valid corpora 
    according to mwetoolkit-corpus.dtd.
    
    `DictXMLHandler` - SAX parser for XML documents that are valid pattern
    or reference lists according to mwetoolkit-dict.dtd.

    `GenericXMLHandler` - SAX parser for the three XML document types handled by
    the classes described above. Treats all entities as special types of Ngrams,
    achieving uniform treatment for all files.
"""

import install

#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# __common.py is part of mwetoolkit
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
    Internal options and common configuration parameters and options for 
    mwetoolkit.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import os

################################################################################

"""
    Two-letters language code of the working corpus. This information will not
    be used by mwetoolkit, but it is important for searching the correct
    language pages in Yahoo's and Google's indices.
"""
DEFAULT_LANG = "en"

"""
    Maximum number of days that a Web result might stay in the cache file. A 
    negative value means that there is no expiration date for cache entries. If 
    you set this parameter to zero, no cache will be used. Note that expired 
    cache entries will be searched again and will count as a search for the 
    daily limit of 5000 searches.
"""
MAX_CACHE_DAYS = -1

"""
    Application ID to be used with Yahoo Web Search API (see specific doc. for
    more details)
"""
YAHOO_APPID = "ngram001"


"""
    Path to the C indexer program. The default value should work.
"""
C_INDEXER_PROGRAM = os.path.dirname(__file__) + "/../../c-indexer"

# Internal options below (do not modify unless you know what you are doing)

"""
    Name of the cache file where mwetoolkit keeps recent Web queries to speed up
    the process.
"""
YAHOO_CACHE_FILENAME = "yahoo_cache.dat"
GOOGLE_CACHE_FILENAME = "google_cache.dat"

"""
    Characters internally used as attribute and word separators.
    Must not appear in the corpus, neither as a word, nor as POS tag etc!
    The probability is minimal but it is nevertheless important to warn you
    about it! Each separator must be a single character.
"""
WILDCARD = "\36"             # ASCII level 3 separator
ATTRIBUTE_SEPARATOR = "\35"  # ASCII level 2 separator
WORD_SEPARATOR = "\34"       # ASCII level 1 separator
SEPARATOR = ATTRIBUTE_SEPARATOR

"""
    The prefix of the name of a temporary file
"""
TEMP_PREFIX = "mwetk_"

"""
    Existing folder where the toolkit keeps temporary files. Default in Linux
"""
TEMP_FOLDER = "/tmp"

"""
    Should not be a token of the corpus neither a POS tag! The probability is 
    minimal but it is nevertheless important to warn you about it!
"""
INDEX_NAME_KEY = "___index_name___"

"""
    Should not be a token of the corpus neither a POS tag! The probability is 
    minimal but it is nevertheless important to warn you about it!
"""
CORPUS_SIZE_KEY = "___corpus_size___"

"""
    Unknown feature value is represented by quote mark in WEKA's arff file 
    format
"""
UNKNOWN_FEAT_VALUE = "?"

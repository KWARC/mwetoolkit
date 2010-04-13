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
    INTERNAL OPTIONS (Do not modify unless you know what you are doing)
"""

# Some internal parameters are taken from config file. They're actually external
# parameters but for transparency, everything is grouped in the __common.py 
# file.
import config

LANG = config.LANG

MAX_CACHE_DAYS = config.MAX_CACHE_DAYS

WILDCARD = config.WILDCARD

YAHOO_APPID = config.YAHOO_APPID

YAHOO_WS_PATH = config.YAHOO_WS_PATH

MAX_MEM = config.MAX_MEM

# Name of the cache file where mwetoolkit keeps recent Web queries to speed up
# the process.
YAHOO_CACHE_FILENAME = LANG + "_yahoo_cache.dat"
GOOGLE_CACHE_FILENAME = LANG + "_google_cache.dat"

# Should not be a token of the corpus neither a POS tag! The probability is 
# minimal but it is nevertheless important to warn you about it!
SEPARATOR = "#S#"

# Should not be a token of the corpus neither a POS tag! The probability is 
# minimal but it is nevertheless important to warn you about it!
WORD_SEPARATOR = "#WS#"

# A temporary file
TEMP_PREFIX = "mwetk_"

# Existing folder where the toolkit keeps temporary files
TEMP_FOLDER = "/tmp"

# Should not be a token of the corpus neither a POS tag! The probability is 
# minimal but it is nevertheless important to warn you about it!
INDEX_NAME_KEY = "___index_name___"

# Should not be a token of the corpus neither a POS tag! The probability is 
# minimal but it is nevertheless important to warn you about it!
CORPUS_SIZE_KEY = "___corpus_size___"

# Unknown feature value is represented by quote mark in WEKA's arff file format
UNKNOWN_FEAT_VALUE = "?"



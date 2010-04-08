#!/usr/bin/python
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

# Name of the cache file where mwttoolkit keeps recent Web queries to speed up 
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
TEMP_PREFIX = "mwt_"

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



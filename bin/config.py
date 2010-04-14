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
    Common configuration parameters and options for mwttoolkit.
"""


"""
    Two-letters language code of the working corpus. This information will not
    be used by mwttoolkit, but it is important for searching the correct 
    language pages in Yahoo's index.
"""
LANG = "en"

"""
    Maximum number of days that a Web result might stay in the cache file. A 
    negative value means that there is no expiration date for cache entries. If 
    you set this parameter to zero, no cache will be used. Note that expired 
    cache entries will be searched again and will count as a search for the 
    daily limit of 5000 searches.
"""
MAX_CACHE_DAYS = -1

"""
    Wildcard for MWT patterns. Please chose a token that is not in the corpus as 
    a token.
"""
WILDCARD = "*"

"""
    Application ID to be used with Yahoo Web Search API (see specific doc. for
    more details)
"""
YAHOO_APPID = "ngram001"

"""
    Path to the "yahoo" folder containing the python API for accessing Yahoo
    search services.
    TODO: remove this dependency
"""
YAHOO_WS_PATH = "/home/ceramisch/Work/tools/yahoo/lib/yws-2.01/Python/pYsearch-2.0/"

"""
    Maximum amount of RAM memory that the corpus index should use. If you have a
    very powerful computer, consider augmenting this number in order to use all
    its capacity, since it speeds up the work with very large corpora. However,
    if your resources are limited and/or your corpus is small, leave this with
    a reasonable value. The memory amount is expressed in Megabytes (MB).
"""
MAX_MEM = 1000 # ~1GB

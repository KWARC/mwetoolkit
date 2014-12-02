#!/usr/bin/python
# -*- coding:UTF-8 -*-

# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011
# THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API, APRIL 2011

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# yahooFreq.py is part of mwetoolkit
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
    This module provides the `YahooFreq` class. This class represents an 
    abstract gateway that allows you to access the Yahoo search index and look 
    up for the number of Web pages that contain a certain word or ngram.
    
    THIS MODULE IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import urllib
import json as simplejson

from libs.base.webFreq import WebFreq
from libs.base.__common import YAHOO_CACHE_FILENAME, YAHOO_APPID


################################################################################         

class YahooFreq( WebFreq ):
    """
        The `YahooFreq` class is an abstraction that allows you to call Yahoo
        Web Service search to estimate the frequency of a certain search term
        in the Web, in terms of pages that contain that term (a term not in the
        sense of Terminology, but in the sense of word or ngram, i.e. an 
        Information Retrieval term). After instanciated, you should call the
        `search_frequency` function to obtain these estimators for a given
        term.
    """

################################################################################          

    def __init__( self, cache_filename=None ) :
        """
            Instanciates a connection to the Yahoo Web Search service. This
            object is a gate through which you can estimate the number of time
            a given element (word or ngram) appears in the Web. A cache 
            mechanism does automatically manage repeated queries.
            
            @param cache_filename The string corresponding to the name of the
            cache file in/from which you would like to store/retrieve recent
            queries. If you do not provide a file name, it will be automatically
            chosen by the class (yahoo_cache.dat or something like this). You
            should have write permission in the current directory in order to
            create and update the cache file.
            
            @return A new instance of the `YahooFreq` service abstraction.
        """
        #### CACHE MECHANISM ####
        if not cache_filename :
            cache_filename = YAHOO_CACHE_FILENAME
        url = ('http://search.yahooapis.com/WebSearchService/V1/webSearch?' +
                    urllib.urlencode( { "results": "0",
                                        "appid": YAHOO_APPID,
                                        "query": "QUERYPLACEHOLDER",
                                        "output": "json",
                                        "language" : "LANGPLACEHOLDER",
                                        "type" : "phrase" } ) )
        super( YahooFreq, self ).__init__( cache_filename=cache_filename,
                                           url=url, 
                                           post_data={},
                                           treat_result=self.treat_result )
            
################################################################################           

    def treat_result( self, response_string ) :
        """
            
        """ 
        # This is an ugly workarround, but it's necessary because
        # sometimes yahoo returns weird unicode characters in the
        # results, and we're totally not interested in weird unicode
        # CORRECTING: This workarround works with yahoo but it doesn't with 
        # google. What do I do? Probably, comment the line whenever I have a
        # problem and uncomment it back if it's already commented out. But 
        # before I surrender to this ugly solution, I'll try with this 
        # "encoding" parameter. Let's hope this never bugs again!
        #response_string = response_string.replace("\\","XX")
        results = simplejson.loads( response_string, encoding="UTF-8" )           
        return int( results[ "ResultSet" ][ "totalResultsAvailable" ] )

################################################################################                   
    
    def corpus_size( self ) :
        """
            Returns the approximate size of the World Wide Web in number of 
            pages. This estimation considers data available from 
            www.worldwidewebsize.com. It was of ~50 billion pages at Oct. 29 
            2009.
            
            @return An integer corresponding to an estimation of the number of
            pages in the World Wide Web.
        """
        return 50000000000 # AROUND 50 BILLION PAGES 29/10/2009

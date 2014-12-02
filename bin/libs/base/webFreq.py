#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# webFreq.py is part of mwetoolkit
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
    This module provides the `WebFreq` class. This class represents an
    abstract gateway that allows you to access the a web search index and look
    up for the number of web pages that contain a certain word or ngram.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import cPickle # Cache is pickled to/from a file
from datetime import date
import urllib2
import urllib
import time

from libs.base.__common import MAX_CACHE_DAYS, DEFAULT_LANG

################################################################################

class WebFreq( object ) :
    """
        The `WebFreq` class is an abstraction that allows you to call a search
        engine Web Service search to estimate the frequency of a certain search
        term in the Web, in terms of pages that contain that term (a term not in
        the sense of Terminology, but in the sense of word or ngram, i.e. an
        Information Retrieval term). After instanciated, you should call the
        `search_frequency` function to obtain these estimators for a given
        term. This class should not be used directly, but through the subclasses
        `YahooFreq`, `GoogleFreq` and `GoogleFreqUniv`.
        
        N.B.: Yahoo is not supported anymore, after August 2011.
    """

################################################################################

    def __init__(self, cache_filename, url, post_data, treat_result):
        """
            Instanciates a connection to the a Web Search service. This object
            is a gate through which you can estimate the number of times a given
            element (word or ngram) appears in the Web. A cache mechanism does
            automatically manage repeated queries. The additional parameters
            will be used to chose a search engine (currently, Google and Yahoo
            are supported)
            N.B.: Yahoo is not supported anymore, after August 2011.

            @param cache_filename The string corresonding to the name of the
            cache file in/from which you would like to store/retrieve recent
            queries. You should have write permission in the current directory
            in order to create and update the cache file.

            @param url The URL of the web service that allows access to the
            search engine index. The URL is generally in the provider's
            documentation.

            @param post_data Some providers like google ask for special fields
            to be sent as post data to identify the user.

            @param treat_result A callback function that will treat the result
            of the search engine query. Since Google and Yahoo differ in the
            format of the answer (names and structure of fields in json format),
            it is necessary to personalise the treatment. The callback should
            receive a json dictionary and return an integer.

            @return A new instance of the `WebFreq` service abstraction.
        """
        self.url = url
        self.post_data = post_data
        self.treat_result = treat_result
        self.cache_filename = cache_filename
        #### CACHE MECHANISM ####
        self.MAX_DAYS = MAX_CACHE_DAYS
        self.today = date.today()
        try :
            cache_file = open( self.cache_filename, "r" )
            self.cache = cPickle.load( cache_file )
            cache_file.close()
        except IOError :
            cache_file = open( self.cache_filename, "w" )
            cache_file.close()
            self.cache = {}

################################################################################

    def send_query( self, lang, search_term ):
        """
            Sends the query to the search engine by replacing the placeholders
            in the template url and creating a new request through urllib2.
            
            @param lang The language code of the search
            
            @param search_term The search term corresponding to the query. The
            search term must be quoted if you want an exact search. The search
            term should not be escaped, this is done inside this function.
            
            @return The integer corresponding to the frequency of the query term
            in the web according to that search engine
        """
        url = self.url.replace( "LANGPLACEHOLDER",lang )
        url = url.replace( "QUERYPLACEHOLDER", urllib.quote_plus( search_term ))
        request = urllib2.Request( url, None, self.post_data )
        response = urllib2.urlopen( request )
        response_string = response.read()
        return self.treat_result( response_string )

################################################################################

    def search_frequency( self, in_term, lang=None ) :
        """
            Searches for the number of Web pages in which a given `in_term`
            occurs, according to a search index. The search is case insensitive
            and language-dependent, please remind to define the correct
            `DEFAULT_LANG` parameter in the `config.py` file or to provide it as
            an argument. If the frequency of the `in_term` is still in cache and
            the cache entry is not expired, no Web query is performed. Since
            each query can take up to 3 or 4 seconds, depending on your Internet
            connection, cache is very important. Please remind to define the
            correct `MAX_CACHE_DAYS` parameter in the `config.py` file,
            according to the number of queries you would like to perform.

            @param in_term The string corresponding to the searched word or
            ngram. If a sequence of words is searched, they should be separated
            by spaces as in a Web search engine query. The query is also
            performed as an exact term query, i.e. with quote marks around the
            terms. You can use the `WILDCARD` to replace a whole word, since
            search engines provides wildcarded query support.

            @param lang Two-letter code of the language of the web pages the
            search engine should consider. Making language-independent queries
            does not seem a good idea since the counters will be overestimated.

            @return An integer corresponding to an approximation of the number
            of Web pages that contain the serached `in_term`. This frequency
            approximation can estimate the number of times the term occurs if
            you consider the Web as a corpus.
        """
        term = in_term.lower().strip()
        if not lang :
            lang = DEFAULT_LANG
        # Look into the cache
        try :
            ( freq, time_searched ) = self.cache[ lang + "___" + term ]
            dayspassed = self.today - time_searched
            if dayspassed.days >= self.MAX_DAYS and self.MAX_DAYS >= 0 :
                raise KeyError # TTL expired, must search again :-(
            else :
                return freq # TTL not expired :-)
        except KeyError :
            search_term = term
            if isinstance( search_term, unicode ) :
                search_term = search_term.encode( 'utf-8' )
            search_term = "\"" + search_term + "\""
            tries = 0
            max_tries = 5
            result_count = None
            while result_count is None :
                try:
                    tries = tries + 1
                    result_count = self.send_query( lang, search_term )
                    if result_count is None :
                        raise Exception("Result was None")
                except urllib2.HTTPError as err:
                    print( "Got an error ->" + str( err ), file=sys.stderr)
                    if tries < max_tries :
                        print("Will retry in 30s...", file=sys.stderr)
                        time.sleep( 30 )
                        #result_count = None
                    else :
                        print("Stopped at search term: " + search_term,
                              file=sys.stderr)
                        #print >> sys.stderr, request.get_full_url()
                        if err.code == 403 : #Forbidden
                            print("Probably your ID for the Google university "
                                  "research program is not correct or is "
                                  "associated to another IP address",
                                  file=sys.stderr)
                            print("Check \"http://research.google.com/"
                                  "university/search/\" for further "
                                  "information",file=sys.stderr)
                        print("PLEASE VERIFY YOUR INTERNET CONNECTION",
                              file=sys.stderr)
                        sys.exit( -1 )
            
            self.cache[ lang + "___" + term ] = ( result_count, self.today )
            return result_count

################################################################################

    def flush_cache( self ) :
        """
            Explicit destructor, flushes the cache content to a file before
            closing the connection. Thus, the cache entries will be available
            the next time the search engine is called and, if they are not
            expired, will avoid repeated queries.

            IMPORTANT: If you want the cache mechanism to be used properly,
            NEVER FORGET to call this function in a "finally" block, in order
            to guarantee that, even if an exceptioon occurs (like pressing
            Ctrl+C), the cache will be flushed.
        """
        # Flush cache content to file
        cache_file = open( self.cache_filename, "w" )
        cPickle.dump( self.cache, cache_file )
        cache_file.close()

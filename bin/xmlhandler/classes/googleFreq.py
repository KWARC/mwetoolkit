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
    This module provides the `YahooFreq` class. This class represents an 
    abstract gateway that allows you to access the Yahoo search index and look 
    up for the number of Web pages that contain a certain word or ngram.
"""

import sys
import cPickle # Cache is pickled to/from a file
from datetime import date
import urllib2
import urllib
import simplejson

from __common import GOOGLE_CACHE_FILENAME, MAX_CACHE_DAYS, LANG

################################################################################         

class GoogleFreq :
    """
        The `GoogleFreq` class is an abstraction that allows you to call Google
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
            Instanciates a connection to the Google Web Search service. This
            object is a gate through which you can estimate the number of time
            a given element (word or ngram) appears in the Web. A cache 
            mechanism does automatically manage repeated queries.
            
            @param cache_file The string corresonding to the name of the cache 
            file in/from which you would like to store/retrieve recent queries. 
            If you do not provide a file name, it will be automatically chosen 
            by the class (google_cache.dat or something like this). You should 
            have write permission in the current directory in order to create
            and update the cache file.
            
            @return A new instance of the `GoogleFreq` service abstraction.
        """
  
        #### CACHE MECHANISM ####
        if cache_filename :
            self.CACHE_FILENAME = cache_filename
        else :
            self.CACHE_FILENAME = GOOGLE_CACHE_FILENAME
        self.MAX_DAYS = MAX_CACHE_DAYS 
        self.today = date.today()
        try :
            cache_file = open( self.CACHE_FILENAME, "r" )
            self.cache = cPickle.load( cache_file )
            cache_file.close()
        except IOError :            
            cache_file = open( self.CACHE_FILENAME, "w" )
            cache_file.close()
            self.cache = {}
            
################################################################################           

    def search_frequency( self, in_term ) : 
        """
            Searches for the number of Web pages in which a given `in_term`
            occurs, according to Google's search index. The search is case 
            insensitive and language-dependent, please remind to define the
            correct `LANG` parameter in the `config.py` file. If the frequency
            of the `in_term` is still in cache and the cache entry is not
            expired, no Web query is performed. Since each query can take up to
            3 or 4 seconds, depending on your Internet connection, cache is
            very important. Please remind to define the correct `MAX_CACHE_DAYS` 
            parameter in the `config.py` file, according to the number of 
            queries you would like to perform.
            
            @param in_term The string corresponding to the searched word or
            ngram. If a sequence of words is searched, they should be separated 
            by spaces as in a Web search engine query. The query is also 
            performed as an exact term query, i.e. with quote marks around the
            terms. You can use the `WILDCARD` to replace a whole word, since
            Yahoo provides wildcarded query support.
            
            @return An integer corresponding to an approximation of the number
            of Web pages that contain the serached `in_term`. This frequency
            approximation can estimate the number of times the term occurs if 
            you consider the Web as a corpus.
        """   
        term = in_term.lower().strip()
        # Look into the cache        
        try :
            ( freq, time ) = self.cache[ term ]
            dayspassed = self.today - time
            if dayspassed.days >= self.MAX_DAYS and self.MAX_DAYS >= 0 :                
                raise KeyError # TTL expired, must search again :-(
            else :
                return freq # TTL not expired :-)
        except KeyError :  
        # Only instanciate self.search when needed. That way, it also works when
        # everything is in cache and you have no Internet.
            search_term = term
            if isinstance( search_term, unicode ) :
                search_term = search_term.encode( 'utf-8' )
            search_term = "\"" + search_term + "\""           
            try:
                url = ('http://ajax.googleapis.com/ajax/services/search/web?' +\
                        urllib.urlencode({"rsz": "small", "v": "1.0", 
                                          "q": search_term, "lr": "lang_" + LANG, 
                                          "hl": LANG } ) )
                request = urllib2.Request( url, None, {'Referer': 'www.inf.ufrgs.br/~ceramisch'})
                response = urllib2.urlopen(request)
                results = simplejson.load(response)
                if results[ "responseData" ][ "results" ] :
                    resultCount = int( results[ "responseData" ][ "cursor" ] \
                                              [ "estimatedResultCount" ] )
                else :
                    resultCount = 0
            except Exception, err:
                print >> sys.stderr, "Got an error ->", err 
                print >> sys.stderr, "PLEASE VERIFY YOUR INTERNET CONNECTION"               
                sys.exit( -1 )                
            self.cache[ term ] = ( resultCount, self.today )
            return resultCount
            
################################################################################                   
    
    def corpus_size( self ) :
        """
            Returns the approximate size of the World Wide Web in number of 
            pages. This estimation considers data available from 
            www.worldwidewebsize.com. It was of ~14 billion pages at Jan. 20, 
            2010
            
            @return An integer corresponding to an estimation of the number of
            pages in the World Wide Web.
        """
        return 14000000000 # AROUND 14 BILLION PAGES 20/Jan/2010
             
################################################################################                   
        
    def __del__( self ) :
        """
            Class destructor, flushes the cache content to a file before closing
            the connection. Thus, the cache entries will be available the next 
            time Yahoo is called and, if they are not expired, will avoid 
            repeated queries.
        """
        # Flush cache content to file
        cache_file = open( self.CACHE_FILENAME, "w" )
        cPickle.dump( self.cache, cache_file )
        cache_file.close()
        
################################################################################                
            
if __name__ == "__main__" :
    import doctest
    doctest.testmod()       



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

from __common import YAHOO_CACHE_FILENAME, MAX_CACHE_DAYS, YAHOO_APPID, \
                       LANG, YAHOO_WS_PATH

# Appends the path to Yahoo WS service to the "import" path
sys.path.append( YAHOO_WS_PATH )

# Now that I know where I can find Yahoo's API, I can import it :-)
from yahoo.search import factory

################################################################################         

class YahooFreq :
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
            
            @param cache_file The string corresonding to the name of the cache 
            file in/from which you would like to store/retrieve recent queries. 
            If you do not provide a file name, it will be automatically chosen 
            by the class (yahoo_cache.dat or something like this). You should 
            have write permission in the current directory in order to create
            and update the cache file.
            
            @return A new instance of the `YahooFreq` service abstraction.
        """
        # self.search will be instanciated (if needed) to contain the access to
        # yahoo web services.
        self.search = None
        #### CACHE MECHANISM ####
        if cache_filename :
            self.CACHE_FILENAME = cache_filename
        else :
            self.CACHE_FILENAME = YAHOO_CACHE_FILENAME
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
            occurs, according to Yahoo's search index. The search is case 
            insensitive and language-dependent, please remind to define the
            correct `LANG` parameter in the `config.py` file. If the frequency
            of the `in_term` is still in cache and the cache entry is not
            expired, no Web query is performed. Since each query can take up to
            3 or 4 seconds, depending on your Internet connection, cache is
            very important. Moreover, Yahoo limits its free Web Service to
            5,000 queries per day per IP address, so a very big list of 
            candidates could take a lot more time to be processed if no cache 
            was available. Please remind to define the correct `MAX_CACHE_DAYS` 
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
            if not self.search :            
                self.__start_search() 
            search_term = term
            if isinstance( search_term, unicode ) :
                search_term = search_term.encode( 'utf-8' )
            self.search.query = "\"" + search_term + "\""           
            try:
                results = self.search.parse_results()
            except Exception, err:
                print >> sys.stderr, "Got an error ->", err 
                print >> sys.stderr, "PLEASE VERIFY YOUR INTERNET CONNECTION"               
                sys.exit( -1 )                
            self.cache[ term ] = ( results.total_results_available, self.today )
            return results.total_results_available
            
################################################################################                             

    def __start_search( self ) :
        """
            Internal function that starts the Yahoo Web Service class. This 
            class is a part of the python API provided by Yahoo. This function
            also sets initial parameters such as application ID and query 
            language. The result is stored into an instance variable and can
            be subsequently used to query Yahoo's index.
        """
        try :
            self.search = factory.create_search( "Web", YAHOO_APPID )        
        except ValueError:
            print >> sys.stderr, "AppID can only contain a-zA-Z" + \
                                 "0-9 _()[]*+-=,.:\@, 8-40 characters"
            sys.exit( -1 )
        self.search.language = LANG
        self.search.results = 0
        self.search.start = 1   

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

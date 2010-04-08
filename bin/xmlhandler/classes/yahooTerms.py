#!/usr/bin/python
"""
"""

import sys
import pdb
import urllib2
import urllib
import simplejson

from __common import LANG, YAHOO_APPID

################################################################################         

class YahooTerms :
    """       
    """

################################################################################          

    def __init__( self, cache_filename=None ) :
        """           
        """
        pass
                   
################################################################################           

    def search_terms( self, in_text, query ) : 
        """            
        """   
        if LANG != "en" :
            print >> sys.err, "WARNING: Yahoo terms only works for English"        
        input_text = in_text.strip()
        if isinstance( input_text, unicode ) :
            input_text = input_text.encode( 'utf-8' )
        try:
            url = ('http://search.yahooapis.com/ContentAnalysisService/V1/termExtraction' )           
            post_data = urllib.urlencode( { "context": input_text, \
                                            "appid": YAHOO_APPID, \
                                            "query": query, \
                                            "output": "json" } ) 
            request = urllib2.Request( url, post_data )
            response = urllib2.urlopen(request)
            results = simplejson.load(response)
            return results[ "ResultSet" ][ "Result" ]
            
        except Exception, err:
            print >> sys.stderr, "Got an error ->", err 
            print >> sys.stderr, "PLEASE VERIFY YOUR INTERNET CONNECTION"               
            sys.exit( -1 )          
           
################################################################################                   
 
    def __del__( self ) :
        """          
        """
        pass
        
################################################################################                
            
if __name__ == "__main__" :
    import doctest
    doctest.testmod()       



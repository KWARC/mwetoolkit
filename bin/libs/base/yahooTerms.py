#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# yahooTerms.py is part of mwetoolkit
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
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import urllib2
import urllib
import json as simplejson

from libs.base.__common import DEFAULT_LANG, YAHOO_APPID
from libs.util import error

################################################################################         

class YahooTerms :
    """
        Representation of an abstract gateway that allows you to access the
        Yahoo terms service and look up for the terms identified in a text
        fragment.
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
        if DEFAULT_LANG != "en" :
            print("WARNING: Yahoo terms only works for English",file=sys.stderr)
        input_text = in_text.strip()
        if isinstance( input_text, unicode ) :
            input_text = input_text.encode( 'utf-8' )
        try:
            url = ('http://search.yahooapis.com/ContentAnalysisService/'
                   'V1/termExtraction' )
            post_data = urllib.urlencode( { "context": input_text,
                                            "appid": YAHOO_APPID,
                                            "query": query,
                                            "output": "json" } ) 
            request = urllib2.Request( url, post_data )
            response = urllib2.urlopen(request)
            results = simplejson.load(response)
            return results[ "ResultSet" ][ "Result" ]
            
        except Exception as err:
            error( "Got an error ->" + str(err) +
                   "\nPLEASE VERIFY YOUR INTERNET CONNECTION")
        
################################################################################                
            
if __name__ == "__main__" :
    import doctest
    doctest.testmod()       

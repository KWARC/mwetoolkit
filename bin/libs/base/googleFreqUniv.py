#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# googleFreqUniv.py is part of mwetoolkit
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
    This module provides the `GoogleFreqUniv` class. This class represents an 
    abstract gateway that allows you to access the Google search index and look 
    up for the number of Web pages that contain a certain word or ngram.
"""

import urllib
import xml.dom.minidom

from __common import GOOGLE_CACHE_FILENAME
import webFreq


################################################################################         

class GoogleFreqUniv( webFreq.WebFreq ) :
    """
        The `GoogleFreqUniv` class is an abstraction that allows you to call 
        Google Web Service search to estimate the frequency of a certain search 
        term in the Web, in terms of pages that contain that term (a term not in 
        the sense of Terminology, but in the sense of word or ngram, i.e. an 
        Information Retrieval term). After instanciated, you should call the
        `search_frequency` function to obtain these estimators for a given
        term. 
        
        This class only works with a valid registered Google Research University
        Program ID and when the script is called from the computer whose IP 
        address is assigned to the ID. If you do not have this ID, use regular
        Google search class `GoogleFreq` bounded by a daily usage quota.
    """

################################################################################          

    def __init__( self, google_id, cache_filename=None ) :
        """
            Instanciates a connection to the Google Web Search service. This
            object is a gate through which you can estimate the number of time
            a given element (word or ngram) appears in the Web. A cache 
            mechanism does automatically manage repeated queries.
            
            @param google_id This is the ID you receive from Google when you 
            register to the Google Search University Research Program. More
            information about it can be found at :
            http://research.google.com/university/search/
            Please remind that the ID only works with the registered IP address.
            
            @param cache_file The string corresonding to the name of the cache 
            file in/from which you would like to store/retrieve recent queries. 
            If you do not provide a file name, it will be automatically chosen 
            by the class (google_cache.dat or something like this). You should 
            have write permission in the current directory in order to create
            and update the cache file.
            
            @return A new instance of the `GoogleFreq` service abstraction.
        """
  
        #### CACHE MECHANISM ####
        url = ('https://research.google.com/university/search/service?' +\
                        urllib.urlencode({"rsz": "small",
                                          "q": "QUERYPLACEHOLDER",
                                          "lr": "LANGPLACEHOLDER",
                                          "start" : "0",
                                          "clid": google_id } ) )
        post_data = {'Referer': 'sourceforge.net/projects/mwetoolkit'}
        if not cache_filename :
            cache_filename = GOOGLE_CACHE_FILENAME
        super( GoogleFreqUniv, self ).__init__( cache_filename, url, post_data,\
                                                self.treat_result )
            
################################################################################           

    def gettext( self, node ):
      """
        Extract the contents of a xml.dom.Nodelist as a string.
        
        @param node An xml.dom.Node instance

        @return A string containing the contents of all node.TEXT_NODE instances
        
        N.B. This function is a copy of Google's example code.
      """
      text = []
      for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE:
          text.append( child.data )
      return ''.join( text )

################################################################################           

    def treat_result( self, results ) :
        """
            Parses the small XML file returned by google API and returns only
            the integer corresponding to the total number of documents returned
            by that query.
            
            @param results XML string containing the whole result set of the 
            query
            
            @return An integer corresponding to the number of total estimated
            results of the query
        """
        dom_results = xml.dom.minidom.parseString( results )
        res_elements = dom_results.getElementsByTagName( 'RES' )
        if len( res_elements ) == 0 :
            return 0
        else :
            res_first = res_elements[ 0 ]        
        total = self.gettext( res_first.getElementsByTagName( 'M' )[ 0 ] )
        return int( total )
            
################################################################################                   
     
    def corpus_size( self ) :
        """
            Returns the approximate size of the World Wide Web in number of 
            pages. This estimation considers data available from 
            www.worldwidewebsize.com. It was of ~52 billion pages at Feb. 24, 
            2012
            
            @return An integer corresponding to an estimation of the number of
            pages in the World Wide Web.
        """
        return 52000000000 # AROUND 52 BILLION PAGES 24/Feb/2012

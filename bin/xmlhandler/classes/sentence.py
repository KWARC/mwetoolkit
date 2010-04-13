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
    This module provides the `Sentence` class. This class represents a sentence, 
    i.e. a sequence of words that convey a complete information, as they occur 
    in the corpus. You are expected to use this class to represent objects that
    are linguistically motivated sentences, not simply ngrams.
"""

from ngram import Ngram

################################################################################

class Sentence( Ngram ) :
    """
        A `Sentence` is a representation of a sequence of words as they appear 
        in a given corpus (mwetoolkit-corpus.dtd). It is a subclass of `Ngram`,
        meaning that it is not more than a sequence of words, with the particu-
        larity that they are linguistic units that convey a complete 
        information and generally end with a punctuation sign. However, no test
        is performed in order to verify whether the sentence is well-formed,
        grammatically or semantically correct. This means that if you 
        append words that do not make sense to the sentence (e.g. "the of going 
        never"), it is basically your problem.
    """
    
################################################################################

    def __init__( self, word_list, s_id ) :
        """
            Instanciates a new sentence from a list of words. A sentence has a
            list of adjacent words and an integer unique identifier. If the 
            sentence ends with a punctuation sign, it should be included as the
            last token of the list. Inermediary punctuation signs such as commas
            and parentheses should also be considered as separate tokens, please
            pay attention to correctly tokenise your corpus before using 
            mwetoolkit.
            
            @param word_list A list of `Word`s in the same order as they occur
            in the sentence in the corpus.
            
            @param s_id An integer identifier that uniquely describes the 
            current sentence.
            
            @return A new instance of a `Sentence`
        """
        self.word_list = word_list
        self.s_id = s_id
        self.freqs = None
        
################################################################################
        
    def to_surface( self ) :
        """
            Returns a simple readable string where the surface forms of the 
            current sentence are concatenated and separated by a single space.
            Used only for debug.
            
            @return A string with the surface form of the sentence, 
            space-separated.
        """
        result = ""
        for word in self.word_list :
            result = result  + word.surface + " "
        return result.strip()   
             
################################################################################
        
    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <s> with its 
            internal structure and attributes, according to 
            mwetoolkit-corpus.dtd.
        """
        result = "<s"
        if( self.s_id >= 0 ) :
            result += " s_id=\"" + str( self.s_id ) + "\">"
        else :
            result += ">"
        for word in self.word_list :
            result = result  + word.to_xml() + " "
        result += "</s>"
        return result.strip()

################################################################################

    def get_ngrams( self, n ) :
        """
            Returns all the `Ngram`s of size `n` in the current sentence. For 
            example, if n=1 and the sentence has m words, returns a list of m 
            ngrams containing one `Word`, i.e. all words of the sentence. If 
            n=2, will return a list with m - 1 bigrams. In the general case of 
            n <= m, returns a list of m - n + 1 ngrams. Please notice that only
            adjacent words are considered. For instance, if the sentence is 
            something like "The man is in the house", valid bigrams are "The 
            man", "man is", "is in", "in the" and "the house", but NOT "The is"
            or "in house", and so on. If there are two identical ngrams, they
            will be returned as separate objects. The `Ngram`s are generated in
            the order in which they occur in the sentence.
            
            @param n An integer representing the size (i.e. number of words) of 
            the ngrams to extract. The value of n should be lower or equal to 
            the number of words in the sentence, otherwise an empty list is 
            returned. 
            
            @return A list of `Ngram`s corresponding to the substrings of the
            sentence that contain `n` words. Notice that we extract substrings
            (i.e. adjacent words) and not subsequences (i.e. possibly gapped).
        """
        ngrams = []
        m = len( self.word_list )
        if n <= m :
            for i in range( m - n + 1 ) :
                ngrams.append( Ngram( self.word_list[ i : i+n ], [] ) )
        return ngrams
        
################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  

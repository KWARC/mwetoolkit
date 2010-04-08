#!/usr/bin/python
"""
    This module provides the `Pattern` class. This class represents a ngram 
    pattern, i.e. a sequence of words (or word patterns) as they occur in the 
    pattern or reference lists (as in mwttoolkit-patterns.dtd).
"""

from ngram import Ngram

################################################################################

class Pattern( Ngram ) :
    """
        A pattern is a sequence of words that express a constraint on another
        ngram. The class `Pattern` extends `Ngram`, so both contain lists of
        `Word`s. However, a pattern is intended to match against other ngrams,
        so its words have probably `WILDCARD`s to express undefined constraints.
        The `freqs` list of a Pattern is not used.
    """

################################################################################

    def match( self, some_ngram ) :
        """
            A simple matching algorithm that returns true if ALL the words of
            the current pattern match all the words of the given ngram. Since a 
            pattern does generally contain `WILDCARD`s to express loose
            constraints, the matching is done at the word level considering only
            the parts that are defined, for example, POS tags for candidate
            extraction or lemmas for automatic gold standard evaluation.
            
            @param some_ngram A `Ngram` against which we would like to compare
            the current pattern. In general, the pattern contains the 
            `WILDCARD`s while `some_ngram` has all the elements with a defined
            value.
            
            @return Will return True if ALL the words of `some_ngram` match ALL
            the words of the current pattern (i.e. they have the same number of
            words and all of them match in the same order). Will return False if
            the ngrams have different sizes or if ANY of the words of 
            `some_ngram` does not match the corresponding word of the current 
            pattern.
        """
        n = self.get_n()
        if( some_ngram.get_n() == n ) :            
            for i in range( n ) :
                if not self.word_at( i ).match( some_ngram.word_at( i ) ) :
                    return False
            return True
        else :
            return False
            
################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()         

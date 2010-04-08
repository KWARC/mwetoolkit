#!/usr/bin/python
#TODO: DOCUMENTATION
"""
    Represents a corpus in a compact format, as a sequence of integers. The 
    corpus must therefore be associated to a vocabulary file that maps each
    integer (unique ID) to a word form (+lemma+POS).
"""

import pdb

from corpus import Corpus

################################################################################

class SuffixArray ( Corpus ) :

################################################################################

    def __init__( self, vocab, corpus, prefix="index.ngrams" ) :
        Corpus.__init__( self, prefix )
        self.corpus = corpus
        self.vocab = vocab

################################################################################
        
    def __str__( self ) :
        result = ""
        for ngram in self :
            i = 0
            while self.corpus[ ngram + i ] != 0 :
                result += str( self.corpus[ ngram + i ] ) + " "
                i = i + 1
            result += "\n"
        return result.strip()

################################################################################
        
    def count_ngram( self, ngram ) :
        """
            @param ngram A list of words using the same format as the index, 
            i.e. word#S#pos.
        """
        ngram_ids = []
        for w in ngram :
            word_id = self.vocab.get( w.encode( 'utf-8' ), None )
            if word_id :
                ngram_ids.append( word_id )
            else :
                return 0
        # Binary search to find the index of the last position     
        i_low = 0
        i_up = len( self )
        i_mid = ( i_up + i_low ) / 2
        while i_up - i_low > 1 :                              
            if self.corpus.compare_ngram_index( self[i_mid], ngram_ids ) > 0 :
                i_up = i_mid
            else :
                i_low = i_mid
            i_mid = ( i_up + i_low ) / 2
        i_last = i_mid
        
        # Binary search to find the index of the first position 
        i_low = 0
        i_up = len( self )
        i_mid = ( i_up + i_low ) / 2
        while i_up - i_low > 1 :                              
            if self.corpus.compare_ngram_index( self[i_mid], ngram_ids ) >= 0 :
                i_up = i_mid
            else :
                i_low = i_mid
            i_mid = ( i_up + i_low ) / 2
        i_first = i_mid            

        return i_last - i_first        
        
################################################################################        

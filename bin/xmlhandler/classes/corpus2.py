#!/usr/bin/python
#TODO: DOCUMENTATION
"""
    Represents a corpus in a compact format, as a sequence of integers. The 
    corpus must therefore be associated to a vocabulary file that maps each
    integer (unique ID) to a word form (+lemma+POS).
"""

import array
import os.path
import sys
import pdb

from __common import MAX_MEM

################################################################################

class CorpusIter() :
    """
    """

    def __init__( self, corpus ) :
        self.current = -1
        self.corpus = corpus

################################################################################
        
    def __iter__( self ) :
        return self
        
################################################################################        
        
    def next( self ) :
        self.current += 1
        if self.current >= len( self.corpus ) :
            raise StopIteration
        else :
            return self.corpus[ self.current ]
            
################################################################################
################################################################################        

class Corpus() :    
    """
    """

    def __init__( self, prefix="index.corpus" ) :
        self.MAX_MEM_ITEMS = int( (MAX_MEM * 1024 * 1024) / 4 )
        if self.MAX_MEM_ITEMS <= 0 :
            raise ValueError( "The maximum amount of RAM must be positive" )
        self.prefix = prefix
        self.__detect_max_suffix()                 
        self.__fromfile( self.max_suffix ) # Open the last corpus file
        self.size = self.MAX_MEM_ITEMS * self.max_suffix + len( self.current_list )

################################################################################
        
    def append( self, item ) :
        # The current list is not the last of the corpus
        self.__changefile( self.max_suffix )        
        if len( self.current_list ) < self.MAX_MEM_ITEMS :
            self.current_list.append( item )
        else : # needs to create a new corpus file
            self.max_suffix = self.max_suffix + 1
            self.__changefile( self.max_suffix )                    
            self.current_list.append( item )            
        self.modified = True
        self.size = self.size + 1
            
################################################################################

    def __make_filename( self, prefix, suffix ) :        
        return prefix + "_" + str( suffix ).rjust( 3, "0" )       

################################################################################

    def __detect_max_suffix( self ) :
        self.max_suffix = 1
        while os.path.isfile( self.__make_filename( self.prefix, self.max_suffix ) ) :
            self.max_suffix = self.max_suffix + 1
        self.max_suffix = self.max_suffix - 1
        
################################################################################

    def __getitem__( self, i ) :
        if i > ( self.max_suffix + 1 ) * self.MAX_MEM_ITEMS :
            pdb.set_trace()
            raise IOError( "array index out of range" )
        file_suffix = i / self.MAX_MEM_ITEMS
        self.__changefile( file_suffix )
        return self.current_list[ i % self.MAX_MEM_ITEMS ]
    
################################################################################ 

    def __setitem__( self, i, value ) :
        if i > ( self.max_suffix + 1 ) * self.MAX_MEM_ITEMS :
            raise IOError( "array assignment index out of range" )
        file_suffix = i / self.MAX_MEM_ITEMS
        self.__changefile( file_suffix )
        self.current_list[ i % self.MAX_MEM_ITEMS ] = value
        self.modified = True

################################################################################ 
        
    def insert( self, i, value ) :
        if i > ( self.max_suffix + 1 ) * self.MAX_MEM_ITEMS :
            raise IOError( "array assignment index out of range" )
        file_suffix = i / self.MAX_MEM_ITEMS
        self.__changefile( file_suffix )
        if file_suffix > self.max_suffix :
            self.max_suffix = file_suffix
        self.current_list.insert( i % self.MAX_MEM_ITEMS, value )        
        self.size = self.size + 1
        self.modified = True        
        if len( self.current_list ) > self.MAX_MEM_ITEMS :
            last_elem = self.current_list.pop()
            self.size = self.size - 1
            self.insert( ( self.current_suffix + 1 ) * self.MAX_MEM_ITEMS, last_elem )
            
    
################################################################################    

    def __changefile( self, new_suffix ) :
        if new_suffix != self.current_suffix :
            if self.modified :
                self.__tofile( self.current_suffix )
            self.__fromfile( new_suffix )
        
################################################################################

    def __iter__( self ) :
        return CorpusIter( self )

################################################################################

    def __len__( self ) :
#        self.__changefile( self.max_suffix )
#        return self.max_suffix * self.MAX_MEM_ITEMS + len( self.current_list )
        return self.size
        
################################################################################

    def __fromfile( self, suffix ) :
        self.current_suffix = suffix    
        self.modified = False        
        self.current_list = array.array( 'L' )    
        try :
            fd = open( self.__make_filename( self.prefix, suffix ), "r" )
            self.current_list.fromfile( fd, self.MAX_MEM_ITEMS )
            fd.close()
        except EOFError :
            pass # Did not read MAX_MEM_ITEMS items? Not a problem...
        except IOError :
            fd = open( self.__make_filename( self.prefix, suffix ), "w" )
            fd.close()

################################################################################

    def __str__( self ) :  
        result = "["
        # +1 because the last frag must be printed too         
        for i in range( self.max_suffix + 1 ) : 
            self.__changefile( i )
            for item in self.current_list :
                result += str( item ) + ", "
        return result[ :len(result) - 2 ] + "]"

################################################################################

    def __tofile( self, suffix ) :
        try :
            fd = open( self.__make_filename( self.prefix, suffix ), "w" )
            self.current_list.tofile( fd )
            fd.close()        
        except IOError :
            print >> sys.stderr, "Error flushing corpus file. You might have "+\
                                 "lost recent modifications"

################################################################################

    def clear( self ) :   
        del_suffix = 0
        filename = self.__make_filename( self.prefix, del_suffix )
        while os.path.isfile( filename ) :
            os.remove( filename )
            del_suffix = del_suffix + 1
            filename = self.__make_filename( self.prefix, del_suffix )
        self.max_suffix = 0       
        self.__fromfile( self.max_suffix ) # Open the last corpus file
        self.size = self.MAX_MEM_ITEMS * self.max_suffix + len( self.current_list )
        

################################################################################

    def __del__( self ) :
        self.__tofile( self.current_suffix )

################################################################################

    def compare_indices( self, pos1, pos2 ) :
        """
            returns 1 if ngram(pos1) >lex ngram(pos2), -1 for ngram(pos1) <lex
            ngram(pos2) and 0 for matching ngrams
        """
        pos1_cursor = pos1
        wordp1 = self[ pos1_cursor ]
        pos2_cursor = pos2 
        wordp2 = self[ pos2_cursor ]          

        while wordp1 == wordp2 :
            # both are zero, we can stop because they are considered identical
            if wordp1 == 0 :
                break                
            pos1_cursor += 1   
            wordp1 = self[ pos1_cursor ]        
            pos2_cursor += 1   
            wordp2 = self[ pos2_cursor ]             
        return wordp1 - wordp2
            
################################################################################

    def compare_ngram_index( self, pos, ngram_ids ) :
        """
            returns 1 if ngram(pos1) >lex ngram(pos), -1 for ngram(pos1) <lex
            ngram(pos) and 0 for matching ngrams
        """
       
        pos1_cursor = pos
        wordp1 = self[ pos1_cursor ]
        pos2_cursor = 0 
        wordp2 = ngram_ids[ pos2_cursor ]          

        while wordp1 == wordp2 and pos2_cursor < len( ngram_ids ) - 1:
            # both are zero, we can stop because they are considered identical
            if wordp1 == 0 :
                break                
            pos1_cursor += 1   
            wordp1 = self[ pos1_cursor ]
            pos2_cursor += 1   
            wordp2 = ngram_ids[ pos2_cursor ]             
        return wordp1 - wordp2

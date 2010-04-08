from xmlhandler.classes.word import Word
from xmlhandler.classes.sentence import Sentence
from xmlhandler.classes.ngram import Ngram

the = Word( "the", "the", "DT", [] )
man = Word( "man", "man", "N", [] )            
be = Word( "is", "be", "V", [] )                        
an = Word( "an", "a", "DT", [] )  
idiot = Word( "idiot", "idiot", "A", [] )
w_list = [ the, man, be, be, an, idiot ]
s1 = Sentence( w_list[:], 0 )
n4 = Ngram( [ be, an, idiot ], [] )
s1.find( n4 )

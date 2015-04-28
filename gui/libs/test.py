from Patterns import *
from EitherPattern import *
from SequencePattern import *
from WordPattern import *
from XMLFormatter import *

patterns = Patterns()
xmlformatter = XMLFormatter()

'''<?xml version="1.0" encoding="UTF-8"?><patterns><pat><w pos="A" /><w pos="N" /></pat></patterns>'''

word1 = WordPattern(1, {'pos': ['A']})
word2 = WordPattern(2, {'pos': ['B']}, {'pos': ['C']})

sequence = SequencePattern(1)
sequence.add(word1)
sequence.add(word2)

patterns.add(sequence)

patterns.accept(xmlformatter)
print xmlformatter.format()
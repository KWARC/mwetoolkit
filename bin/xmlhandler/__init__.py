"""
    This package provides a set of XML handlers that convert the XML entities
    into Object Oriented representations that are used by mwttoolkit's scripts. 
    The classes provided in this package correspond to the DTDs that define
    mwttoolkit's intermediary XML formats:
    
    `CandidatesXMLHandler` - SAX parser for XML documents that are valid 
    candidate lists according to mwttoolkit-candidates.dtd.
    
    `CorpusXMLHandler` - SAX parser for XML documents that are valid corpora 
    according to mwttoolkit-corpus.dtd.
    
    `PatternsXMLHandler` - SAX parser for XML documents that are valid pattern 
    or reference lists according to mwttoolkit-patterns.dtd.      
"""

import install

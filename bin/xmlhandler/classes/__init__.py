"""
    This package provides the classes that are used by the XML handlers as
    Object Oriented representations of the XML entities contained in the files
    that are used by mwttoolkit. The classes provided in this package are:
    
    `Candidate` - representation of a MWT candidate, including base form, id, 
    occurrences, features and the TP class (true/false MWT).
    
    `CorpusSize` - representation of a meta-information about the number of 
    tokens in a given corpus.   
   
    `Feature` - representation of a feature of the candidate, i.e. a pair 
    attribute-value that describes it.
   
    `Frequency` - representation of a frequency of occurrences of an element in
    a corpus, i.e. an integer for the number of times the element (word or 
    ngram) appears in the corpus.
   
    `Meta` - representation of the header of the XML file, describing several 
    meta-information about the canidate list that the file contains.
   
    `MetaFeat` - representation of the meta-information about a `Feature`, 
    specially its type.
    
    `MetaTPClass` - representation of the meta-information about a `TPClass`, 
    specially the enumeration of possible class values.
    
    `Ngram` - representation of an ngram, i.e. a sequence of words as they occur 
    in the corpus. A ngram is any sequence of n words, not necessarily a 
    linguistically motivated phrase.
    
    `Pattern` - representation of an ngram pattern, i.e. a sequence of words (or 
    word patterns) as they occur in the pattern or reference lists.
    
    `Sentence` - representation of a sentence, i.e. a sequence of words that 
    convey a complete information, as they occur in the corpus. You are expected 
    to use this class to represent objects that are linguistically motivated
    sentences, not simply ngrams.
    
    `TPClass` - representation of a True Positive judgment of a candidate, i.e. 
    the evaluation of a candidate with respect to a reference, that can be a
    machine-readable gold standard (automatic evaluation) or a human judge 
    (manual evaluation).
    
    `Word` - representation of an orthographic word defined by a surface form, a 
    lemma and a POS tag.
    
    `YahooFreq` - representation of an abstract gateway that allows you to 
    access the Yahoo search index and look up for the number of Web pages that 
    contain a certain word or ngram.    
"""

import install

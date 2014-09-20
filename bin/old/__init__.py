#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# __init__.py is part of mwetoolkit
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
    This package provides the base that are used by the XML handlers as
    Object Oriented representations of the XML entities contained in the files
    that are used by mwetoolkit. The base provided in this package are:
    
    `Candidate` - representation of a MWE candidate, including base form, id,
    occurrences, features and the TP class (true/false MWE).
    
    `CorpusSize` - representation of a meta-information about the number of 
    tokens in a given corpus.   
   
    `Entry` - representation of a dictionary entry, i.e. a sequence of words (or
    word patterns) as they occur in the pattern, reference and dictionary lists.

    `Feature` - representation of a feature of the candidate, i.e. a pair 
    attribute-value that describes it.
   
    `Frequency` - representation of a frequency of occurrences of an element in
    a corpus, i.e. an integer for the number of times the element (word or 
    ngram) appears in the corpus.
   
    `GoogleFreq` - representation of an abstract gateway that allows you to
    access the Google search index and look up for the number of Web pages that
    contain a certain word or ngram.

    `Meta` - representation of the header of the XML file, describing several 
    meta-information about the canidate list that the file contains.
   
    `MetaFeat` - representation of the meta-information about a `Feature`, 
    specially its type.
    
    `MetaTPClass` - representation of the meta-information about a `TPClass`, 
    specially the enumeration of possible class values.
    
    `Ngram` - representation of an ngram, i.e. a sequence of words as they occur 
    in the corpus. A ngram is any sequence of n words, not necessarily a 
    linguistically motivated phrase.
         
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

    `YahooTerms` - representation of an abstract gateway that allows you to
    access the Yahoo terms service and look up for the terms identified in a
    text fragment.

"""

import install

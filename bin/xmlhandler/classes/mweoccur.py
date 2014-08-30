#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2014 Silvio Ricardo Cordeiro, Carlos Ramisch
#
# mweoccur.py is part of mwetoolkit
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
This module provides the `MWEOccurrence` class. This class represents an
occurrence of an MWE `Candidate` inside a `Sentence`.
"""

################################################################################

import pdb


class MWEOccurrence(object):
    r"""Represents the occurrence of an MWE candidate in a sentence.

    Attributes:
    -- sentence: The sentence in this occurrence.
    -- candidate: The MWE candidate in this occurrence.
    -- indexes: A list of indexes that represent the position of
    each word from `self.candidate` in `self.sentence`.
    This list will be `list(xrange(i, i + len(self.candidate)))` when
    referring to the simplest kinds of MWEs.  If the MWE in-sentence has
    different word order (e.g. passive voice in English), a permutation of
    those indexes should be used.  If there are gaps inside the MWE (e.g.
    verb-particle compounds in English), other sentence indexes may be used.
    IMPORTANT: This list is 0-based in python but 1-based in XML.

    Examples:
        Today ,  a  demo was given  Sentence
                 ~  ~~~~     ~~~~~  Candidate = "give a demo"
        _     _  2  3    _   5      indexes = [5, 2, 3]

        The old man kicked the proverbial bucket  Sentence
                    ~~~~~~ ~~~            ~~~~~~  Candidate = "kick the bucket"
        _   _   _   3      4   _          6       indexes = [3, 4, 6]
    """
    def __init__(self, sentence, candidate, sentence_indexes):
        self.candidate = candidate
        self.sentence = sentence
        self.indexes = sentence_indexes

    def to_xml(self):
        ret = ['<mweoccur candid="']
        ret.append(unicode(self.candidate.id_number))
        ret.append('">')
        # For each (candidate index, sentence index)...
        for c_i, s_i in enumerate(self.indexes):
            ret.append('<mwepart index="')
            ret.append(unicode(s_i + 1))
            ret.append('">')
            ret.append(self.candidate[c_i].lemma)
            ret.append('</mwepart>')
        ret.append("</mweoccur>")
        return ''.join(ret)



class MWEOccurrenceBuilder(object):
    r"""Creates an instance of MWEOccurrence.

    Attributes:
    -- sentence: Will become `MWEOccurrence.sentence`.
    -- candidate: Will become `MWEOccurrence.candidate`.
    -- indexes: Will become `MWEOccurrence.indexes`.
    """
    # XXX implement a JMWE-style comparator
    def __init__(self, sentence, candidate):
        self.sentence, self.candidate = sentence, candidate
        words = set(w.lemma for w in self.sentence.word_list)
        self.has_multiple = len(words) != len(sentence)
        self.indexes = []  # similar to JMWE's `MWEBuilder.slot`

    def is_full(self):
        r"""Return whether the builder is ready to create an MWEOccurrence."""
        # Similar to JMWE's `MWEBuilder.isFull`.
        assert len(self.indexes) <= len(self.candidate)
        return len(self.indexes) == len(self.candidate)

    def match(self, index_sentence, index_candidate):
        r"""Return whether we should fill position `index_candidate`
        with the word in `index_sentence`."""
        # Similar to JMWE's `IMWEDesc.isFillerForSlot`.
        raise NotImplementedError

    def fill_next_slot(self, index_sentence):
        r"""If possible to fill next index slot, do it by
        appending an index from sentence to this builder
        and return True.  Otherwise, return False."""
        # Similar to JMWE's `MWEBuilder.fillNextSlot`.
        if self.is_full():
            return False  # Cannot match anything else
        if not self.match(index_sentence, len(self.indexes)):
            return False  # Does not match POS or whatever
        self.indexes.append(index_sentence)
        return True

    def checked_fill_next_slot(self, index_sentence):
        r"""Call `fill_next_slot` and raise if it returns False."""
        if not self.fill_next_slot(index_sentence):
            raise Exception("Unable to fill next slot!")

    def create(self):
        r"""Create an MWEOccurrence object."""
        if not self.is_full():
            raise Exception("MWEOccurrence not ready to be created")
        return MWEOccurrence(self.sentence,
                self.candidate, self.indexes)
    
    def __repr__(self):
        return b" ".join(w.lemma.encode('utf8') for w in self.candidate.word_list)

        
################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  

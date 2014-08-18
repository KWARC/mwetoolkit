#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2014 Silvio Ricardo Cordeiro
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


class MWEOccurrence(object):
    r"""Represents the occurrence of an MWE candidate in a sentence.

    Attributes:
    -- sentence: The sentence in this occurrence.
    -- candidate: The MWE candidate in this occurrence.
    -- base_index: The first index in `self.sentence`.
    -- indexes: A list of indexes that, after being offset by `self.base_index`,
    represent the position of each word from `self.candidate` in `self.sentence`.
    This list can be `None` or `list(xrange(len(self.candidate)))` when
    referring to the simplest kinds of MWEs.  If the MWE in-sentence has
    different word order (e.g. passive voice in English), a permutation of
    those indexes should be used.  If there are gaps inside the MWE
    (e.g. verb-particle compounds in English), the list will be missing indexes
    below `len(self.candidate)` and will have indexes above this threshold.

    Examples:
        Today ,  a  demo was given  Sentence
                 ~  ~~~~     ~~~~~  Candidate = "give a demo"
        0     1  ^  3    4   5      base_index = 2
        _     _  1  2    _   0      indexes = [1, 2, 0]

        The old man kicked the proverbial bucket  Sentence
                    ~~~~~~ ~~~            ~~~~~~  Candidate = "kick the bucket"
        0   1   2   ^      4   5          6       base_index = 3
        _   _   _   0      1   _          3       indexes = [0, 1, 3]
    """
    def __init__(self, sentence, candidate, indexes=None, base_index=0):
        if indexes is None:
            indexes = tuple(xrange(len(candidate)))
        assert 0 <= base_index < len(candidate)
        assert len(indexes) == len(candidate)
        self.candidate, self.sentence = candidate, sentence
        self.base_index, self.indexes = base_index, indexes

    def rebase(self):
        r"""Update the value of `base_index` to the lowest possible.
        (After this, there will be a `0` in `self.indexes`)."""
        offset = min(self.indexes)
        self.indexes = [i-offset for i in self.indexes]
        self.base_index += offset
        return self

    def iter_relative_indexes(self):
        r"""For each word in `self.candidate`, yield the
        index of `self.sentence` that correspond to that word
        WHEN offset by `self.base_index`."""
        indexes = self.indexes or xrange(len(self.candidate))
        for i in indexes:
            yield i

    def iter_absolute_indexes(self):
        r"""For each word in `self.candidate`, yield the
        index of `self.sentence` that correspond to that word."""
        for i in self.iter_relative_indexes():
            yield self.base_index + i

    def to_xml(self):
        ret = ['<mweoccur base_index="']
        ret.append(unicode(self.base_index))
        ret.append('" candid="')
        ret.append(unicode(self.candidate.id_number))
        ret.append('">')
        for i in self.iter_relative_indexes():
            ret.append('<mwepart index="')
            ret.append(unicode(i))
            ret.append('">')
            ret.append(self.candidate[i].lemma)
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
        if not self.match(index_sentence, len(self.indexes)):
            return False
        self.indexes.append(index_sentence)
        return True

    def create(self):
        r"""Create an MWEOccurrence object."""
        if not self.is_full():
            raise Exception("MWEOccurrence not ready to be created")
        return MWEOccurrence(self.sentence,
                self.candidate, self.indexes).rebase()
    
    def __repr__(self):
        return b" ".join(w.lemma.encode('utf8') for w in self.candidate.word_list)

        
################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  

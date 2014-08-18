#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2014 Silvio Ricardo Cordeiro
#
# annotate_mwe.py is part of mwetoolkit
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
This script creates an annotated copy of an XML corpus (mwetoolkit-corpus.dtd)
based on an XML with a list of MWE candidates (mwetoolkit-candidates.dtd).

For more information, call the script with no parameter and read the
usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
import sys
import re
import shelve
import xml.sax
import os
import tempfile
import pdb

from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.genericXMLHandler import GenericXMLHandler
from xmlhandler.dictXMLHandler import DictXMLHandler
from xmlhandler.classes.__common import WILDCARD, \
                                        TEMP_PREFIX, \
                                        TEMP_FOLDER, \
                                        XML_HEADER, \
                                        XML_FOOTER
from xmlhandler.classes.frequency import Frequency
from xmlhandler.classes.candidate import Candidate
from xmlhandler.classes.mweoccur import MWEOccurrence
from xmlhandler.classes.mweoccur import MWEOccurrenceBuilder
from xmlhandler.classes.ngram import Ngram
from xmlhandler.classes.word import Word
from xmlhandler.classes.entry import Entry
from util import usage, read_options, treat_options_simplest, \
                 verbose, interpret_ngram, XMLParser
from xmlhandler.classes.printer import Printer as XMLPrinter

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s -c <candidates.xml> OPTIONS <corpus>

-c <candidates.xml> OR --candidates <candidates.xml>
    The MWE candidates to annotate (mwetoolkit-candidates.dtd)

    
OPTIONS may be:

XXX XXX CHANGE TO THE ACTUAL OPTIONS
-i OR --index
     Read the corpus from an index instead of an XML file. Default false.
"""
candidates_fnames = []
candidate_from_id = {}  # ID -> Candidate
detector = None



################################################################################

class AnnotatingXMLParser(XMLParser):
    def __init__(self, args):
        super(AnnotatingXMLParser,self).__init__(
                args, printer=XMLPrinter("corpus"))
        self.sentence_counter = 0

    def treat_sentence(self, sentence):
        """For each sentence in the corpus, detect MWEs and append
        MWEOccurrence instances to its `mweoccur` attribute.

        @param sentence A `Sentence` that is being read from the XML file.    
        """
        self.sentence_counter += 1
        if self.sentence_counter % 100 == 0:
            verbose("Processing sentence number %(n)d"
                    % {"n": self.sentence_counter})

        for mwe_occurrence in detector.detect(sentence):
            sentence.mweoccurs.append(mwe_occurrence)
        self.printer.add(sentence)


class ConsecutiveLemmaDetector(object):
    r"""MWE candidates detector that detects MWEs whose
    lemmas appear contiguously in a sentence.
    
    Attributes:
    -- candidate_from_id: A mapping from `Candidate.id_number`
    to the candidate instance itself.
    """
    # Similar to JMWE's `Consecutive`.
    def __init__(self, candidate_from_id):
        self.candidate_from_id = candidate_from_id
        assert all(k==v.id_number for (k,v) in
                self.candidate_from_id.iteritems())

    def detect(self, sentence):
        r"""Return a list of MWEOccurrence objects for this sentence."""
        cur_b = []  # similar to JMWE's local var `in_progress`
        done_b = [] # similar to JMWE's local var `done`
        for i in xrange(len(sentence)):
            # Keep only builders that can fill next slot
            cur_b = [b for b in cur_b if b.fill_next_slot(i)]
            # Move full builders to `done_b`
            done_b.extend(b for b in cur_b if b.is_full())
            # Remove full builders from `cur_b`
            cur_b = [b for b in cur_b if not b.is_full()]

            # Append new builders for whom `i` can fill the first slot
            for candidate in self.candidate_from_id.itervalues():
                b = self.LemmaMWEOBuilder(sentence, candidate)
                if b.fill_next_slot(i):
                    cur_b.append(b)

        return [b.create() for b in done_b]


    class LemmaMWEOBuilder(MWEOccurrenceBuilder):
        r"""Matches equal lemmas in sentence-vs-candidate."""
        def match(self, index_sentence, index_candidate):
            s = self.sentence[index_sentence]
            c = self.candidate[index_candidate]
            return s.lemma == c.lemma


class XXXXXXXXXXXXAbstractDetector(object):
    r"""Instances of this class are used to detect the occurrence
    of candidate MWEs in sentences.

    Protected attributes:
    @param _from_lemma_set Map from set(lemmas) to subset of candidates.
    @param _from_first_lemma Map from lemma to subset of candidates.
       Maps to the subset of candidates that start with this lemma.
    """
    def __init__(self, candidates):
        r"""Initialize detector with given candidates."""
        self._from_lemma_set = collections.defaultdict(set)
        self._from_first_lemma = {}
        for c in candidates:
            if len(c):
                self._from_first_lemma[c[0]].add(c)
            self._from_lemma_set[set(c)].add(c)

    def detect(self, sentence):
        r"""Yield all occurrences of a candidate in `sentence`."""
        IMPLEMENT_ME


################################################################################  


class CandidatesParser(XMLParser):
    def treat_sentence(self, candidate):
        global candidate_from_id
        candidate_from_id[candidate.id_number] = candidate


################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global candidates_fnames, detector, candidate_from_id
    treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o in ("-c", "--candidates"):
            candidates_fnames.append(a)

    if not candidates_fnames:
        print("No candidates file given!", file=sys.stderr)
        exit(1)

    try:
        CandidatesParser(candidates_fnames).parse()
    except Exception:
        print("Error loading candidates file!", file=sys.stderr)
        raise

    detector = ConsecutiveLemmaDetector(candidate_from_id)

        
################################################################################  
# MAIN SCRIPT

longopts = ["candidates="]
arg = read_options("c:", longopts, treat_options, -1, usage_string)
AnnotatingXMLParser(arg).parse()

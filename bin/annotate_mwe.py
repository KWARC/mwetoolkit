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

-d <method> OR --detection <method>
    Name of a valid detection method.
    * Method "ContiguousLemma" = detects contiguous lemmas.
    * Method "Source" = uses `<sources>` tag from candidates file.

-S OR --source
    Annotate based on the `<sources>` tag from the candidates file.
    Same as passing the parameter `-d Sources`.
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


################################################################################


class SourcesDetector(object):
    r"""MWE candidates detector that uses information
    from the <sources> tag in the candidates file to
    annotate the original corpus.

    Attributes:
    -- candidate_from_id: A mapping from `Candidate.id_number`
    to the candidate instance itself.
    -- sentence_occurs: A mapping from `Sentence.id_number`
    to a list of (candidate, indexes) for an MWE occurrence.
    """
    def __init__(self, candidate_from_id):
        self.candidate_from_id = candidate_from_id
        self.sentence_occurs = collections.defaultdict(list)
        for cand in candidate_from_id.itervalues():
            for ngram in cand.occurs:
                for source in ngram.sources:
                    sentence_id, indexes = source.split(":")
                    indexes = [int(i) for i in indexes.split(",")]
                    if len(cand) != len(indexes):
                        raise Exception("Bad value of indexes for cand {}: {}"
                                .format(cand.id_number, indexes))
                    self.sentence_occurs[int(sentence_id)].append((cand,indexes))

    def detect(self, sentence):
        r"""Yield MWEOccurrence objects for this sentence."""
        for cand, indexes in self.sentence_occurs[sentence.id_number]:
            yield MWEOccurrence(sentence, cand, indexes).rebase()


class ContiguousLemmaDetector(object):
    r"""MWE candidates detector that detects MWEs whose
    lemmas appear contiguously in a sentence.
    
    Attributes:
    -- candidate_from_id: A mapping from `Candidate.id_number`
    to the candidate instance itself.
    """
    # Similar to JMWE's `Consecutive`.
    def __init__(self, candidate_from_id):
        self.candidate_from_id = candidate_from_id

    def detect(self, sentence):
        r"""Yield MWEOccurrence objects for this sentence."""
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


detectors = {
    "Sources" : SourcesDetector,
    "ContiguousLemma" : ContiguousLemmaDetector,
}


################################################################################  


class CandidatesParser(XMLParser):
    def treat_sentence(self, candidate):
        global candidate_from_id
        candidate_from_id[candidate.id_number] = candidate


################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global candidates_fnames, detector, candidate_from_id
    treat_options_simplest(opts, arg, n_arg, usage_string)
    detector_class = ContiguousLemmaDetector

    for (o, a) in opts:
        if o in ("-c", "--candidates"):
            candidates_fnames.append(a)
        if o in ("-d", "--detector"):
            detector_class = detectors[a]
        if o in ("-S", "--source"):
            detector_class = SourcesDetector

    if not candidates_fnames:
        print("No candidates file given!", file=sys.stderr)
        exit(1)

    try:
        CandidatesParser(candidates_fnames).parse()
    except Exception:
        print("Error loading candidates file!", file=sys.stderr)
        raise

    assert all(k==v.id_number for (k,v) in
            candidate_from_id.iteritems())

    detector = detector_class(candidate_from_id)

        
################################################################################  
# MAIN SCRIPT

longopts = ["candidates=", "detector=", "source"]
arg = read_options("c:d:S", longopts, treat_options, -1, usage_string)
AnnotatingXMLParser(arg).parse()

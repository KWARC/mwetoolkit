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
                 verbose, interpret_ngram, XMLParser, error
from xmlhandler.classes.printer import Printer as XMLPrinter

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s -c <candidates.xml> OPTIONS <corpus>

-c <candidates.xml> OR --candidates <candidates.xml>
    The MWE candidates to annotate (mwetoolkit-candidates.dtd)

    
OPTIONS may be:

-d <method> OR --detection <method>
    Choose a method of MWE detection (default: "ContiguousLemma"):
    * Method "ContiguousLemma": detects contiguous lemmas.
    * Method "Source": uses `<sources>` tag from candidates file.

-S OR --source
    Annotate based on the `<sources>` tag from the candidates file.
    Same as passing the parameter `--detection=Source`.

-x OR --text
    Output the corpus in textual format, only surface forms, with <mwe> XML
    tags around MWE members.

%(common_options)s
"""
candidates_fnames = []
detector = None
out_text = False

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
        global out_text
        self.sentence_counter += 1
        if self.sentence_counter % 100 == 0:
            verbose("Processing sentence number %(n)d"
                    % {"n": self.sentence_counter})

        for mwe_occurrence in detector.detect(sentence):
            sentence.mweoccurs.append(mwe_occurrence)
            
        if out_text :  #CR - probably better with a TxTPrinter class?
            print( sentence.to_surface() )            
        else : #CR
            self.printer.add(sentence)


################################################################################


class SourceDetector(object):
    r"""MWE candidates detector that uses information
    from the <sources> tag in the candidates file to
    annotate the original corpus.
    """
    def __init__(self, candidate_info):
        self.candidates_list = candidate_info.candidates_list()
        self.info_from_s_id = candidate_info.parsed_source_tag()

    def detect(self, sentence):
        r"""Yield MWEOccurrence objects for this sentence."""
        for cand, indexes in self.info_from_s_id[sentence.id_number]:
            yield MWEOccurrence(sentence, cand, indexes).rebase()


class ContiguousLemmaDetector(object):
    r"""MWE candidates detector that detects MWEs whose
    lemmas appear contiguously in a sentence.

    This is similar to JMWE's Consecutive class, but:
    -- We build MWEOccurrence objects based on a hash table
    from the first lemma of the candidate, turning that ugly
    `O(n*m)` algorithm into a best-case `O(n+m)` algorithm,
    attempting to match against only a small fraction of the
    set of candidates for each index of the sentence.
    (Assuming `n = number of words in all sentences`
    and `m = number of MWE candidates`).
    -- Instead of keeping a local variable `done` with the list
    of MWE builders that are `full`, we keep a list `all_b` with
    all builders created, and then filter out the bad ones in the end.
    This allows us to report MWEs in the order they were seen.
    """
    # Similar to JMWE's `Consecutive`.
    def __init__(self, candidate_info):
        self.candidates_from_1st_lemma = \
                candidate_info.candidates_from_1st_lemma()

    def detect(self, sentence):
        r"""Yield MWEOccurrence objects for this sentence."""
        all_b = []  # all builders ever created
        cur_b = []  # similar to JMWE's local var `in_progress`
        for i in xrange(len(sentence)):
            # Keep only builders that can (and did) fill next slot
            cur_b = [b for b in cur_b if b.fill_next_slot(i)]

            # Append new builders for whom `i` can fill the first slot
            first_lemma = sentence[i].lemma
            for candidate in self.candidates_from_1st_lemma[first_lemma]:
                b = self.LemmaMWEOBuilder(sentence, candidate)
                b.checked_fill_next_slot(i)
                cur_b.append(b)
                all_b.append(b)

        return [b.create() for b in all_b if b.is_full()]


    class LemmaMWEOBuilder(MWEOccurrenceBuilder):
        r"""Matches equal lemmas in sentence-vs-candidate."""
        def match(self, index_sentence, index_candidate):
            s = self.sentence[index_sentence]
            c = self.candidate[index_candidate]
            return s.lemma == c.lemma


detectors = {
    "Source" : SourceDetector,
    "ContiguousLemma" : ContiguousLemmaDetector,
}


################################################################################  


class CandidatesParser(XMLParser):
    r"""Parse file and populate a CandidateInfo object."""
    def __init__(self, candidate_fnames):
        super(CandidatesParser,self).__init__(candidate_fnames)
        self.info = CandidateInfo()

    def treat_sentence(self, candidate):
        self.info.add(candidate)


class CandidateInfo(object):
    r"""Object with information about candidates."""
    def __init__(self):
        self._L = []

    def add(self, candidate):
        r"""Add a candidate to this object."""
        self._L.append(candidate)

    def candidates_list(self):
        """Return a list of candidates [c..]."""
        return self._L

    def candidate_from_id(self):
        r"""Return a dict {c.id_number: c}."""
        return dict((c.id_number,c) for c in self._L)

    def candidates_from_1st_lemma(self):
        r"""Return a dict {1st lemma: [list of candidates]}."""
        ret = collections.defaultdict(list)
        for c in self._L:
            ret[c[0].lemma].append(c)
        return ret

    def parsed_source_tag(self):
        r"""Return a dict {s_id: [(cand,indexes), ...]}."""
        ret = collections.defaultdict(list)
        for cand in self._L:
            for ngram in cand.occurs:
                for source in ngram.sources:
                    sentence_id, indexes = source.split(":")
                    indexes = [int(i)-1 for i in indexes.split(",")]
                    if len(cand) != len(indexes):
                        raise Exception("Bad value of indexes for cand {}: {}"
                                .format(cand.id_number, indexes))
                    ret[int(sentence_id)].append((cand,indexes))
        return ret


################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global candidates_fnames, detector, out_text
    treat_options_simplest(opts, arg, n_arg, usage_string)
    detector_class = ContiguousLemmaDetector

    for (o, a) in opts:
        if o in ("-c", "--candidates"):
            candidates_fnames.append(a)
        if o in ("-d", "--detector"):
            detector_class = detectors[a]
        if o in ("-S", "--source"):
            detector_class = SourceDetector
        if o in ("-x", "--text"):  #CR
            out_text = True #CR
    if not candidates_fnames:
        error("No candidates file given!") #CR refactoring

    try:
        p = CandidatesParser(candidates_fnames)
        p.parse()
    except Exception:
        print("Error loading candidates file!", file=sys.stderr)
        raise

    detector = detector_class(p.info)

        
################################################################################  
# MAIN SCRIPT

longopts = ["candidates=", "detector=", "source", "text"]
arg = read_options("c:d:Sx", longopts, treat_options, -1, usage_string)
AnnotatingXMLParser(arg).parse()

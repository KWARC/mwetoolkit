#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
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
from __future__ import absolute_import

import collections
import sys

from libs.base.mweoccur import MWEOccurrenceBuilder, MWEOccurrence
from libs.util import read_options, treat_options_simplest, verbose, error
from libs.printers import XMLPrinter, SurfacePrinter, MosesPrinter
from libs.parser_wrappers import parse, InputHandler




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
    * Method "Source": uses "<sources>" tag from candidates file.

-g <n-gaps> OR --gaps <n-gaps>
    Allow a number of gaps inside the detected MWE.
    (This argument is NOT allowed for the method of detection "Source").

-S OR --source
    Annotate based on the "<sources>" tag from the candidates file.
    Same as passing the parameter "--detection=Source".

-o <format> OR --output <format>
    Choose a method of output (default: "XML"):
    * Method "XML": output corpus in XML format.
    * Method "Text": output corpus in textual format, showing only surface forms 
      and <mwe> XML tags surrounding MWE tokens.
    * Method "Moses": output corpus in Moses factored format, with word factors 
      separated by vertical bars | and <mwe> XML tags surrounding MWE tokens.

%(common_options)s
"""
detector = None
printer_class = None

################################################################################


class AnnotatorHandler(InputHandler):
    r"""An InputHandler that prints the input with annotated MWEs."""
    def __init__(self, printer):
        self.printer = printer
        self.sentence_counter = 0

    def handle_sentence(self, sentence, info={}):
        """For each sentence in the corpus, detect MWEs and append
        MWEOccurrence instances to its `mweoccur` attribute.

        @param sentence: A `Sentence` that is being read from the XML file.    
        @param info: A dictionary with info regarding `sentence`.
        """
        self.sentence_counter += 1
        if self.sentence_counter % 100 == 0:
            verbose("Processing sentence number %(n)d"
                    % {"n": self.sentence_counter})

        for mwe_occurrence in detector.detect(sentence):
            sentence.mweoccurs.append(mwe_occurrence)
        self.printer.add(sentence)


################################################################################


class AbstractDetector(object):
    r"""Base MWE candidates detector.
    
    Constructor Arguments:
    @param candidate_info An instance of CandidateInfo.
    @param n_gaps Number of gaps to allow inside detected MWEs.
    Subclasses are NOT required to honor `n_gaps`.
    """
    def __init__(self, candidate_info, n_gaps):
        self.candidate_info = candidate_info
        self.n_gaps = n_gaps

    def detect(self, sentence):
        r"""Yield MWEOccurrence objects for this sentence."""
        raise NotImplementedError


class SourceDetector(AbstractDetector):
    r"""MWE candidates detector that uses information
    from the <sources> tag in the candidates file to
    annotate the original corpus.

    See `AbstractDetector`.
    """
    def __init__(self, *args, **kwargs):
        super(SourceDetector,self).__init__(*args, **kwargs)
        self.info_from_s_id = self.candidate_info.parsed_source_tag()

    def detect(self, sentence):
        for cand, indexes in self.info_from_s_id[sentence.id_number]:
            yield MWEOccurrence(sentence, cand, indexes)


class ContiguousLemmaDetector(AbstractDetector):
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

    See `AbstractDetector`.
    """
    # Similar to JMWE's `Consecutive`.
    def __init__(self, *args, **kwargs):
        super(ContiguousLemmaDetector,self).__init__(*args, **kwargs)
        self.candidates_from_1st_lemma = \
                self.candidate_info.candidates_from_1st_lemma()

    def detect(self, sentence):
        all_b = []  # all builders ever created
        cur_b = []  # similar to JMWE's local var `in_progress`
        for i in xrange(len(sentence)):
            # Keep only builders that can (and did) fill next slot
            cur_b = [b for b in cur_b if b.fill_next_slot(i)]

            # Append new builders for whom `i` can fill the first slot
            first_lemma = sentence[i].lemma_or_surface()
            for candidate in self.candidates_from_1st_lemma[first_lemma]:
                b = self.LemmaMWEOBuilder(sentence, candidate, self.n_gaps)
                b.checked_fill_next_slot(i)
                cur_b.append(b)
                all_b.append(b)

        return [b.create() for b in all_b if b.is_full()]


    class LemmaMWEOBuilder(MWEOccurrenceBuilder):
        r"""Matches equal lemmas in sentence-vs-candidate."""
        def match_key(self, word):
            return word.lemma_or_surface()


detectors = {
    "Source" : SourceDetector,
    "ContiguousLemma" : ContiguousLemmaDetector,
}


################################################################################  


class CandidatesHandler(InputHandler):
    r"""Parse file and populate a CandidateInfo object."""
    def __init__(self):
        self.info = CandidateInfo()

    def handle_candidate(self, candidate, info={}):
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
            ret[c[0].lemma_or_surface()].append(c)
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

    global printer_class

    treat_options_simplest(opts, arg, n_arg, usage_string)

    detector_class = ContiguousLemmaDetector
    printer_class = XMLPrinter
    candidates_fnames = []
    n_gaps = None

    for (o, a) in opts:
        if o in ("-c", "--candidates"):
            candidates_fnames.append(a)
        if o in ("-d", "--detector"):
            detector_class = detectors[a]
        if o in ("-S", "--source"):
            detector_class = SourceDetector
        if o in ("-o", "--output"):
            printers = {
                "XML": XMLPrinter, 
                "Text": SurfacePrinter, 
                "Moses": MosesPrinter 
            }
            printer_class = printers[a]
        if o in ("-g", "--gaps"):
            n_gaps = int(a)

    if not candidates_fnames:
        error("No candidates file given!")
    if detector_class == SourceDetector and n_gaps is not None:
        error('Bad arguments: method "Source" with "--gaps"')

    try:
        p = parse(candidates_fnames, CandidatesHandler())
    except Exception:
        print("Error loading candidates file!", file=sys.stderr)
        raise

    global detector, printer
    printer = printer_class(root="corpus")
    detector = detector_class(p.info, n_gaps)

        
################################################################################  
# MAIN SCRIPT


longopts = ["candidates=", "detector=", "gaps=", "source", "output="]
arg = read_options("c:d:g:So:", longopts, treat_options, -1, usage_string)
parse(arg, AnnotatorHandler(printer))

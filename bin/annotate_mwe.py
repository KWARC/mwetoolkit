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
from libs import filetype




################################################################################
# GLOBALS

usage_string = """Usage: 
    
python {program} -c <candidates-file> OPTIONS <corpus>

-c <candidates-file> OR --candidates <candidates-file>
    The MWE candidates to annotate, in one of the filetype
    formats accepted by the `--candidates-from` switch.

The <corpus> input file must be in one of the filetype
formats accepted by the `--corpus-from` switch.
    

OPTIONS may be:

--candidates-from <candidates-filetype>
    Force reading candidates from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[candidates]}

--corpus-from <corpus-filetype>
    Force reading corpus from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}

--to <corpus-filetype>
    Output corpus in given filetype format
    (by default, outputs in same format as input):
    {descriptions.output[corpus]}

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

--filter
    Only outputs sentences that matched with MWEs.
    (Does not annotate the MWE candidates).

{common_options}
"""
detector = None
filetype_corpus_ext = None
filetype_candidates_ext = None
output_filetype_ext = None

action_annotate = True
action_filter = False

################################################################################


class AnnotatorHandler(filetype.ChainedInputHandler):
    r"""An InputHandler that prints the input with annotated MWEs."""
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)
        verbose("Annotating corpus with MWEs found in list")

    def handle_sentence(self, sentence, info={}):
        """For each sentence in the corpus, detect MWEs and append
        MWEOccurrence instances to its `mweoccur` attribute.

        @param sentence: A `Sentence` that is being read from the XML file.    
        @param info: A dictionary with info regarding `sentence`.
        """
        found_occurrence = False
        for mwe_occurrence in detector.detect(sentence):
            found_occurrence = True
            if action_annotate:
                sentence.mweoccurs.append(mwe_occurrence)

        if found_occurrence or not action_filter:
            self.chain.handle_sentence(sentence)


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


class CandidatesHandler(filetype.InputHandler):
    r"""Parse file and populate a CandidateInfo object."""
    def __init__(self):
        self.info = CandidateInfo()

    def handle_meta(self, meta, info={}):
        pass # Removes warning. This handler is supposed to ignore meta

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
    global filetype_corpus_ext
    global filetype_candidates_ext
    global output_filetype_ext
    global action_annotate
    global action_filter

    treat_options_simplest(opts, arg, n_arg, usage_string)

    detector_class = ContiguousLemmaDetector
    candidates_fnames = []
    n_gaps = None

    for (o, a) in opts:
        if o in ("-c", "--candidates"):
            candidates_fnames.append(a)
        elif o in ("-d", "--detector"):
            detector_class = detectors[a]
        elif o in ("-S", "--source"):
            detector_class = SourceDetector
        elif o in ("-g", "--gaps"):
            n_gaps = int(a)
        elif o == "--corpus-from":
            filetype_corpus_ext = a
        elif o == "--candidates-from":
            filetype_candidates_ext = a
        elif o == "--to":
            output_filetype_ext = a
        elif o == "--filter":
            action_annotate = False
            action_filter = True
        else:
            raise Exception("Bad arg: " + o)

    if not candidates_fnames:
        error("No candidates file given!")
    if detector_class == SourceDetector and n_gaps is not None:
        error('Bad arguments: method "Source" with "--gaps"')
    c = CandidatesHandler()
    verbose("Reading MWE list from candidates file")
    filetype.parse(candidates_fnames,
            c, filetype_candidates_ext)
    verbose("MWE list loaded in memory successfully")
    global detector
    detector = detector_class(c.info, n_gaps)

        
################################################################################  
# MAIN SCRIPT


longopts = ["corpus-from=", "candidates-from=", "to=",
        "candidates=", "detector=", "gaps=", "source", "filter"]
arg = read_options("c:d:g:So:", longopts, treat_options, -1, usage_string)
filetype.parse(arg, AnnotatorHandler(), filetype_corpus_ext)

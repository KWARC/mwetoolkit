#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# measure.py is part of mwetoolkit
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
This script implements different token-based MWE identification measures,
which can be used to compare a corpus of predicted MWEs with another reference
corpus, on account of the annotated MWEs.

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
from libs.filetype import parse_entities




################################################################################
# GLOBALS

usage_string = """Usage:
    
python {program} -r <reference> OPTIONS <corpus>

-r <reference> OR --reference <reference>
    A gold-standard corpus with annotated MWE occurrences, in one
    of the filetype formats accepted by the `--reference-from` switch.

The <corpus> input file must be in one of the filetype
formats accepted by the `--corpus-from` switch.

    
OPTIONS may be:

--corpus-from <input-filetype-ext>
    Force reading corpus from given file type extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}

--reference-from <reference-filetype-ext>
    Force reading gold-standard from given file type extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}

-e <evaluator> OR --evaluator <evaluator>
    The MWE evaluation algorithm.
    * Evaluator "ExactMatch": Binary comparison.
      Either the MWEs match or they do not.
    * Evaluator "LinkBased": Compare subsequent MWE token pairs,
      as in Schneider [2014] at TACL.

--sentence-aligner <aligner>
    The algorithm that will align sentences between reference and prediction.
    * Aligner "Naive": aligns (0, 0), (1, 1) ... (N, N).
      The only currently supported aligner.
      
{common_options}
"""

reference_fname = None
mwe_evaluator = None
corpus_filetype_ext = None
reference_filetype_ext = None


################################################################################


class OneSidedComparison(object):
    r"""The result of a one-sided reference-vs-prediction MWE comparison.
    This is essentially a pair (NumberOfMatches, NumberOfAttempts), with
    an `add` operation that can be called on each match attempt.

    Example:
    >>> ose = OneSidedComparison(); ose
    OneSidedComparison((0, 0))
    >>> ose.add(1, 3); ose
    OneSidedComparison((1, 3))
    >>> ose.add(1, 2); ose
    OneSidedComparison((2, 5))
    >>> ose.evaluate_float()  # 2/5
    0.4
    """
    def __init__(self, _value=None):
        self.matches, self.attempts = _value or (0, 0)

    def add(self, num_matches, num_attempts):
        r"""Add (+num_matches / +num_attempts) to fraction."""
        self.matches += num_matches
        self.attempts += num_attempts

    def evaluate_float(self):
        r"""Evaluate fraction as a `float` instance."""
        if self.attempts == 0:
            return float('nan')
        return self.matches / self.attempts

    def __iter__(self):
        return iter((self.matches, self.attempts))

    def __repr__(self):
        return "OneSidedComparison({})".format(tuple(self))

    def __mul__(self, mul):
        return OneSidedComparison((mul * x for x in self))
    __rmul__ = __mul__

    def __add__(self, other):
        return OneSidedComparison((x + y for (x, y) in zip(self, other)))



class EvaluationResult(object):
    r"""The result of reference-vs-prediction corpus evaluation.
    
    Example:
    >>> er = EvaluationResult(); er
    EvaluationResult(((0, 0), (0, 0)))
    >>> er.prediction_comparison.add(1, 3); er
    EvaluationResult(((1, 3), (0, 0)))
    >>> er.prediction_comparison.add(1, 2); er
    EvaluationResult(((2, 5), (0, 0)))
    >>> er.precision()  # 2/5
    0.4
    >>> er.reference_comparison.add(4, 8); er
    EvaluationResult(((2, 5), (4, 8)))
    >>> er.recall()  # 4/8
    0.5
    >>> er = 2 * er; er
    EvaluationResult(((4, 10), (8, 16)))
    >>> er = er + EvaluationResult(((0, 0), (1, 1))); er
    EvaluationResult(((4, 10), (9, 17)))
    """
    def __init__(self, _values=None):
        p, r = _values or ((0, 0), (0, 0))
        self.prediction_comparison = OneSidedComparison(p)
        self.reference_comparison = OneSidedComparison(r)

    def precision(self):
        r"""Return the precision (aka Positive Predictive Value)."""
        return self.prediction_comparison.evaluate_float()

    def recall(self):
        r"""Return the recall (aka True Positive Rate)."""
        return self.reference_comparison.evaluate_float()

    def f_measure(self):
        r"""Return the harmonic mean of [precision, recall]."""
        p, r = self.precision(), self.recall()
        return 2*p*r / (p+r)

    def __repr__(self):
        return "EvaluationResult({})".format(
                tuple(tuple(x) for x in self))

    def __iter__(self):
        return iter((self.prediction_comparison, self.reference_comparison))

    def __mul__(self, mul):
        return EvaluationResult((mul * x for x in self))
    __rmul__ = __mul__

    def __add__(self, other):
        return EvaluationResult((x + y for (x, y) in zip(self, other)))


############################################################


class NaiveSentenceAligner(object):
    """A very simplistic sentence-alignment algorithm.
    Assumes that the number of sentences is the same in
    both reference and in prediction corpus and that
    they appear in the same order.
    """
    def aligned_sentence_lists(self, reference, prediction):
        r"""Yield (multiplier, s_reference, s_prediction) pairs, where:
        -- `multiplier`: a number in [0,1].
        -- `s_reference`: a `Sentence` object.
        -- `s_prediction`: a `Sentence` object.

        @param reference: A list of `Sentence` objects.
        @param prediction: A list of `Sentence` objects.
        """
        return ((1, r, p) for (r, p) in zip(reference, prediction))


############################################################


class AbstractMWEEvaluator(object):
    """Base class for MWE evaluation algorithms.  A `sentence_aligner`
    is used to align sentences in corpora and the algorithm only compares
    MWEs inside aligned sentence pairs.

    Subclasses should override `compare_sentences` or use the default
    symmetrical implementation and override `_one_sided_compare` instead.
    """
    def __init__(self, sentence_aligner):
        self._sentence_aligner = sentence_aligner

    def compare_sentence_lists(self, reference, prediction):
        r"""Compare two corpora and return a EvaluationResult.
        @param reference: A list of `Sentence` objects.
        @param prediction: A list of `Sentence` objects.
        """
        ret = EvaluationResult()
        alignment = self._sentence_aligner \
                .aligned_sentence_lists(reference, prediction)
        for mul, s_ref, s_pred in alignment:
            ret += mul * self.compare_sentences(s_ref, s_pred)
        return ret

    def compare_sentences(self, s_reference, s_prediction):
        r"""Compare the `MWEOccurrence`s in both `Sentence`s
        and return an EvaluationResult.
        @param s_reference: A `Sentence` object.
        @param s_prediction: A `Sentence` object.
        """
        # Default implementation: call `_one_sided_compare`
        #   twice, for a symmetric comparison between sentences
        return EvaluationResult((
            self._one_sided_compare(s_reference, s_prediction),
            self._one_sided_compare(s_prediction, s_reference)))

    def _one_sided_compare(self, s_a, s_b):
        r"""Compare the `MWEOccurrence`s in both `Sentence`s
        and return a OneSidedComparison object.
        Subclasses do NOT need to override this method if
        `compare_sentences` has been overridden.

        @param s_a: A `Sentence` object.
        @param s_a: A `Sentence` object.
        """
        raise NotImplementedError


class ExactMatchMWEEvaluator(AbstractMWEEvaluator):
    """MWE evaluation algorithm in which each comparison has
    value 1 if two MWEs have the same indexes and 0 otherwise.
    (See `AbstractMWEEvaluator`).
    """
    def _one_sided_compare(self, s_a, s_b):
        ret = OneSidedComparison()
        indexes_a = set(tuple(mweo.indexes) for mweo in s_a.mweoccurs)
        for mweo in s_b.mweoccurs:
            ret.add(tuple(mweo.indexes) in indexes_a, 1)
        return ret


class LinkBasedMWEEvaluator(AbstractMWEEvaluator):
    """MWE evaluation algorithm in which comparisons are performed
    on each "link", where a link is a pair of consecutive tokens inside
    a MWE (See Schneider [2014] at TACL).

    The value of a link is 1 if both reference and prediction
    sentences have that link and 0 otherwise.
    (See `AbstractMWEEvaluator`).
    """
    def _one_sided_compare(self, s_a, s_b):
        ret = OneSidedComparison()
        # links_a = all links in flattened(s_a.mweoccurs.indexes)
        links_a = set(link for mweo in s_a.mweoccurs \
                for link in zip(mweo.indexes, mweo.indexes[1:]))
        for mweo_b in s_b.mweoccurs:
            for link_b in zip(mweo_b.indexes, mweo_b.indexes[1:]):
                ret.add(link_b in links_a, 1)
        return ret


###########################################################


SENTENCE_ALIGNERS = {
    "Naive": NaiveSentenceAligner,
}
MWE_EVALUATORS = {
    "ExactMatch": ExactMatchMWEEvaluator,
    "LinkBased": LinkBasedMWEEvaluator,
}


############################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global reference_fname
    global mwe_evaluator
    global corpus_filetype_ext
    global reference_filetype_ext

    sentence_aligner_class = NaiveSentenceAligner
    mwe_evaluator_class = ExactMatchMWEEvaluator

    treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o in ("-r", "--reference"):
            reference_fname = a
        elif o in ("--sentence-aligner"):
            sentence_aligner_class = SENTENCE_ALIGNERS[a]
        elif o in ("-e", "--evaluator"):
            mwe_evaluator_class = MWE_EVALUATORS[a]
        elif o == "--corpus-from":
            corpus_filetype_ext = a
        elif o == "--reference-from":
            reference_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)

    if not reference_fname:
        error("No reference file given!")

    sentence_aligner = sentence_aligner_class()
    mwe_evaluator = mwe_evaluator_class(sentence_aligner)


        
################################################################################  
# MAIN SCRIPT


if __name__ == "__main__":
    longopts = ["reference=", "sentence-aligner=", "evaluator=", "reference-from=", "corpus-from="]
    args = read_options("r:e:", longopts, treat_options, -1, usage_string)
    reference = parse_entities([reference_fname], reference_filetype_ext)
    prediction = parse_entities(args, corpus_filetype_ext)
    results = mwe_evaluator.compare_sentence_lists(reference, prediction)
    print("DEBUG:", results)
    print("Precision:", results.precision())
    print("Recall:", results.recall())
    print("F-measure:", results.f_measure())

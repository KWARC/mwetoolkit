#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# eval_automatic.py is part of mwetoolkit
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
    This script performs the automatic annotation of a candidate list according
    to a reference list (also called Gold Standard). The reference list should
    contain a manually verified list of attested Multiword Terms of the domain.
    The annotation defines a True Positive class for each candidate, which is
    True if the candidate occurs in the reference and False if the candidate is
    not in the reference (thus the candidate is probably a random word
    combination and not a MWE).

    For more information, call the script with no parameter and read the
    usage instructions.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
import sys
import re

from libs.base.tpclass import TPClass
from libs.base.candidate import Candidate
from libs.base.word import Word
from libs.base.meta_tpclass import MetaTPClass
from libs.util import read_options, treat_options_simplest, verbose, error
from libs.base.__common import WILDCARD, WORD_SEPARATOR
from libs import filetype


################################################################################
# GLOBALS

usage_string = """Usage:

python {program} -r <reference.xml> OPTIONS <candidates>

-r <reference> OR --reference <patterns>
    The reference list or gold standard, in one of the filetype
    formats accepted by the `--reference-from` switch.

The <candidates> input file must be in one of the filetype
formats accepted by the `--input-from` switch.


OPTIONS may be:

--input-from <input-filetype-ext>
    Force reading input candidates from given file type extension.
    (By default, file type is automatically detected):
    {descriptions.input[candidates]}

--reference-from <reference-filetype-ext>
    Force reading reference candidates from given file type extension.
    (By default, file type is automatically detected):
    {descriptions.input[dict]}

-c OR --case
    Make matching of a candidate against a dictionary entry case-sensitive
    (default is to ignore case in comparisons)

-g OR --ignore-pos
    Ignores Part-Of-Speech when counting candidate occurences. This means, for
    example, that "like" as a preposition and "like" as a verb will be counted
    as the same entity. Default false.

-L OR --lemma-or-surface
    Match lemma and surface of candidates each against both lemma and surface
    of references. If either of the four comparisons is successful, the match
    is successful. Wildcards in references are not considered.

{common_options}
"""
#gs = []
pre_gs = {}
fuzzy_pre_gs = {}
ignore_pos = False
lemma_or_surface = False
gs_name = None
ignore_case = True
entity_counter = 0
tp_counter = 0
ref_counter = 0

input_filetype_ext = None
reference_filetype_ext = None


################################################################################

class EvaluatorHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, None)
        self.chain.before_file(fileobj, info)

    def handle_meta(self, meta, info={}) :
        """Adds new meta-TP class corresponding to the evaluation of the candidate
        list according to a reference gold standard. Automatic evaluation is
        2-class only, the class values are "True" and "False" for true and
        false positives.

        @param meta The `Meta` header that is being read from the XML file.
        """
        global gs_name
        meta.add_meta_tpclass( MetaTPClass( gs_name, "{True,False}" ) )
        self.chain.handle_meta(meta)


    def handle_candidate(self, candidate_i, info={}) :
        """For each candidate, verifies whether it is contained in the reference
        list (in which case it is a *True* positive) or else, it is not in the
        reference list (in which case it is a *False* positive, i.e. a random
        ngram that does not constitute a MWE).

        @param candidate_i The `Candidate` that is being read from the XML file.
        """
        global ignore_pos
        global gs_name
        global ignore_case
        global entity_counter
        global tp_counter
        global pre_gs
        global lemma_or_surface
        global fuzzy_pre_gs

        true_positive = False
        #pdb.set_trace()
        candidate = Candidate( 0, [], [], [], [], [] )
        for w in candidate_i :
            copy_w = Word( w.surface, w.lemma, w.pos, w.syn, [] )
            candidate.append( copy_w )    
        
        if ignore_pos :
            candidate.set_all( pos=WILDCARD )     # reference has type Pattern
        pre_gs_key = candidate.to_string()
        if ignore_case :
            pre_gs_key = pre_gs_key.lower()
        entries_to_check = pre_gs.get( pre_gs_key, [] )

        if lemma_or_surface:
            entries_to_check += fuzzy_pre_gs.get(WORD_SEPARATOR.join([w.lemma for w in candidate]), [])
            entries_to_check += fuzzy_pre_gs.get(WORD_SEPARATOR.join([w.surface for w in candidate]), [])

        for gold_entry in entries_to_check :
            if gold_entry.match( candidate, ignore_case=ignore_case, lemma_or_surface=lemma_or_surface ) :
                true_positive = True
                break # Stop at first positive match

        if true_positive :
            candidate_i.add_tpclass( TPClass( gs_name, "True" ) )
            tp_counter = tp_counter + 1
        else :
            candidate_i.add_tpclass( TPClass( gs_name, "False" ) )
        self.chain.handle_candidate(candidate_i)
        entity_counter += 1


################################################################################

class ReferenceReaderHandler(filetype.InputHandler):
    def handle_candidate(self, reference, info={}):
        """For each entry in the reference Gold Standard, store it in main memory
        in the `pre_gs` global list. We hope that the GS is not too big. Future
        implementation should consider to use "shelve" for this.

        @param reference A `Pattern` contained in the reference Gold Standard.
        """
        global ignore_pos
        global ref_counter
        global ignore_case
        global pre_gs
        global lemma_or_surface
        global fuzzy_pre_gs
        if ignore_pos :
            reference.set_all( pos=WILDCARD )     # reference has type Pattern
        pre_gs_key = reference.to_string()
        if ignore_case :
            pre_gs_key = pre_gs_key.lower()

        pre_gs_entry = pre_gs.get( pre_gs_key, [] )
        pre_gs_entry.append( reference )
        pre_gs[ pre_gs_key ] = pre_gs_entry

        if lemma_or_surface:
            fuzzy_pre_gs.setdefault(WORD_SEPARATOR.join(
                [w.lemma for w in reference]), []).append(reference)
            fuzzy_pre_gs.setdefault(WORD_SEPARATOR.join(
                [w.surface for w in reference]), []).append(reference)

        #gs.append( reference )
        ref_counter = ref_counter + 1


################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.

        @param opts The options parsed by getopts. Ignored.

        @param arg The argument list parsed by getopts.

        @param n_arg The number of arguments expected for this script.
    """
    global pre_gs
    global ignore_pos
    global gs_name
    global ignore_case
    global lemma_or_surface
    global input_filetype_ext
    global reference_filetype_ext
    ref_name = None
    
    treat_options_simplest( opts, arg, n_arg, usage_string )    
    
    for ( o, a ) in opts:
        if o in ("-r", "--reference"):
             ref_name = a
        elif o in ("-g", "--ignore-pos"):
            ignore_pos = True
        elif o in ("-c", "--case"):
            ignore_case = False
        elif o in ("-L", "--lemma-or-surface"):
            lemma_or_surface = True
        elif o == "--input-from":
            input_filetype_ext = a
        elif o == "--reference-from":
            reference_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)
            
    # The reference list needs to be opened after all the options are read,
    # since options such as -g and -c modify the way the list is represented
    if ref_name :
        filetype.parse([ref_name], ReferenceReaderHandler(), reference_filetype_ext)
        gs_name = re.sub( ".*/", "", re.sub( "\.xml", "", ref_name ) )
    # There's no reference list... Oh oh cannot evaluate :-(
    if not pre_gs :
        error("You MUST provide a non-empty reference list!")


################################################################################
# MAIN SCRIPT

longopts = ["input-from=", "reference-from=",
        "reference=", "ignore-pos", "case", "lemma-or-surface"]
args = read_options( "r:gcL", longopts, treat_options, -1, usage_string )

filetype.parse(args, EvaluatorHandler(), input_filetype_ext)
        

precision = float( tp_counter ) / float( entity_counter )
recall = float( tp_counter ) / float( ref_counter )
if precision + recall > 0 :
    fmeas =  ( 2 * precision * recall) / ( precision + recall )
else :
    fmeas = 0.0
print("Nb. of true positives: {tp}".format(tp=tp_counter), file=sys.stderr)
print("Nb. of candidates: {ca}".format(ca=entity_counter), file=sys.stderr)
print("Nb. of references: {refs}".format(refs=ref_counter), file=sys.stderr)
print("Precision: {p}".format(p=precision), file=sys.stderr)
print("Recall: {r}".format(r=recall), file=sys.stderr)
print("F-measure: {f}".format(f=fmeas), file=sys.stderr)

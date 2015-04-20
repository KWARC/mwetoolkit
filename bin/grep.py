#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
# 
# grep.py is part of mwetoolkit
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
    Filter the elements of the input that match given pattern.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs import util
from libs import filetype
from libs.base.candidate import CandidateFactory
from libs.base.mweoccur import MWEOccurrence


################################################################################
# GLOBALS

usage_string = """Usage:

python {program} -p <patterns-file> OPTIONS <input-file>

-p <patterns-file> OR --patterns <patterns-file>
    The patterns to look for, in one of these formats:
    {descriptions.input[patterns]}

The <input-file> must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[ALL]}

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, keeps input in original format):
    {descriptions.output[ALL]}

--annotate
    Annotate matches as if they were MWEs.

-d <distance> OR --match-distance <distance>
    Select the distance through which patterns will match (default: "All"):
    * Distance "Shortest": Output the shortest matches (non-greedy).
    * Distance "Longest": Output the longest matches (greedy).
    * Distance "All": Output all match sizes.

-N OR --non-overlapping
    Do not output overlapping word matches.
    This option should not be used if match-distance is "All".

--id-order <list-of-ids>
    Output tokens in the pattern ID order given by the
    colon-separated <list-of-ids>.  The special ID "*" can be used
    to represent "all remaining IDs". Default: "*".

{common_options}
"""
input_patterns = None
input_filetype_ext = None
output_filetype_ext = None
match_distance = "All"
non_overlapping = False
id_order = ["*"]
annotate = False


################################################################################

class GrepHandler(filetype.ChainedInputHandler):
    """For each entity in the file, match it against patterns
    and output it if the match was successful.
    """
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
            self.candidate_factory = CandidateFactory()
            self.global_dict = {}
        self.chain.before_file(fileobj, info)
        
    def handle_candidate(self, original_cand, info={}):
        if list(self._iter_matches(original_cand)):
            self.chain.handle(original_cand, info)

    def handle_sentence(self, sentence, info={}):
        matched = False
        for match_ngram, wordnums in self._iter_matches(sentence):
            matched = True
            if not annotate: break
            cand = self.candidate_factory.make_uniq(match_ngram)
            cand.add_sources("{}:{}".format(sentence.id_number,
                    ",".join(unicode(wn+1) for wn in wordnums)))
            mweo = MWEOccurrence(sentence, cand, wordnums)
            sentence.mweoccurs.append(mweo)

        if matched:
            self.chain.handle(sentence, info)


    def _iter_matches(self, entity):
        for pattern in input_patterns:
            for (match_ngram, wordnums) in pattern.matches(entity,
                    match_distance=match_distance, id_order=id_order,
                    overlapping=not non_overlapping):
                yield match_ngram, wordnums


################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.
    """
    global input_patterns
    global input_filetype_ext
    global output_filetype_ext
    global match_distance
    global non_overlapping
    global id_order
    global annotate

    util.treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o == "--input-from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        elif o in ("-p", "--patterns"):
            input_patterns = filetype.parse_entities([a])
        elif o in ("-d", "--match-distance") : 
            match_distance = a
        elif o in ("-N", "--non-overlapping") : 
            non_overlapping = True
        elif o == "--id-order":
            id_order = a.split(":")
        elif o == "--annotate":
            annotate = True
        else:
            raise Exception("Bad arg " + o)

    if input_patterns is None:
        util.error("No patterns provided. Option --patterns is mandatory!")


################################################################################
# MAIN SCRIPT

longopts = ["input-from=", "to=", "patterns=",
        "match-distance=", "non-overlapping=", "id-order=", "annotate"]
args = util.read_options("p:d:N", longopts, treat_options, -1, usage_string)
filetype.parse(args, GrepHandler(), input_filetype_ext)

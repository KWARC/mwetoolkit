#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# candidates.py is part of mwetoolkit
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
    This script extract Multiword Expression candidates from a raw corpus in 
    valid XML (mwetoolkit-corpus.dtd) and generates a candidate list in valid 
    XML (mwetoolkit-candidates.dtd). There are two possible extraction methods: 
    the -p option assumes that you have a patterns file in which you define 
    shallow morphosyntactic patterns (e.g. I want to extract Verb + Preposition
    pairs); the -n option assumes that you do not care about the type of the
    candidates and that you are trying to extract all possible ngrams from the
    corpus. The latter should only be used as a backoff strategy when you do not
    know anything about the corpus or language: do not expect to obtain 
    impressive results with it. Notice that in the -n option, ngrams are not
    extracted across sentence borders, since these would certainly not be
    interesting MWE candidates.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re
import shelve
import os
import tempfile

from libs.base.__common import WILDCARD, TEMP_PREFIX, TEMP_FOLDER
from libs.base.frequency import Frequency
from libs.base.candidate import Candidate
from libs.base.ngram import Ngram
from libs.util import read_options, treat_options_simplest, error, verbose,\
    interpret_ngram, warn
from libs.filetype.patternlib import build_generic_pattern
#from libs.filetype.indexlib import Index
from libs.base.meta import Meta
from libs import filetype


################################################################################
# GLOBALS

usage_string = """Usage: 
    
python {program} [-n <min>:<max> | -p <patterns-file>] OPTIONS <corpus>

-p <patterns-file> OR --patterns <patterns-file>
    The patterns to extract, in one of these formats:
    {descriptions.input[patterns]}

-n <min>:<max> OR --ngram <min>:<max>
    The length of ngrams to extract. For instance, "-n 3:5" extracts ngrams 
    that have at least 3 words and at most 5 words. If you define only <min> or
    only <max>, the default is to consider that both have the same value, i.e. 
    if you call the program with the option "-n 3", you will extract only 
    trigrams while if you call it with the options "-n 3:5" you will extract 
    3-grams, 4-grams and 5-grams. The value of <min> must be at least 1.

You must choose either the -p option or the -n option
(both are not allowed at the same time).

The <corpus> input file must be in one of the filetype
formats accepted by the `--from` switch.
    

OPTIONS may be:

-i OR --index
    (Deprecated. We currently detect BinaryIndex files automatically.
    To force detection, use --from=BinaryIndex.)

--from <input-filetype-ext>
    Force reading from given file type extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}

--to <output-filetype-ext>
    Output extracted candidates in given filetype format
    (By default, outputs in "XML" candidate format):
    {descriptions.output[candidates]}

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
     
-f OR --freq     
    Output the count of the candidate. This counter will merge the candidates if
    more than one pattern matches it, considering it as a single entry. The 
    counts of individual words in the candidate are NOT output by this option,
    you must use counter.py for this. Default false.

-g OR --ignore-pos
     Ignores parts of speech when counting candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be counted 
     as the same entity. Default false.

-s OR --surface
    Counts surface forms instead of lemmas. Default false.

-S OR --source
    Output a <source> tag with the IDs of the sentences where each ngram occurs.
    The syntax is `ID_A:w1,w2,w3...wN;ID_B:w1,w2...;ID_K:w1,w2...`.
    Example: "158:48,49;455:8,9".

{common_options}
"""
patterns = []
ignore_pos = False
match_distance = "All"
non_overlapping = False
surface_instead_lemmas = False
print_cand_freq = False
longest_pattern = 0
shortest_pattern = float("inf")
print_source = False
id_order = ["*"]

input_filetype_ext = None
output_filetype_ext = None


################################################################################
       
class CandidatesGeneratorHandler(filetype.InputHandler):
    r"""An InputHandler that generates Candidates."""

    def handle_sentence(self, sentence, info={}):
        """For each sentence in the corpus, generates all the candidates that match
        at least one pattern in the patterns file (-p option) or all the
        ngrams that are in the valid range (-n option). The candidates are
        stored into a temporary file and will be further printed to a XML file.
        The temp file is used to avoid printing twice a repeated candidate and
        to count occurrences of the same candidate.
        
        @param sentence A `Sentence` that is being read from the XML file.    
        """
        global patterns, temp_file, ignore_pos, surface_instead_lemmas, \
               longest_pattern, shortest_pattern

        already_matched = set()

        for pattern in patterns:
            for (match_ngram, wordnums) in pattern.matches(sentence,
                    match_distance=match_distance, id_order=id_order,
                    overlapping=not non_overlapping):
                wordnums_string = ",".join( map( str, wordnums ) )
                if wordnums_string in already_matched:
                    continue
                already_matched.add( wordnums_string )

                #match_ngram = Ngram(copy_word_list(ngram), [])

                if ignore_pos :    
                    match_ngram.set_all( pos=WILDCARD )
                internal_key = unicode( match_ngram.to_string() ).encode('utf-8')

                if( surface_instead_lemmas ) :
                    match_ngram.set_all( lemma=WILDCARD )
                else :
                    match_ngram.set_all( surface=WILDCARD )                    
                key = unicode( match_ngram.to_string() ).encode('utf-8')
                ( surfaces_dict, total_freq ) = temp_file.get( key, ( {}, 0 ) )
                freq_surface = surfaces_dict.setdefault( internal_key, [] )

                # Append the id of the source sentence. The number of items in
                # surfaces_dict[form] is the number of occurrences of that form.
                source_sent_id = str( sentence.id_number ) + ":" + wordnums_string
                surfaces_dict[ internal_key ].append( source_sent_id )
                temp_file[ key ] = ( surfaces_dict, total_freq + 1 )


    def after_file(self, fileobj, info={}):
        ext = output_filetype_ext or "XML"
        chain = filetype.printer_class(ext)("candidates")
        chain.before_file(fileobj, info)
        #import pdb
        #pdb.set_trace()
        chain.handle_meta(Meta([],[],[]), info)
        self.print_candidates(chain, fileobj.name, info)
        chain.after_file(fileobj, info)


    def print_candidates(self, chain, filename, info):
        """Prints a XML file (mwetoolkit-candidates.dtd) from a temporary 
        candidates file generated by the treat_sentence callback function. 
        Repeated candidates are not printed several times: instead, each base 
        form has a joint frequency of the candidate in the corpus. Since the
        new version of the "count.py" script, this initial frequency is only
        printed if you explicitely ask to do it through the -f option.

        @param filename: The file name of the corpus from which we generate the
        candidates.
        """
        global print_cand_freq, print_source, temp_file
        corpus_name = re.sub( ".*/", "", re.sub( "\.(xml|info)", "", filename ) )
        verbose("Outputting candidates file...")
        #chain.handle_meta(Meta([],[],[]))
        id_number = 0        
        for base_string in temp_file.keys() :
            (surface_dict, total_freq) = temp_file[ base_string ]
            cand = Candidate( id_number, [], [], [], [], [] )
            cand.from_string( unicode( base_string, 'utf-8' ) )
            if print_cand_freq :
               freq = Frequency( corpus_name, total_freq )
               cand.add_frequency( freq )
            id_number = id_number + 1                        
            for occur_string in surface_dict.keys() :
                occur_form = Ngram( [], [] )
                occur_form.from_string( unicode(occur_string, 'utf-8') )
                sources = surface_dict[occur_string]
                freq_value = len(sources)
                freq = Frequency( corpus_name, freq_value )
                occur_form.add_frequency( freq )
                if print_source:
                    occur_form.add_sources(sources)
                cand.add_occur( occur_form )
            chain.handle_candidate(cand, info)

        
################################################################################  

def create_patterns_file( ngram_range ) :
    """
        Create an artificial list of MWE patterns in which all the parts of
        the words are wildcards. Such artificial patterns match every ngram
        of size n, which is exactly what we want to do with the option -n. This
        may seem a weird way to extract ngrams, but it allows a single 
        transparent candidate extraction function, treat_sentence.
        
        @param ngram_range String argument of the -n option.
    """        
    global patterns, usage_string, shortest_pattern, longest_pattern
    result = interpret_ngram( ngram_range )
    if result :
        ( shortest_pattern, longest_pattern ) = result
        patterns.append(build_generic_pattern(shortest_pattern, longest_pattern))
    else :
        error("Invalid argument for -n.")

################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global patterns
    global ignore_pos
    global surface_instead_lemmas
    global print_cand_freq
    global print_source
    global match_distance
    global non_overlapping
    global input_filetype_ext
    global output_filetype_ext
    global id_order
    
    treat_options_simplest( opts, arg, n_arg, usage_string )
        
    mode = []
    patterns_file = None
    for ( o, a ) in opts:
        if o in ("-p", "--patterns") : 
            mode.append( "patterns" )
            patterns_file = a
        elif o in ( "-n", "--ngram" ) :
            create_patterns_file( a )
            mode.append( "ngram" )
        elif o in ("-g", "--ignore-pos") : 
            ignore_pos = True
        elif o in ("-d", "--match-distance") : 
            match_distance = a
        elif o in ("-N", "--non-overlapping") : 
            non_overlapping = True
        elif o in ("-s", "--surface") : 
            surface_instead_lemmas = True
        elif o in ("-S", "--source") :
            print_source = True
        elif o in ("-f", "--freq") : 
            print_cand_freq = True
        elif o in ("-i", "--index") :
            input_filetype_ext = "BinaryIndex"
            warn("Option -i is deprecated; use --from=BinaryIndex")
        elif o == "--id-order":
            id_order = a.split(":")
        elif o == "--from" :
            input_filetype_ext = a
        elif o == "--to" :
            output_filetype_ext = a
        else:
            raise Exception("Bad flag")

    if non_overlapping and match_distance == "All":
        # If we are taking all matches, we need to be able to overlap...
        error("Conflicting options: --match-distance=All and --non-overlapping")

    if len(mode) != 1 :
        error("Exactly one option, -p or -n, must be provided")
    if "patterns" in mode:
        global patterns
        patterns = filetype.parse_entities([patterns_file])

################################################################################  
# MAIN SCRIPT

longopts = [ "from=", "to=", "patterns=", "ngram=", "index", "match-distance=",
        "non-overlapping", "freq", "ignore-pos", "surface", "source",
        "id-order=" ]
arg = read_options( "p:n:id:NfgsS", longopts, treat_options, -1, usage_string )

with tempfile.NamedTemporaryFile(
        prefix=TEMP_PREFIX, dir=TEMP_FOLDER) as temp_fh:
    temp_name = temp_fh.name

from contextlib import closing
with closing(shelve.open( temp_name, 'n' )) as temp_file :
    filetype.parse(arg, CandidatesGeneratorHandler(), input_filetype_ext)

# Try to remove temp file, if the system didn't do it automatically
try :
    os.remove(temp_fh.name)
except OSError :
    os.remove( temp_fh.name + ".db" ) # Some dbms used by shelve add the
   # .db suffix to the file
except IOError as err :
    error(str(err)+"\nError closing temporary file.\n"
                   "Please verify __common.py configuration")

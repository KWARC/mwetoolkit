#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# lowercase.py is part of mwetoolkit
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
   This script homogenises the case of a corpus. Two possible lowercasing 
   algorithms are proposed: simple and complex. The former lowercases 
   everything, regardless of acronyms, proper names, dates, etc. The latter 
   keeps the case of words that do not present a preferred form, i.e. words that 
   might occur uppercased even if they are not at the beginning of a sentence. 
   Some fuzzy thresholds are hardcoded and were fixed based on empirical 
   observation of the Genia corpus. Since you are supposed to perform 
   lowercasing before any linguistic processing, this script operates on surface 
   forms. Any lemma information will be ignored during lowercasing, unless you
   use -l option.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re

from libs.base.word import Word
from libs.util import read_options, treat_options_simplest, \
        verbose, warn, error
from libs import filetype


################################################################################
# GLOBALS

usage_string = """Usage: 
    
python {program} OPTIONS <corpus>

The <corpus> input file must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, keeps input in original format):
    {descriptions.output[corpus]}

-a OR --algorithm
    The name of the lowercasing algorithm used to convert from upper to 
    lowercase characters. Supported algorithms are:
    * "simple" (default): lowercases everything, regardless of acronyms, proper 
      names, dates, etc.
    * "complex": keeps the case of words that do not present a preferred form, 
      i.e. words that might occur uppercased even if they are not at the beginning 
      of a sentence. Some fuzzy thresholds are hardcoded and were fixed based on
      empirical observation of the Genia corpus.
    * "aggressive": lowercases all words that do not occur more than 90% of the
      time in upper/mixed case. For instance, if a word never appears in lowercase,
      it will be kept. Words that occur in various cases will be lowercased.

-l OR --lemmas
    Lowercase lemmas instead of surface forms. Might be useful when dealing with
    corpora which were accidentally parsed before lowercasing, and the parser
    doesn't lowercase lemmas (as it is the case in RASP 2, for instance)

-x OR --text
    DEPRECATED: Use --from=PlainCorpus instead.

-m OR --moses
    DEPRECATED: Use --from=Moses instead.

{common_options}

IMPORTANT: you are supposed to perform lowercasing before any linguistic
processing. Therefore, this algorithm operates on surface forms by default. 
Except if you specify the -l option, lemmas will be ignored during 
lowercasing.
"""

algoname = "simple"
vocab = {}
# In complex algorithm, a Firstupper form occurring 80% of the time or more 
# at the beginning of a sentence is systematically lowercased.
START_THRESHOLD=0.8
lower_attr="surface"

input_filetype_ext = None
output_filetype_ext = None


################################################################################

class LowercaserHandler(filetype.ChainedInputHandler):
    def __init__(self):
        global algoname
        if algoname == "simple" : 
            self.handle_sentence = self.handle_sentence_simple # Redundant, kept for clarity
        elif algoname == "complex" :
            self.handle_sentence = self.handle_sentence_complex
        elif algoname == "aggressive" :
            self.handle_sentence = self.handle_sentence_aggressive # Redundant, kept for clarity                
        else :
            error("%s is not a valid algorithm\nYou must provide a valid "+\
                  "algorithm (e.g. \"complex\", \"simple\")." % algoname)


    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)


    def handle_sentence_simple(self, sentence, info={}):
        """For each sentence in the corpus, lowercases
        its words in a dummy stupid way.
        """
        global text_version
        global moses_version
        global lower_attr
        
        for w in sentence :
            setattr(w, lower_attr, getattr(w, lower_attr).lower())
        self.chain.handle_sentence(sentence, info)


    def handle_sentence_complex(self, sentence, info={}):
        """For each sentence in the corpus, lowercases its words
        based on the most frequent form in the vocabulary.
        """    
        global vocab
        global START_THRESHOLD    
        global lower_attr
        
        for w_i, w in enumerate(sentence):
            case_class = w.get_case_class()
            # Does nothing if it's already lowercase or if it's not alphabetic

            if case_class != "lowercase" and case_class != "?":
                low_key = getattr(w, lower_attr).lower()
                token_stats = vocab[ low_key ]
                percents = get_percents( token_stats )
                pref_form = get_preferred_form( percents )

                if case_class == "UPPERCASE" or case_class == "MiXeD" :
                    if pref_form :
                        setattr( w, lower_attr, pref_form ) 
                        # If the word is UPPERCASE or MiXed and does not have a 
                        # preferred form, what do you expect me to do about it? 
                        # Nothing, I just ignore it, it's a freaky weird creature!   

                elif case_class == "Firstupper" :
                    occurs = token_stats[ getattr( w, lower_attr) ]
                    if ( w_i == 0 or
                       re.match( "[:\.\?!;]", sentence[ w_i - 1 ].surface ) ) and \
                       float(occurs[ 1 ]) / float(occurs[ 0 ]) >= START_THRESHOLD :
                        setattr( w, lower_attr, getattr( w, lower_attr ).lower() )  
                    elif pref_form :
                        setattr( w, lower_attr, pref_form )
                        # Else, don't modify case, since we cannot know whether it
                        # is a proper noun, a sentence start, a title word, a spell 
                        # error, etc.

        self.chain.handle_sentence(sentence)


    def handle_sentence_aggressive(self, sentence, info={}):
        """For each sentence in the corpus, lowercases its words except if it 
        occurs in uppercase in 90% of the occurrences.
        """    
        global vocab
        global lower_attr
        
        AGG_THRESH = .9
        
        for w_i, w in enumerate(sentence):
            case_class = w.get_case_class(s_or_l=lower_attr)
            # Does nothing if it's aready lowercase or if it's not alphabetic

            if case_class != "lowercase" and case_class != "?" :
                current_form = getattr( w, lower_attr ) 
                #if current_form == "Advance" or current_form == "Abstract" :
                #    pdb.set_trace()
                token_stats = vocab[ current_form.lower() ]
                percents = get_percents( token_stats )
                if percents[ current_form ] < AGG_THRESH :
                    setattr( w, lower_attr, current_form.lower() )          

        self.chain.handle_sentence(sentence, info)


################################################################################

class VocabReaderHandler(filetype.InputHandler):
    def handle_sentence(self, sentence, info={}):
        """
            For each sentence in the corpus, add it to the vocabulary. The vocab is
            a global dictionary that contains, for each lowercased surface form, a
            dictionary that associate the case configurations to occurrence counters
            both general and start-of-sentence (see below).
        """
        global vocab
        global lower_attr
        prev_key = ""
        for w_i, w in enumerate(sentence):
            key = getattr(w, lower_attr)
            low_key = key.lower()
            forms = vocab.get( low_key, {} )
            form_entry = forms.get( key, [ 0, 0 ] )
            # a form entry has two counters, one for the occurrences and one for
            # the number of times it occurred at the beginning of a sentence. 
            # Therefore, form_entry[0] >= form_entry[1]
            form_entry[ 0 ] = form_entry[ 0 ] + 1  
            # This form occurrs at the first position of the sentence or after a
            # period (semicolon, colon, exclamation or question mark). Count it
            if w_i == 0 or re.match( "[:\.\?!;]", prev_key ) :
                form_entry[ 1 ] = form_entry[ 1 ] + 1 
            forms[ key ] = form_entry
            vocab[ low_key ] = forms
            prev_key = key


################################################################################

def get_percents( token_stats ) :
    """
        Given a vocabulary entry for a given word key, returns a dictionary 
        containing the corresponding percents, i.e. the proportion of a given
        occurrence wrt to all occurrences of that word. For instance:
        `token_stats` = { "The": 100, "the": 350, "THE": 50 } will return 
        { "The": .2, "the": .7, "THE": .1 } meaning that the word "the" occurrs
        20% of the times in Firstupper configuration, 70% in lowercase and 10% 
        in UPPERCASE. The sum of all dictionary values in the result is 1.
        
        Forms occurring at the beginning of a sentence or after a period are
        ignored, since they might have case modifications due to their position.
        
        @param token_stats A vocabulary entry that associates case 
        configurations to an integer number of occurrences.
        
        @param token_stats A dictionary that associates case configurations to 
        a float percent value equal to the number of occurrences of that 
        configuration divided by the total number of occurrences of that word.
       
    """
    percents = {}
    total_count = 0
    for a_form in token_stats.keys() :
        count = percents.get( a_form, 0 )
        count_notstart = token_stats[ a_form ][ 0 ] - token_stats[ a_form ][ 1 ]
        # Smoothing to avoid division by zero (occurs ONLY in first position)
        # Add-one smoothing is simple and solves the problem
        count_notstart += 1
        count = count + count_notstart
        percents[ a_form ] = count
        total_count = total_count + count_notstart
    for a_form in percents.keys() :
        if total_count != 0 :
            percents[ a_form ] = percents[ a_form ] / float(total_count)
        else :
            warn("Percents cannot be calculated for non-occurring words!")
    return percents

################################################################################

def get_preferred_form( percents ) :
    """
        Given a percents array generated by the function above, returns the form
        that occurrs most frequently. Besides of being the most frequent form,
        the preferred form must also occur above the threshold t defined by the
        formula t=0.9-0.1*len(percents). For example, if there are two possible
        forms, t=0.7, with three possible forms, t=.6 and so on. If no form 
        respects the threshold criterium, the result is None. This means that no
        form is preferred above the others.
        
        @param percents A dictionary that associates case configurations to
        percents, as defined by the function above.
        
        @return A string that corresponds to the preferred forms among the keys
        of `percents`, None if the forms are too homogeneously distributed.
    """
    # If a given forms occurrs 70% of the cases (for 2 forms) or more, it is 
    # considered preferred
    # TODO: Test an entropy-based measure for choosing among the forms
    PRED_THRESHOLD = .9 - .15 * len(percents)
    max_like = (0, None)
    for form in percents.keys() :
        if percents[form] >= PRED_THRESHOLD and percents[form] > max_like[0]:
            max_like = (percents[ form ], form )
    return max_like[ 1 ] # No preferred form
    
################################################################################    
    
def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global algoname
    global lower_attr
    global input_filetype_ext
    global output_filetype_ext

    treat_options_simplest( opts, arg, n_arg, usage_string )        

    for ( o, a ) in opts:
        if o == "--from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        elif o in ("-l","--lemmas" ) :
            lower_attr = "lemma"
        elif o in ("-a", "--algorithm"):
            algoname = a.lower()
        else:
            raise Exception("Bad arg: " + o)

 
################################################################################
# MAIN SCRIPT

longopts = [ "from=", "to=", "algorithm=", "lemmas" ]
args = read_options( "a:xml", longopts, treat_options, 1, usage_string )

if algoname != "simple" :
    verbose( "Pass 1: Reading vocabulary from file... please wait" )
    filetype.parse(args, VocabReaderHandler(), input_filetype_ext)

verbose( "Pass 2: Lowercasing the words in the file" )
filetype.parse(args, LowercaserHandler(), input_filetype_ext)

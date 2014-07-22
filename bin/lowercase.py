#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
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
   forms. Any lemma information will be ignored during lowercasing, except you
   use -l option.
"""

import sys
import xml.sax
import pdb
import re
import operator

from xmlhandler.genericXMLHandler import GenericXMLHandler
from xmlhandler.classes.word import Word
from util import usage, read_options, treat_options_simplest, verbose, \
                 parse_xml, parse_txt

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s [OPTIONS] <file.xml>

    OPTIONS may be:    
    
-a OR --algorithm
    The name of the lowercaisng algorithm used to convert majuscule to 
    minuscule characters. Supported algorithms are:
    * simple (default): lowercases everything, regardless of acronyms, proper 
    names, dates, etc.
    * complex: keeps the case of words that do not present a preferred form, 
    i.e. words that might occur uppercased even if they are not at the beginning 
    of a sentence. Some fuzzy thresholds are hardcoded and were fixed based on
    empirical observation of the Genia corpus.
    
-x OR --text
    Use as input a text file instead of XML file. One sentence per line, 
    tokenised with spaces. Output will be text as well.
    
-m OR --moses
    Uses Moses factored corpus format as input. This format must be pure text,
    one sentence per line, tokens separated by spaces, each token being:
    surface|lemma|POS|syntrelation:synthead
    Which are equivalent to the xml fields. Empty fields should be left blank,
    but every token must have 3 vertical bars. The actual character for vertical
    bars must be escabed and replaced by a placeholder that does not contain
    this character (e.g. %%VERTICAL_BAR%%)
    
-l OR --lemmas
	Lowercase lemmas instead of surface forms. Might be useful when dealing with
	corpora which were accidentally parsed before lowercasing, and the parser
	doesn't lowercase lemmas (as it is the case in RASP 2, for instance)

%(common_options)s

    IMPORTANT: you are supposed to perform lowercasing before any linguistic
    processing. Therefore, this algorithm operates on surface forms by default. 
    Except if you specify the -l option, lemmas will be ignored during 
    lowercasing.

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""
algorithm = None
vocab = {}
entity_counter = 0
# In complex algorithm, a Firstupper form occurring 80% of the time or more 
# at the beginning of a sentence is systematically lowercased.
START_THRESHOLD=0.8
text_version=False
moses_version=False
lower_attr="surface"

################################################################################

def treat_meta( meta ) :
    """
        Simply prints the meta header to the output without modifications.

        @param meta The `Meta` header that is being read from the XML file.
    """

    print meta.to_xml().encode( 'utf-8' )
    
################################################################################

def treat_sentence_simple( sentence ) :
    """
        For each sentence in the corpus, lowercases its words in a dummy stupid
        way.
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """
    global entity_counter
    global text_version
    global moses_version
    global lower_attr
    
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )
    new_sent = []
    for w in sentence :
        if text_version :
            new_sent.append( w.lower() )
        elif moses_version :
        	word = w.split( "|" )
        	if lower_attr == "lemma" : # option --lemmas passed
        		word[1] = word[1].lower()
        	else :
        		word[0] = word[0].lower()
        	new_sent.append( "|".join( word ) )
        else :
            setattr(w, lower_attr, getattr(w, lower_attr).lower() )
    if text_version or moses_version :
        print " ".join( new_sent )
    else :
        print sentence.to_xml().encode( "utf-8" )
    entity_counter += 1

################################################################################

def treat_sentence_complex( sentence ) :
    """
        For each sentence in the corpus, lowercases its words based on the most
        frequent form in the vocabulary.
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """    
    global vocab
    global entity_counter
    global START_THRESHOLD    
    global text_version
    global moses_version
    global lower_attr
    
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )

    for w_i in range(len(sentence)) :
        if text_version :
            sentence[ w_i ] = Word( sentence[ w_i ], None, None, None, None )
        elif moses_version :
            parts = sentence[ w_i ].split("|")
            if len(parts) != 4 :
                print >> sys.stderr, "WARNING: malformed token %s" % \
                                     sentence[ w_i ]
                print >> sys.stderr, "Ignoring sentence %d" % entity_counter
                return
            sentence[ w_i ] = Word(parts[0], parts[1], parts[2], parts[3], None)
        w = sentence[ w_i ]
        case_class = w.get_case_class()
        # Does nothing if it's aready lowercase or if it's not alphabetic
        
        if case_class != "lowercase" and case_class != "?" :
            low_key = getattr( w, lower_attr).lower()            
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
                if ( w_i == 0 or \
                   re.match( "[:\.\?!;]", sentence[ w_i - 1 ].surface ) ) and \
                   float(occurs[ 1 ]) / float(occurs[ 0 ]) >= START_THRESHOLD :
                    setattr( w, lower_attr, getattr( w, lower_attr ).lower() )  
                elif pref_form :
                    setattr( w, lower_attr, pref_form )
                    # Else, don't modify case, since we cannot know whether it
                    # is a proper noun, a sentence start, a title word, a spell 
                    # error, etc.

    if text_version :
    	print " ".join( map( lambda x : getattr( x, lower_attr), sentence ) )
    elif moses_version :
    	print " ".join( map( lambda x : x.to_moses(), sentence ) )    	
    else :
        print sentence.to_xml().encode( 'utf-8' )
    entity_counter += 1

################################################################################
       
def build_vocab( sentence ) :
    """
        For each sentence in the corpus, add it to the vocabulary. The vocab is
        a global dictionary that contains, for each lowercased surface form, a
        dictionary that associate the case configurations to occurrence counters
        both general and start-of-sentence (see below).
        
        @param sentence A `Sentence` that is being read from the XML file. If
        text_version, then it is simply a list of string tokens    
    """
    global vocab
    global entity_counter
    global text_version
    global moses_version
    global lower_attr
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )
    prev_key = ""
    for w_i in range(len(sentence)) :
        if text_version :
            key = sentence[ w_i ]
        elif moses_version :
            fields = sentence[ w_i ].split( "|" )
            if lower_attr == "surface" :
                key = fields[0]
            elif lower_attr == "lemma" :
                key = fields[1]
            else : # Will never occur
                print >> sys.stderr, "ERROR: unkown attrbute %s" % lower_attr
                exit(-1)
        else :
            key = getattr( sentence[ w_i ], lower_attr )
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
    entity_counter += 1
    
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
        count = percents.get( a_form, 0 );
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
            print >> sys.stderr, "ERROR: Percents cannot be calculated for " \
                                 "non-occurring words!"
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
    PRED_THRESHOLD = .9 - 0.1 * len(percents)
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
    global algorithm
    global text_version
    global moses_version
    global lower_attr
    algorithm = treat_sentence_simple # Default value
    treat_options_simplest( opts, arg, n_arg, usage_string )        
    for ( o, a ) in opts:
        if o in ("-x", "--text" ) :
            text_version = True
        elif o in ("-m", "--moses" ) :       
            moses_version = True    
        elif o in ("-l","--lemmas" ) :
            lower_attr = "lemma"
        elif o in ("-a", "--algorithm"):
            algoname = a.lower()
            if algoname == "complex" :
                algorithm = treat_sentence_complex
            elif algoname == "simple" : 
                algorithm = treat_sentence_simple # Redundant, kept for clarity
            else :
                print >> sys.stderr, "ERROR: " + algoname + " is not a valid"+\
                                     " algorithm"
                print >> sys.stderr, "ERROR: You must provide a valid " + \
                                     "algorithm (e.g. \"complex\", \"simple\")."
                usage( usage_string )
                sys.exit( 2 )  
 
################################################################################
# MAIN SCRIPT

longopts = [ "algorithm=", "text", "moses", "lemmas" ]
arg = read_options( "a:xml", longopts, treat_options, 1, usage_string )

if algorithm == treat_sentence_complex :
    verbose( "Pass 1: Reading vocabulary from file... please wait" )
    if text_version or moses_version :
        parse_txt( build_vocab, arg )
    else :
        parse_xml( GenericXMLHandler( treat_entity=build_vocab ), arg )
    entity_counter = 0
    
verbose( "Pass 2: Lowercasing the words in the file" )
if text_version or moses_version :
    parse_txt( algorithm, arg )
else :
    handler = GenericXMLHandler( treat_meta=treat_meta,
                                 treat_entity=algorithm,
                                 gen_xml=True )
    parse_xml( handler, arg )
    print handler.footer

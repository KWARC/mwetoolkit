#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
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
   forms. Any lemma information will be ignored during lowercasing.
"""

import sys
import xml.sax

import install
from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import usage, read_options, treat_options_simplest, verbose

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

-v OR --verbose
    Print friendly messages that explain what is happening.

    IMPORTANT: you are supposed to perform lowercasing before any linguistic
    processing. Therefore, this algorithm operates on surface forms. Any lemma
    information will be ignored during lowercasing.

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""
algorithm = "simple"
vocab = {}
sentence_counter = 0
# In complex algorithm, a Firstupper form occurring 80% of the time or more 
# at the beginning of a sentence is systematically lowercased.
START_THRESHOLD=0.8

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
    global sentence_counter
    
    if sentence_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":sentence_counter } )

    for w in sentence :
        w.surface = w.surface.lower()
    print sentence.to_xml().encode( "utf-8" )
    sentence_counter += 1

################################################################################

def treat_sentence_complex( sentence ) :
    """
        For each sentence in the corpus, lowercases its words based on the most
        frequent form in the vocabulary.
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """    
    global vocab, sentence_counter, START_THRESHOLD    
    if sentence_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":sentence_counter } )
    
    for w_i in range(len(sentence)) :
        w = sentence[ w_i ]
        case_class = get_case_class( w.surface )          
        # Does nothing if it's aready lowercase or if it's not alphabetic
        if case_class != "lowercase" and case_class != "?" :
            low_key = w.surface.lower()            
            token_stats = vocab[ low_key ]
            percents = get_percents( token_stats )
            pref_form = get_preferred_form( percents )
            if case_class == "UPPERCASE" or case_class == "MiXeD" :
                if pref_form :
                    w.surface = pref_form
                    # If the word is UPPERCASE or MiXed and does not have a 
                    # preferred form, what do you expect me to do about it? 
                    # Nothing, I just ignore it, it's a freaky weird creature!   
            elif case_class == "Firstupper" :
                occurs = token_stats[ w.surface ]
                if w_i == 0 and \
                   float(occurs[ 1 ]) / float(occurs[ 0 ]) >= START_THRESHOLD :
                    w.surface = w.surface.lower()
                elif pref_form :
                    w.surface = pref_form
                    # Else, don't modify case, since we cannot know whether it
                    # is a proper noun, a sentence start, a title word, a spell 
                    # error, etc.                   
    print sentence.to_xml().encode( 'utf-8' )
    sentence_counter += 1

################################################################################
       
def build_vocab( sentence ) :
    """
        For each sentence in the corpus, add it to the vocabulary. The vocab is
        a global dictionary that contains, for each lowercased surface form, a
        dictionary that associate the case configurations to occurrence counters
        both general and start-of-sentence (see below).
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """
    global vocab, sentence_counter
    if sentence_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":sentence_counter } )
    for w_i in range(len(sentence)) :
        key = sentence[ w_i ].surface        
        low_key = sentence[ w_i ].surface.lower()
        forms = vocab.get( low_key, {} )
        form_entry = forms.get( key, [ 0, 0 ] )
        # a form entry has two counters, one for the occurrences and one for
        # the number of times it occurred at the beginning of a sentence. 
        # Therefore, form_entry[0] >= form_entry[1]
        form_entry[ 0 ] = form_entry[ 0 ] + 1  
        # This form occurrs at the first position of the sentence. Count it
        if w_i == 0 :
            form_entry[ 1 ] = form_entry[ 1 ] + 1 
        forms[ key ] = form_entry
        vocab[ low_key ] = forms
    sentence_counter += 1
    
################################################################################  

def get_case_class( token ) :
    """
        For a given token, assigns a class that can be:        
        * lowercase - All characters are lowercase
        * UPPERCASE - All characters are uppercase
        * Firstupper - All characters are lowercase except for the first
        * MiXeD - This token contains mixed lowercase and uppercase characters
        * ? - This token contains non-alphabetic characters
        
        @param A string that corresponds to a raw token of the corpus.
        
        @return A string that describes the case class according to the list 
        above.
    """
    token_list = list( token )
    case_class = "?"
    for letter_i in range( len( token_list ) ) :
        letter = token_list[ letter_i ]
        if letter.isupper() :
            if letter_i > 0 :
                if case_class == "lowercase" or case_class == "Firstupper" :
                    case_class = "MiXeD"
                elif case_class == "?" :
                    case_class = "UPPERCASE"    
            else :
                case_class = "UPPERCASE"                
        elif letter.islower() :
            if letter_i > 0 :                
                if case_class == "UPPERCASE" :
                    if letter_i == 1 :
                        case_class = "Firstupper"
                    else :
                        case_class = "MiXeD"
                elif case_class == "?" :
                    case_class = "lowercase"
            else :
                case_class = "lowercase"
    return case_class        

################################################################################

def get_percents( token_stats ) :
    """
        Given a vocabulary entry for a given word key, returns a dictionary 
        containing the corresponding percents, i.e. the proportion of a given
        occurrence wrt to all occurrences of that word. For instance:
        `token_stats` = { "The": 100, "the": 350, "THE": 50 } will return 
        { "The": .2, "the": .7, "THE": .1 } meaninf that the word "the" occurrs
        20% of the times in Firstupper configuration, 70% in lowercase and 10% 
        in UPPERCASE. The sum of all dictionary values in the result is 1.
        
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
        count = count + token_stats[ a_form ][ 0 ]
        percents[ a_form ] = count
        total_count = total_count + token_stats[ a_form ][ 0 ]
    for a_form in percents.keys() :
        percents[ a_form ] = percents[ a_form ] / float(total_count)
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
    for ( o, a ) in opts:
        if o in ("-a", "--algorithm"):
            algorithm = a.lower()
            if algorithm != "simple" and algorithm != "complex" :
                print >> sys.stderr, "ERROR: " + algorithm + " is not a valid"+\
                                     " algorithm"
                print >> sys.stderr, "ERROR: You must provide a valid " + \
                                     "algorithm (e.g. \"complex\", \"simple\")."
                usage( usage_string )
                sys.exit( 2 )    
            
    treat_options_simplest( opts, arg, n_arg, usage_string )      
    
################################################################################
# MAIN SCRIPT

longopts = [ "algorithm=", "verbose" ]
arg = read_options( "a:v", longopts, treat_options, 1, usage_string )

try :    
    parser = xml.sax.make_parser()
    if algorithm == "complex" :
        verbose( "Pass 1: Reading vocabulary from file... please wait" )
        input_file = open( arg[ 0 ] )
        parser.setContentHandler( GenericXMLHandler( treat_entity=build_vocab ))
        parser.parse( input_file )
        input_file.close()
    # Second pass
    sentence_counter = 0
    verbose( "Pass 2: Lowercasing the words in the XML file" )
    input_file = open( arg[ 0 ] )    
    if algorithm == "complex" :
        handler = GenericXMLHandler( treat_meta=treat_meta,
                                     treat_entity=treat_sentence_complex,
                                     gen_xml=True )
    elif algorithm == "simple" :    
        handler = GenericXMLHandler( treat_meta=treat_meta,
                                     treat_entity=treat_sentence_simple,
                                     gen_xml=True )
    parser.setContentHandler( handler )
    parser.parse( input_file )
    print handler.footer
    input_file.close() 
 
except IOError, err :  
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid XML file," +\
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-*.dtd)"

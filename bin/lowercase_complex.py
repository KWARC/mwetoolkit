#!/usr/bin/python
"""
   
"""

import sys
import xml.sax

import install
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from util import usage, read_options, treat_options_simplest

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s <corpus.xml>

    The <corpus.xml> file must be valid XML (mwttoolkit-corpus.dtd).
"""
vocab = {}

################################################################################
       
def build_vocab( sentence ) :
    """
        For each sentence in the corpus, add it to the vocabulary.
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """
    global vocab
    for w_i in range(len(sentence.word_list)) :
        key = sentence.word_list[ w_i ].surface        
        low_key = sentence.word_list[ w_i ].surface.lower()
        forms = vocab.get( low_key, {} )
        form_entry = forms.get( key, [ 0, 0 ] )
        # a form entry has two counters, one for the occurrences and one for
        # the number of times this occurred at the beginning of a sentence. 
        # Therefore, form_entry[0] >= form_entry[1]
        form_entry[ 0 ] = form_entry[ 0 ] + 1  
        # This form occurrs at the first position of the sentence. Count it
        if w_i == 0 :
            form_entry[ 1 ] = form_entry[ 1 ] + 1 
        forms[ key ] = form_entry
        vocab[ low_key ] = forms
    
################################################################################  

def get_case_class( token ) :
    """
        For a given token, assigns a class that can be:
        lowercase - All characters are lowercase
        UPPERCASE - All characters are uppercase
        Firstupper - All characters are lowercase except for the first
        MiXeD - This token contains mixed lowercase and uppercase characters
        ? - This token does not contain alphabetic characters
        
        >>> print get_case_class( "Abacus" )
        Firstupper
        >>> print get_case_class( "abacus" )
        lowercase
        >>> print get_case_class( "ABACUS" )
        ?
        >>> print get_case_class( "1234" )
        UPPERCASE    
        >>> print get_case_class( "A" )
        UPPERCASE
        >>> print get_case_class( "a" )
        lowercase
        >>> print get_case_class( "Ab" )
        Firstupper    
        >>> print get_case_class( "aB" )
        MiXeD    
        >>> print get_case_class( "AB" )
        UPPERCASE
        >>> print get_case_class( "A23" )
        UPPERCASE
        >>> print get_case_class( "23A" )
        UPPERCASE
        >>> print get_case_class( "a23" )
        lowercase
        >>> print get_case_class( "23a" )                                                
        lowercase
        >>> print get_case_class( "a23A" )
        MiXeD    
        >>> print get_case_class( "A23a" )    
        MiXeD    
    """
    token_list = list(token)
    case_class = "?"
    for letter_i in range(len(token_list)) :
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
    """
    # If a given forms occurrs 70% of the cases (for 2 forms) or more, it is 
    # considered preferred
    PRED_THRESHOLD = .9 - 0.1 * len(percents)
    max_like = (0, None)
    for form in percents.keys() :
        if percents[form] >= PRED_THRESHOLD and percents[form] > max_like[0]:
            max_like = (percents[ form ], form )
    return max_like[ 1 ] # No preferred form
    


################################################################################

def treat_sentence( sentence ) :
    """
        For each sentence in the corpus, lowercases its words based on the most
    frequent form in the vocabulary.
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """
    
    global vocab
    
    # When 80% or more of the Firstupper forms occur at sentence start, we 
    # lowercase it.
    START_THRESHOLD=0.8
        
    for w_i in range(len(sentence.word_list)) :
        w = sentence.word_list[ w_i ]
        case_class = get_case_class( w.surface )          
        # Does nothing if it's aready lowercase or if it's not alphabetic
        if case_class != "lowercase" and case_class != "?" :
            low_key = w.surface.lower()            
            token_stats = vocab[ low_key ]
            percents = get_percents( token_stats )
            pref_form = get_preferred_form( percents )
            if case_class == "UPPERCASE" :
                if pref_form :
                    w.surface = pref_form
                else :
                    pass # Sometimes the word is all uppercase, sometimes it is
                         # not... So let it be what it wants to be, nobody's 
                         # forcing it to change its case
            elif case_class == "Firstupper" :
                occurs = token_stats[ w.surface ]
                if w_i == 0 and \
                   float(occurs[ 1 ]) / float(occurs[ 0 ]) >= START_THRESHOLD :
                    w.surface = w.surface.lower()
                elif pref_form :
                    w.surface = pref_form
                else :
                    pass # Don't modify case, we cannot know whether it is a 
                         # proper noun, a sentence start, a title word, a spell 
                         # error, etc.                   
            else : # MiXeD
                if pref_form :
                    w.surface = pref_form
                else :
                    pass # The word contains majuscules, minuscules, and does 
                         # not have a preferred form. So, what do you expect me
                         # to do about it? Nothing, I just ignore it, it's a 
                         # freaky weird creature!                    
    print sentence.to_xml().encode( 'utf-8' )
    
################################################################################
# MAIN SCRIPT


arg = read_options( "", [], treat_options_simplest, 1, usage_string )

try :    
    print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    print "<!DOCTYPE corpus SYSTEM \"dtd/mwttoolkit-corpus.dtd\">"
    print "<corpus>"         
    
    input_file = open( arg[ 0 ] )    
    parser = xml.sax.make_parser()
    parser.setContentHandler( CorpusXMLHandler( build_vocab ) ) 
    parser.parse( input_file )
    # Second pass
    input_file = open( arg[ 0 ] )    
    parser.setContentHandler( CorpusXMLHandler( treat_sentence ) ) 
    parser.parse( input_file )

    input_file.close() 
    print "</corpus>"    
except IOError, err :  
    print err
    print "Error reading corpus file. Please verify __common.py configuration"        
    sys.exit( 2 )      
except Exception, err :
    print err
    print "You probably provided an invalid corpus file, please " + \
          "validate it against the DTD (mwttoolkit-corpus.dtd)"

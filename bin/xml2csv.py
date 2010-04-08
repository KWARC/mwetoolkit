#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
    This script converts a candidates file in XML (mwttoolkit-candidates.dtd) 
    into a corresponding representation in the file format 
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import getopt
import xml.sax
import re

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from util import usage, read_options, treat_options_simplest
from xmlhandler.classes.__common import SEPARATOR, WILDCARD, WORD_SEPARATOR
     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <candidates.xml> file must be valid XML (mwttoolkit-candidates.dtd). 
"""     
            
################################################################################     

def treat_meta( meta ) :
    """
    """
    string_cand = "id\tngram\tpos\t"
    for cs in meta.corpus_sizes :
        string_cand = string_cand + cs.name + "\t"  
    string_cand = string_cand.strip()        
        
    print string_cand.encode( 'utf-8' )       
       
################################################################################     
       
def treat_candidate( candidate ) :
    """
        For each `Candidate`, print the candidate ID, its POS pattern and the 
        list of occurrences one per line
        
        @param candidate The `Candidate` that is being read from the XML file.
    """
    string_cand = ""
    if candidate.id_number >= 0 :
        string_cand += str( candidate.id_number )
    string_cand = string_cand.strip() + "\t"    
    
    for w in candidate.base.word_list :
        if w.lemma != WILDCARD :            
            string_cand += w.lemma + " "
        else :
            string_cand += w.surface + " "
    string_cand = string_cand.strip() + "\t"
    
    for w in candidate.base.word_list :
        string_cand += w.pos + " "
    string_cand = string_cand.strip() + "\t"
    
    for freq in candidate.base.freqs :
        string_cand += str( freq.value ) + "\t"
    string_cand = string_cand.strip()
                 
    
    print string_cand.encode( 'utf-8' )

################################################################################     
# MAIN SCRIPT

arg = read_options( "", [], treat_options_simplest, 1, usage_string ) 

try :    
    relation_name = re.sub( "\.xml", "", arg[ 0 ] )
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    parser.setContentHandler( CandidatesXMLHandler( \
                              treat_candidate=treat_candidate, \
                              treat_meta=treat_meta ) ) 
    parser.parse( input_file )
    input_file.close() 
    
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(mwttoolkit-candidates.dtd)"

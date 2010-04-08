#!/usr/bin/python
"""
    This script simply gives some stats about a candidates file, such as number
    of candidates, etc. Output is written on stderr.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import getopt
import xml.sax

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from util import read_options, treat_options_simplest
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <candidates.xml> file must be valid XML (mwttoolkit-candidates.dtd). 
"""          
candidate_counter = 0
 
################################################################################     
       
def treat_candidate( candidate ) :
    """
        For each candidate and for each `CorpusSize` read from the `Meta` 
        header, generates four features that correspond to the Association
        Measures described above.
        
        @param candidate The `Candidate` that is being read from the XML file.    
    """
    global candidate_counter
    candidate_counter += 1

################################################################################     
# MAIN SCRIPT

arg = read_options( "", [], treat_options_simplest, 1, usage_string )

try :    
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    parser.setContentHandler(CandidatesXMLHandler( \
                             treat_candidate=treat_candidate)) 
    parser.parse( input_file )
    input_file.close() 
    print >> sys.stderr, str( candidate_counter ) + " candidates in " + arg[ 0 ]
    
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid corpus file, " + \
                         "please validate it against the DTD " + \
                         "(mwttoolkit-corpus.dtd)"

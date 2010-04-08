#!/usr/bin/python
"""
    This script performs the automatic annotation of a candidate list according
    to a reference list (also called Gold Standard). The reference list should 
    contain a manually verified list of attested Multiword Terms of the domain.
    The annotation defines a True Positive class for each candidate, which is
    True if the candidate occurs in the reference and False if the candidate is
    not in the reference (thus the candidate is probably a random word 
    combination and not a MWT).
    
    For more information, call the script with no parameter and read the
    usage instructions.    
"""

import sys
import getopt
import re
import xml.sax

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.patternsXMLHandler import PatternsXMLHandler
from xmlhandler.classes.tpclass import TPClass
from xmlhandler.classes.meta_tpclass import MetaTPClass
from util import usage, read_options, treat_options_simplest

################################################################################     
# GLOBALS   

usage_string = """Usage: 
    
python %(program)s -r <reference.xml> OPTIONS <ccandidates.xml>

-r <reference.xml> OR --reference <patterns.xml>
    The reference list or gold standard, valid XML (mwttoolkit-patterns.dtd).
            
OPTIONS may be:

-g OR --ignore-pos
     Ignores Part-Of-Speech when counting candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be counted 
     as the same entity. Default false.

    The <candidates.xml> file must be valid XML (mwttoolkit-candidates.dtd). The 
reference list or gold standard must be valid XML (mwttoolkit-patterns.dtd).
"""
gs = []
ignore_pos = False
gs_name = None

################################################################################     

def treat_meta( meta ) :
    """
        Adds new meta-TP class corresponding to the evaluation of the candidate
        list according to a reference gold standard. Automatic evaluation is
        2-class only, the class values are "True" and "False" for true and
        false positives.
        
        @param meta The `Meta` header that is being read from the XML file.       
    """
    global gs_name
    meta.add_meta_tpclass( MetaTPClass( gs_name, "{True,False}" ) )
    print meta.to_xml().encode( 'utf-8' )

################################################################################     
       
def treat_candidate( candidate ) :
    """
        For each candidate, verifies whether it is contained in the reference
        list (in which case it is a *True* positive) or else, it is not in the
        reference list (in which case it is a *False* positive, i.e. a random
        ngram that does not constitute a MWT).
        
        @param candidate The `Candidate` that is being read from the XML file.        
    """
    global gs, ignore_pos, gs_name
    true_positive = False
    for gold_entry in gs :
        if gold_entry.match( candidate.base ) :
            true_positive = True
            break # Stop at first positive match
    
    if true_positive :   
        candidate.add_tpclass( TPClass( gs_name, "True" ) )
    else :
        candidate.add_tpclass( TPClass( gs_name, "False" ) )               
    print candidate.to_xml().encode( 'utf-8' )
         
################################################################################     

def treat_reference( reference ) :
    """
        For each entry in the reference Gold Standard, store it in main memory
        in the `gs` global list. We hope that the GS is not too big. Future
        implementation should consider to use "shelve" for this.
        
        @param reference A `Pattern` contained in the reference Gold Standard.
    """
    global gs, ignore_pos
    if ignore_pos :
        reference.reset_pos()     # reference has type Pattern
    gs.append( reference )    

################################################################################     

def open_gs( gs_filename ) :
    """
        Reads the reference list from a file that is XML according to
        mwttoolkit-patterns.dtd. The Gold Standard (GS) reference is stored in
        the global variable gs.
        
        @param gs_filename The file name containing the Gold Standard reference
        in valid XML (mwttoolkit-patterns.dtd).
    """
    global gs
    try :      
        reference_file = open( gs_filename )
        parser = xml.sax.make_parser()
        parser.setContentHandler( PatternsXMLHandler( treat_reference ) )        
        parser.parse( reference_file )        
        reference_file.close()
    except IOError, err:
        print >> sys.stderr, err
        sys.exit( 2 ) 
    except Exception, err :
        print >> sys.stderr,  err
        print >> sys.stderr, "You probably provided an invalid reference " + \
                             "file, please validate it against the DTD " + \
                             "(mwttoolkit-patterns.dtd)"
        sys.exit( 2 )               

################################################################################     

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.
    """
    global gs, ignore_pos, gs_name
    for ( o, a ) in opts:
        if o in ("-r", "--reference"): 
            open_gs( a )     
            gs_name = re.sub( "\.xml", "", a ) 
        elif o in ("-g", "--ignore-pos"): 
            ignore_pos = True
       
    if not gs :
        print >> sys.stderr, "You MUST provide a non-empty reference list!"
        usage( usage_string )
        sys.exit( 2 )
        
    treat_options_simplest( opts, arg, n_arg, usage_string )    

################################################################################    
# MAIN SCRIPT

longopts = ["reference=", "ignore-pos" ]
arg = read_options( "r:g", longopts, treat_options, 1, usage_string )

try :         
    print """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE candidates SYSTEM "dtd/mwttoolkit-candidates.dtd">
<candidates>
""" 
    input_file = open( arg[ 0 ] )
    parser = xml.sax.make_parser()
    parser.setContentHandler(CandidatesXMLHandler(treat_meta, treat_candidate)) 
    parser.parse( input_file )
    input_file.close()     
    print "</candidates>"   
                  
except IOError, err :
    print >> sys.stderr, err
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid candidates file," + \
#                         " please validate it against the DTD " + \
#                         "(mwttoolkit-candidates.dtd)"

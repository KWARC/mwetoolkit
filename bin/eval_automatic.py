#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
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
    combination and not a MWT).
    
    For more information, call the script with no parameter and read the
    usage instructions.    
"""

import sys
import re
import xml.sax

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.dictXMLHandler import DictXMLHandler
from xmlhandler.classes.tpclass import TPClass
from xmlhandler.classes.meta_tpclass import MetaTPClass
from util import usage, read_options, treat_options_simplest, verbose

################################################################################     
# GLOBALS   

usage_string = """Usage: 
    
python %(program)s -r <reference.xml> OPTIONS <ccandidates.xml>

-r <reference.xml> OR --reference <patterns.xml>
    The reference list or gold standard, valid XML (dtd/mwetoolkit-patterns.dtd).
            
OPTIONS may be:

-c OR --case
    Make matching of a candidate against a dictionary entry case-sensitive
    (default is to ignore case in comparisons)

-v OR --verbose
    Print messages that explain what is happening.

-g OR --ignore-pos
     Ignores Part-Of-Speech when counting candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be counted 
     as the same entity. Default false.

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
    The reference list or gold standard must be valid XML
    (dtd/mwttoolkit-dict.dtd).
"""
gs = []
ignore_pos = False
gs_name = None
ignore_case = True
entity_counter = 0
tp_counter = 0
ref_counter = 0

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
        ngram that does not constitute a MWE).
        
        @param candidate The `Candidate` that is being read from the XML file.        
    """
    global gs, ignore_pos, gs_name, ignore_case, entity_counter, tp_counter
    if entity_counter % 100 == 0 :
        verbose( "Processing candidate number %(n)d" % { "n":entity_counter } )
    true_positive = False
    for gold_entry in gs :
        if gold_entry.match( candidate, ignore_case ) :
            true_positive = True
            break # Stop at first positive match
    
    if true_positive :   
        candidate.add_tpclass( TPClass( gs_name, "True" ) )
        tp_counter = tp_counter + 1
    else :
        candidate.add_tpclass( TPClass( gs_name, "False" ) )               
    print candidate.to_xml().encode( 'utf-8' )
    entity_counter += 1
         
################################################################################     

def treat_reference( reference ) :
    """
        For each entry in the reference Gold Standard, store it in main memory
        in the `gs` global list. We hope that the GS is not too big. Future
        implementation should consider to use "shelve" for this.
        
        @param reference A `Pattern` contained in the reference Gold Standard.
    """
    global gs, ignore_pos, ref_counter
    if ignore_pos :
        reference.reset_pos()     # reference has type Pattern
    gs.append( reference )
    ref_counter = ref_counter + 1

################################################################################     

def open_gs( gs_filename ) :
    """
        Reads the reference list from a file that is XML according to
        mwetoolkit-dict.dtd. The Gold Standard (GS) reference is stored in
        the global variable gs.
        
        @param gs_filename The file name containing the Gold Standard reference
        in valid XML (dtd/mwetoolkit-dict.dtd).
    """
    global gs
    try :      
        reference_file = open( gs_filename )
        parser = xml.sax.make_parser()
        parser.setContentHandler( DictXMLHandler( treat_reference ) )
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
    global gs, ignore_pos, gs_name, ignore_case
    for ( o, a ) in opts:
        if o in ("-r", "--reference"): 
            open_gs( a )     
            gs_name = re.sub( "\.xml", "", a ) 
        elif o in ("-g", "--ignore-pos"): 
            ignore_pos = True
        elif o in ("-c", "--case"):
            ignore_case = False

    if not gs :
        print >> sys.stderr, "You MUST provide a non-empty reference list!"
        usage( usage_string )
        sys.exit( 2 )
        
    treat_options_simplest( opts, arg, n_arg, usage_string )    

################################################################################    
# MAIN SCRIPT

longopts = ["reference=", "ignore-pos", "verbose", "case" ]
arg = read_options( "r:gvc", longopts, treat_options, 1, usage_string )

try :             
    input_file = open( arg[ 0 ] )
    parser = xml.sax.make_parser()
    handler = CandidatesXMLHandler( treat_meta=treat_meta,
                                    treat_candidate=treat_candidate,
                                    gen_xml="candidates")
    parser.setContentHandler(handler)
    parser.parse( input_file )
    input_file.close()     
    print handler.footer
    precision = float( tp_counter ) / float( entity_counter )
    recall = float( tp_counter ) / float( ref_counter )
    fmeas =  ( 2 * precision * recall) / ( precision + recall )
    verbose( "Nb. of true positives: %(tp)d" % {"tp" : tp_counter } )
    verbose( "Nb. of candidates: %(cand)d" % {"cand" : entity_counter } )
    verbose( "Nb. of references: %(refs)d" % {"refs" : ref_counter } )
    verbose( "Precision: %(p)f" % {"p" : precision } )
    verbose( "Recall: %(r)f" % {"r" : recall } )
    verbose( "F-measure: %(f)f" % {"f" : fmeas } )

                  
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-candidates.dtd)"

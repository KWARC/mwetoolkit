#!/usr/bin/python
"""
    This script sorts the candidate list according to the value of a feature (or
    the values of some features) that is/are called key feature(s). The key is
    used to sort the candidates in descending order (except if explicitely asked
    to sort in ascending order). Sorting is stable, i.e. if two candidates have 
    the same key feature values, their relative order will be preserved in the 
    output.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import getopt
import xml.sax
import os
import tempfile
import shelve
import bisect

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.util import read_options, treat_options_simplest, usage
from xmlhandler.classes.__common import TEMP_PREFIX, TEMP_FOLDER
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s [OPTIONS] -f <feat> <candidates.xml>

-f <feat> OR --feat <feat>    
    The name of the feature that will be used to sort the candidates. For 
    candidates whose sorting feature is not present, the script assumes the 
    default UNKNOWN_FEAT_VALUE, which is represented by a question mark "?".

OPTIONS may be:

-a OR --asc
    Sort in ascending order. By default, classification is descending.
-d OR --desc
    Sort in descending order. By default, classification is descending, so that
    this flag can also be ommitted.

    The <candidates.xml> file must be valid XML (mwttoolkit-candidates.dtd).    
"""          
feat_list = []
all_feats = []
feat_list_ok = False
temp_file = None
feat_to_order = []
ascending = False
 
################################################################################     
       
def treat_meta( meta ) :
    """
        Treats the meta information of the file. Besides of printing the meta
        header out, it also keeps track of all the meta-features. The list of
        `all_feats` will be used in order to verify that all key features have a
        valid meta-feature. This is important because we need to determine the
        correct type of the feature value, since it might influence sorting 
        order (e.g. integers 1 < 2 < 10 but strings "1" < "10" < "2")
        
        @param meta The `Meta` header that is being read from the XML file.         
    """
    global all_feats
    for meta_feat in meta.meta_feats :
        all_feats.append( meta_feat.name )
    print meta.to_xml().encode( 'utf-8' )
    
################################################################################         
    
def treat_candidate( candidate ) :
    """
        For each candidate, stores it in a temporary Database (so that it can be
        retrieved later) and also creates a tuple containing the sorting key
        feature values and the candidate ID. All the tuples are stored in a
        global list, that will be sorted once all candidates are read and stored
        into the temporary DB.
        
        @param candidate The `Candidate` that is being read from the XML file.
    """
    global feat_list, all_feats, feat_list_ok, feat_to_order
    # First, verifies if all the features defined as sorting keys are real 
    # features, by matching them against the meta-features of the header. This
    # is only performed once, before the first candidate is processed
    if not feat_list_ok :
        for feat_name in feat_list :
            if feat_name not in all_feats :
                print >> sys.stderr, "%(feat)s is not a valid feature" % \
                                     { "feat" : feat_name }
                print >> sys.stderr, "Please chose features from the list below"
                for feat in all_feats :
                    print >> sys.stderr, "* " + feat
                sys.exit( 2 )
        feat_list_ok = True
        
    # Store the whole candidate in a temporary database
    temp_file[ str( candidate.id_number ) ] = candidate
    # Create a tuple to be added to a list. The tuple contains the sorting key
    # values and...
    one_tuple = ()
    for feat_name in feat_list :
        one_tuple = one_tuple + ( candidate.get_feat_value( feat_name ), )
    # ... the candidate ID. The former are used to sort the candidates, the 
    # latter is used to retrieve a candidate from the temporary DB
    one_tuple = one_tuple + ( candidate.id_number, )
    feat_to_order.append( one_tuple )

################################################################################     

def sort_and_print() :
    """
        Sorts the tuple list `feat_to_order` and then retrieves the candidates
        from the temporary DB in order to print them out.
    """
    global feat_to_order, ascending, temp_file
    # Sorts the tuple list ignoring the last entry, i.e. the candidate ID
    # If I didn't ignore the last entry, algorithm wouldn't be stable
    # If the user didn't ask "-a" explicitely, sorting is reversed (descending)
    feat_to_order.sort( key=lambda x: x[ 0:len(x)-1 ], reverse=(not ascending) )    
    # Now print sorted candidates. A candidate is retrieved from temp DB through
    # its ID
    for feat_entry in feat_to_order :
        candidate = temp_file[ str( feat_entry[ len( feat_entry ) - 1 ] ) ]
        print candidate.to_xml().encode( 'utf-8' )

################################################################################     

def treat_feat_list( feat_string ) :
    """
        Parses the option of the "-f" option. This option is of the form 
        "<feat1>:<feat2>:<feat3>" and so on, i.e. feature names separated by
        colons.
        
        @param argument String argument of the -f option, has the form 
        "<feat1>:<feat2>:<feat3>"
        
        @return A list of strings containing the (unverified) key feature names.
    """
    return feat_string.split( ":" )

################################################################################     

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global feat_list, ascending
    a_or_d = []
    for ( o, a ) in opts:
        if o in ("-f", "--feat"): 
            feat_list = treat_feat_list( a )
        elif o in ("-a", "--asc") :        
            ascending = True      
            a_or_d.append( "a" )
        elif o in ("-d", "--desc") :
            ascending = False   
            a_or_d.append( "d" )         
            
    if len( a_or_d ) > 1 :
        print >> sys.stderr, "WARNING: you must provide only one option, -a" + \
                             " OR -d. Only the last one will be considered."            
    if not feat_list :
        print >> sys.stderr, "You MUST provide at least one sorting key with -f"
        usage( usage_string )
        sys.exit( 2 )
                            
    treat_options_simplest( opts, arg, n_arg, usage_string )


################################################################################     
# MAIN SCRIPT

longopts = [ "feat=", "asc", "desc" ]
arg = read_options( "f:ad", longopts, treat_options, 1, usage_string )

try :    
    try :    
        temp_fh = tempfile.NamedTemporaryFile( prefix=TEMP_PREFIX, 
                                               dir=TEMP_FOLDER )
        temp_name = temp_fh.name
        temp_fh.close()
        temp_file = shelve.open( temp_name, 'n' )
    except IOError, err :
        print >> sys.stderr, err
        print >> sys.stderr, "Error opening temporary file."
        print >> sys.stderr, "Please verify __common.py configuration"
        sys.exit( 2 )

    print """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE candidates SYSTEM "mwttoolkit-candidates.dtd">
<candidates>
"""   
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    parser.setContentHandler(CandidatesXMLHandler( \
                             treat_candidate=treat_candidate,
                             treat_meta=treat_meta)) 
    parser.parse( input_file )
    input_file.close()     
    sort_and_print()
    print "</candidates>"          
    
    try :
        temp_file.close()
        os.remove( temp_name )
    except IOError, err :
        print >> sys.stderr, err
        print >> sys.stderr, "Error closing temporary file. " + \
              "Please verify __common.py configuration"        
        sys.exit( 2 )
        
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(mwttoolkit-candidates.dtd)"

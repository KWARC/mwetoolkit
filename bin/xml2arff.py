#!/usr/bin/python
"""
    This script converts a candidates file in XML (mwttoolkit-candidates.dtd) 
    into a corresponding representation in the arff file format, used by the
    WEKA machine learning toolkit. Only features and TP classes are considered,
    information about the candidate's ngrams or occurrences are ignored. Please
    notice that if you don't have a feature that uniquely identifies your 
    candidate, you will not be able to trace back the classifier results to the
    original candidates.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import getopt
import xml.sax
import re

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.util import usage, read_options, treat_options_simplest
     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <candidates.xml> file must be valid XML (mwttoolkit-candidates.dtd). 
"""     
all_feats = []         
     
################################################################################     
       
def treat_meta( meta ) : 
    """
        When the `Meta` header is read, this function generates a corresponding
        header for the arff file. The header includes the name of the relation
        and a description of the attributes. This description is based on the
        `MetaFeat' and `MetaTPClass` entries of the header. If you provided
        invalid types for the features or the TP classes, the generated arff
        file will not be recognised by WEKA. If necessary, correct it manually.
        
        @param meta The `Meta` header that is being read from the XML file.
    """
    global all_feats, relation_name
    print "% Automatically generated by xml2arff"
    print "@relation %(name)s" % { "name" : relation_name }
    for meta_feat in meta.meta_feats :
        print "@attribute %(name)s %(type)s" % \
            { "name" : meta_feat.name, "type" : meta_feat.value }
        # features that will be considered in each candidate
        all_feats.append( meta_feat.name ) 
    for meta_tpclass in meta.meta_tpclasses :
        print "@attribute %(name)s %(type)s" % \
            { "name" : meta_tpclass.name, "type" : meta_tpclass.value }        
    print "@data"
       
################################################################################     
       
def treat_candidate( candidate ) :
    """
        For each `Candidate`, print a comma-separated line with its feature 
        values as described by the meta-features in the header. If a feature has
        no meta-feature header, it will be ignored. If a feature has an 
        associated meta-feature header but no feature value, it will be
        considered as a missing value "?" in the arff file. The True Positive
        classes are also considered as features in this context and are printed
        after the standard features of the candidate.
        
        @param candidate The `Candidate` that is being read from the XML file.
    """
    global all_feats
    line = ""
    for feat_name in all_feats :
        line = line + str( candidate.get_feat_value( feat_name ) ) + ","
    for tpclass in candidate.tpclasses :
        line = line + tpclass.value + ","        
    if isinstance( line, unicode ) :
        line = line.encode( 'utf-8' );
    print line[ 0:len(line)-1 ]

################################################################################     
# MAIN SCRIPT

arg = read_options( "", [], treat_options_simplest, 1, usage_string ) 

try :    
    relation_name = re.sub( "\.xml", "", arg[ 0 ] )
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    parser.setContentHandler(CandidatesXMLHandler( treat_meta, treat_candidate)) 
    parser.parse( input_file )
    input_file.close() 
    
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(mwttoolkit-candidates.dtd)"

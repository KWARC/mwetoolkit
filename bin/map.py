#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010 Carlos Ramisch
# 
# map.py is part of mwetoolkit
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
    TODO: Insert a description of your module here.
"""

import sys
import pdb
import xml.sax

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from util import read_options, treat_options_simplest, usage
from xmlhandler.classes.__common import UNKNOWN_FEAT_VALUE

################################################################################
# GLOBALS

usage_string = """Usage:

python %(program)s [OPTIONS] -f <feats> <candidates.xml>

-f <feats> OR --feat <feats>
    The name of the features that will be used to calculate Mean Average
    Precision. Each feature name correspond to a numeric feature described in
    the meta header of the file. Feature names should be separated by colon ":"
    The script ignores candidates whose feature is not present

OPTIONS may be:

-a OR --asc
    Sort in ascending order. By default, classification is descending.

-d OR --desc
    Sort in descending order. By default, classification is descending, so that
    this flag can also be ommitted.

-v OR --verbose
    Print messages that explain what is happening.

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
    Additionally, each candidate must contain at least one boolean tpclass using
    default "True" and "False" annotation.
"""
feat_list = []
all_feats = []
feat_list_ok = False
feat_to_order = {}
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
    global all_feats, usage_string, feat_to_order
    for meta_feat in meta.meta_feats :
        if meta_feat.value == "integer" or meta_feat.value == "real" :
            all_feats.append( meta_feat.name )
    tp_classes_ok = False
    for meta_tp in meta.meta_tpclasses :
        if meta_tp.value == "{True,False}" :
            tp_classes_ok = True
            feat_to_order[ meta_tp.name ] = {}
            for feat_name in all_feats :
                feat_to_order[ meta_tp.name ][ feat_name ] = []
    if not tp_classes_ok :
        print >> sys.stderr,"ERROR: You must define a boolean TP class"
        print >> sys.stderr, usage_string
        sys.exit( -1 )
        
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
                print >> sys.stderr, "ERROR: %(feat)s is not a valid feature" %\
                                     { "feat" : feat_name }
                print >> sys.stderr, "Please chose features from the list below"
                for feat in all_feats :
                    print >> sys.stderr, "* " + feat
                sys.exit( -1 )                
        feat_list_ok = True

    for tp_class in candidate.tpclasses :
        for feat_name in feat_list :
            feat_value = candidate.get_feat_value( feat_name )
            tp_value = candidate.get_tpclass_value( tp_class.name )
            if feat_value != UNKNOWN_FEAT_VALUE and \
               tp_value != UNKNOWN_FEAT_VALUE :
                tuple = ( float( feat_value ), tp_value == "True" )
                feat_to_order[ tp_class.name ][ feat_name ].append( tuple )
    
################################################################################

def calculate_map( values ):
    """
    """
    tp_counter = 0.0
    cumul_precision = 0.0
    for ( index, ( value, tpclass ) ) in enumerate( values ) :
        if tpclass :
            tp_counter += 1.0
            # rank = index+1, index = 0..n, rank = 1..n+1
            precision = 100.0 * (tp_counter / (index + 1))
            cumul_precision += precision            
    map = cumul_precision / tp_counter
    
    tp_counter = 0.0
    cumul_squared_error = 0.0
    for ( index, ( value, tpclass ) ) in enumerate( values ) :
        if tpclass :
            tp_counter += 1.0            
            # rank = index+1, index = 0..n, rank = 1..n+1
            precision = 100.0 * (tp_counter / (index + 1))
            cumul_squared_error += ( precision - map ) * ( precision - map )
    variance = cumul_squared_error / ( tp_counter - 1 )

    return map, variance, tp_counter

################################################################################

def print_stats() :
    """
        Sorts the tuple list `feat_to_order` and then retrieves the candidates
        from the temporary DB in order to print them out.
    """
    global feat_to_order, ascending

    #feat_to_order.sort( key=lambda x: x[ 0:len(x)-1 ], reverse=(not ascending) )
    # Now print sorted candidates. A candidate is retrieved from temp DB through
    # its ID
    for tpclass in feat_to_order.keys() :
        print "----------------------------------------------------------------"
        print "Statistics for %(tp)s:" % { "tp" : tpclass }
        print "----------------------------------------------------------------"
        for feat_name in feat_to_order[ tpclass ].keys() :
            feat_values = feat_to_order[ tpclass ][ feat_name ]
            feat_values.sort( key=lambda x: x[ 0 ], reverse=(not ascending) )
            ( map, variance, tps ) = calculate_map( feat_values )
            print "Feature: %(m)s" % { "m" : feat_name }
            print "MAP      : %(m).4f" % { "m": map }
            print "# of TPs : %(m).0f" % { "m": tps }
            print "Variance : %(m).4f" % { "m": variance }
            print ""

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
        print >> sys.stderr, "WARNING: you should provide only one option, " + \
                             "-a OR -d. Only the last one will be considered."
    if not feat_list :
        print >> sys.stderr, "You MUST provide at least one feature with -f"
        usage( usage_string )
        sys.exit( 2 )

    treat_options_simplest( opts, arg, n_arg, usage_string )


################################################################################
# MAIN SCRIPT

longopts = [ "feat=", "asc", "desc", "verbose" ]
arg = read_options( "f:adv", longopts, treat_options, 1, usage_string )

try :
    input_file = open( arg[ 0 ] )
    parser = xml.sax.make_parser()
    handler = CandidatesXMLHandler( treat_candidate=treat_candidate,
                                    treat_meta=treat_meta,
                                    gen_xml=False )
    parser.setContentHandler( handler )
    parser.parse( input_file )
    input_file.close()
    print_stats()    

except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-candidates.dtd)"

################################################################################
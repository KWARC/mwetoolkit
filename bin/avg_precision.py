#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
# 
# avg_precision.py is part of mwetoolkit
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
    Calculates Mean Average Precision (MAP) for a list of candidates containing
    numerical features. MAP is the average of precisions taken at each recall
    point (i.e. each TP) in a rank of candidates. Please see the implementation
    below for more details. This script is strongly inspired from Stefan Evert's
    script, released for the MWE 2008 shared task. You might find useful to 
    consult his publications to find a more detailed explanation on what MAP
    measures.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import read_options, treat_options_simplest, warn, verbose, error
from libs.base.__common import UNKNOWN_FEAT_VALUE
from libs import filetype


################################################################################
# GLOBALS

usage_string = """Usage:

python {program} [OPTIONS] -f <feats> <candidates>

-f <feats> OR --feat <feats>
    The name of the features that will be used to calculate Mean Average
    Precision. Each feature name correspond to a numeric feature described in
    the meta header of the file. Feature names should be separated by colon ":"
    The script ignores candidates whose feature is not present

The <candidates> input file must be in one of the filetype
formats accepted by the `--from` switch.
Additionally, each candidate must contain at least one boolean
tpclass using default "True" and "False" annotation.


OPTIONS may be:

--from <input-filetype-ext>
    Force reading from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[candidates]}

-a OR --asc
    Sort in ascending order. By default, classification is descending.

-d OR --desc
    Sort in descending order. By default, classification is descending, so that
    this flag can also be ommitted.
    
-p OR --precs
    Print the precisions at each recall level, for each feature. This is useful
    to generate precision/recall curves. Default false.

{common_options}
"""
feat_list = []
all_feats = []
feat_list_ok = False
feat_to_order = {}
ascending = False
print_precs = False
input_filetype_ext = None


################################################################################

class StatsCollectorHandler(filetype.InputHandler):
    def handle_meta(self, meta, info={}) :
        """Treats the meta information of the file. Besides of printing the meta
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
            error("You must define a boolean TP class")


    def handle_candidate(self, candidate, info={}) :
        """For each candidate, stores it in a temporary Database (so that it can be
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
                    error("%(feat)s is not a valid feature\n" + \
                          "Please chose features from the list below\n" + \
                          "%(list)s" % {"feat": feat_name,
                                        "list": "\n".join(
                                            map(lambda x: "* " + x, all_feats))})
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
        Calculates Mean Average Precision for a list of feature values. We 
        suppose that the input list is already sorted.
        
        @param values A list containing tuples in the form (value,TPclass), 
        where value is a float number corresponding to a feature value and
        TPclass is a boolean indicating whether the candidate is a TP. The list
        must be sorted in ascending or descending order.
        
        @return A tuple containing 0) Mean Average Precision, 1) Variance, 2)
        Total number of TPs in the list and 3) a list with all the precisions at
        each TP.
    """
    tp_counter = 0.0
    cumul_precision = 0.0
    precs = []
    for ( index, ( value, tpclass ) ) in enumerate( values ) :
        if tpclass :
            tp_counter += 1.0
            # rank = index+1, index = 0..n, rank = 1..n+1
            precision = 100.0 * (tp_counter / (index + 1))
            #verbose "Precision at %(c)d : %(p)f" % { "c" : tpcounter, 
            #                                         "p" : precision }
            precs.append( precision )
            cumul_precision += precision
    if tp_counter != 0.0 :
        mapr = cumul_precision / tp_counter
    else :
        mapr = 0.0
    
    tp_counter = 0.0
    cumul_squared_error = 0.0
    for ( index, ( value, tpclass ) ) in enumerate( values ) :
        if tpclass :
            tp_counter += 1.0            
            # rank = index+1, index = 0..n, rank = 1..n+1
            precision = 100.0 * (tp_counter / (index + 1))
            cumul_squared_error += ( precision - mapr ) * ( precision - mapr )
    if tp_counter > 1.0 :
        variance = cumul_squared_error / ( tp_counter - 1.0 )
    else :
        variance = 0.0

    return mapr, variance, tp_counter, precs

################################################################################

def print_stats() :
    """
        Sorts the tuple list `feat_to_order` and then retrieves the candidates
        from the temporary DB in order to print them out.
    """
    global feat_to_order
    global ascending
    global feat_list
    global print_precs
    #feat_to_order.sort( key=lambda x: x[ 0:len(x)-1 ], reverse=(not ascending))
    # Now print sorted candidates. A candidate is retrieved from temp DB through
    # its ID
    for tpclass in feat_to_order.keys() :
        precisions = []
        print("----------------------------------------------------------------")
        print("Statistics for %(tp)s:" % { "tp" : tpclass })
        print("----------------------------------------------------------------")
        for feat_name in feat_list :
            feat_values = feat_to_order[ tpclass ][ feat_name ]
            feat_values.sort( key=lambda x: x[ 0 ], reverse=(not ascending))
            ( mapr, variance, tps, precs ) = calculate_map(feat_values)
            print("Feature: %(m)s" % { "m" : feat_name })
            print("MAP      : %(m).4f" % { "m": mapr })
            print("# of TPs : %(m).0f" % { "m": tps })
            print("Variance : %(m).4f" % { "m": variance })
            print()
            precisions.append( precs )
        if print_precs :
            for line in zip( *precisions ) :
                print("\t".join( map( str, line ) ))

################################################################################

def treat_feat_list( feat_string ) :
    """
        Parses the option of the "-f" option. This option is of the form
        "<feat1>:<feat2>:<feat3>" and so on, i.e. feature names separated by
        colons.

        @param feat_string String argument of the -f option, has the form
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
    global feat_list
    global ascending
    global print_precs
    
    treat_options_simplest( opts, arg, n_arg, usage_string )    
    
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
        elif o in ("-p", "--precs") :
            print_precs = True
        elif o == "--from":
            input_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)

    if len( a_or_d ) > 1 :
        warn("you should provide only one option, -a OR -d. Only the last one"+\
             " will be considered.")
    if not feat_list :
        error("You MUST provide at least one feature with -f")

################################################################################
# MAIN SCRIPT

longopts = [ "from=", "feat=", "asc", "desc", "precs" ]
args = read_options( "f:adp", longopts, treat_options, 1, usage_string )
filetype.parse(args, StatsCollectorHandler(), input_filetype_ext)
print_stats()    

#!/usr/bin/python
# -*- coding:UTF-8 -*-

# ###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# sort.py is part of mwetoolkit
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
    This script sorts the candidate list according to the value of a feature (or
    the values of some features) that is/are called key feature(s). The key is
    used to sort the candidates in descending order (except if explicitely asked
    to sort in ascending order). Sorting is stable, i.e. if two candidates have 
    the same key feature values, their relative order will be preserved in the 
    output.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import tempfile
import shelve

from libs.util import read_options, treat_options_simplest, \
    error, warn
from libs.base.__common import TEMP_PREFIX, TEMP_FOLDER
from libs import filetype


################################################################################     
# GLOBALS     

usage_string = """Usage: 
    
python {program} [OPTIONS] -f <feat> <candidates>

-f <feat> OR --feat <feat>    
    The name of the feature that will be used to sort the candidates. For 
    candidates whose sorting feature is not present, the script assumes the 
    default UNKNOWN_FEAT_VALUE, which is represented by a question mark "?".

The <candidates> input file must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

-a OR --asc
    Sort in ascending order. By default, classification is descending.

-d OR --desc
    Sort in descending order (default).

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[candidates]}

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, keeps input in original format):
    {descriptions.output[candidates]}

{common_options}
"""
feat_list = []
all_feats = []
feat_list_ok = False
temp_file = None
feat_to_order = []
ascending = False

input_filetype_ext = None
output_filetype_ext = None


################################################################################     

class SorterHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)

    def handle_meta(self, meta, info={}):
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
        for meta_feat in meta.meta_feats:
            all_feats.append(meta_feat.name)
        self.chain.handle_meta(meta, info)


    def handle_candidate(self, candidate, info={}):
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
        if not feat_list_ok:
            for feat_name in feat_list:
                if feat_name not in all_feats:
                    error("{feat} is not a valid feature\n" \
                            "Please chose features from the list below:\n" \
                            "{list}".format(feat=feat_name, list="\n".join(
                                    "* " + feat for feat in all_feats)))
            feat_list_ok = True

        # Store the whole candidate in a temporary database
        temp_file[str(candidate.id_number)] = candidate
        # Create a tuple to be added to a list. The tuple contains the sorting key
        # values and...
        one_tuple = ()
        for feat_name in feat_list:
            one_tuple = one_tuple + ( candidate.get_feat_value(feat_name), )
        # ... the candidate ID. The former are used to sort the candidates, the 
        # latter is used to retrieve a candidate from the temporary DB
        one_tuple = one_tuple + ( candidate.id_number, )
        feat_to_order.append(one_tuple)


    def after_file(self, fileobj, info={}):
        """
            Sorts the tuple list `feat_to_order` and then retrieves the candidates
            from the temporary DB in order to print them out.
        """
        global feat_to_order, ascending, temp_file
        # Sorts the tuple list ignoring the last entry, i.e. the candidate ID
        # If I didn't ignore the last entry, algorithm wouldn't be stable
        # If the user didn't ask "-a" explicitely, sorting is reversed (descending)
        feat_to_order.sort(key=lambda x: x[0:len(x) - 1], reverse=(not ascending))
        # Now print sorted candidates. A candidate is retrieved from temp DB through
        # its ID
        for feat_entry in feat_to_order:
            candidate = temp_file[unicode(feat_entry[len(feat_entry) - 1])]
            self.chain.handle_candidate(candidate)
        self.chain.after_file(fileobj, info)


################################################################################

def treat_feat_list(feat_string):
    """
        Parses the option of the "-f" option. This option is of the form 
        "<feat1>:<feat2>:<feat3>" and so on, i.e. feature names separated by
        colons.
        
        @param feat_string String argument of the -f option, has the form
        "<feat1>:<feat2>:<feat3>"
        
        @return A list of strings containing the (unverified) key feature names.
    """
    return feat_string.split(":")


################################################################################

def treat_options(opts, arg, n_arg, usage_string):
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global feat_list
    global ascending
    global input_filetype_ext
    global output_filetype_ext

    treat_options_simplest(opts, arg, n_arg, usage_string)

    a_or_d = []
    for ( o, a ) in opts:
        if o in ("-f", "--feat"):
            feat_list = treat_feat_list(a)
        elif o in ("-a", "--asc"):
            ascending = True
            a_or_d.append("a")
        elif o in ("-d", "--desc"):
            ascending = False
            a_or_d.append("d")
        elif o == "--from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        else:
            raise Exception("Bad arg")

    if len(a_or_d) > 1:
        warn("you must provide only one option, -a OR -d. Only the last one" + \
             " will be considered.")
    if not feat_list:
        error("You MUST provide at least one sorting key with -f")



################################################################################     
# MAIN SCRIPT

longopts = ["from=", "to=", "feat=", "asc", "desc"]
args = read_options("f:ad", longopts, treat_options, -1, usage_string)

try:
    temp_fh = tempfile.NamedTemporaryFile(prefix=TEMP_PREFIX,
                                          dir=TEMP_FOLDER, delete=True)
    temp_name = temp_fh.name
    temp_fh.close()
    temp_file = shelve.open(temp_name, 'n')
except IOError as err:
    error("Error opening temporary file.\n" + \
          "Please verify __common.py configuration")

filetype.parse(args, SorterHandler(), input_filetype_ext)

try:
    temp_file.close()
except IOError as err:
    error("Error closing temporary file.\n" + \
          "Please verify __common.py configuration")

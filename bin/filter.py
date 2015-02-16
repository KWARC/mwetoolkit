#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# filter.py is part of mwetoolkit
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
    This script filters the candidate list based:

        1) On the number of occurrences of the candidate. The threshold might
        be defined individually for each corpus. Candidates occurring less than
        the threshold are filtered out.

        2) On whether they match one of a set of patterns. The patterns are
        in the same format as used by candidates.py, except that they are
        'anchored' by default (i.e., they must match the whole n-gram, not just
        part of it).
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import read_options, treat_options_simplest, verbose, error, warn
from libs import filetype

     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python {program} [OPTIONS] <input-file>

The <input-file> must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[ALL]}

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, keeps input in original format):
    {descriptions.output[ALL]}

-p <patterns.xml> OR --patterns <patterns.xml>
    The patterns to keep in the file, valid XML (mwetoolkit-dict.dtd)
    Note that unlike candidates.py, this scripts treats patterns as 'anchored',
    i.e., they must match the whole ngram, not just a part of it.

-t <source>:<value> OR --threshold <source>:<value>    
    Defines a frequency threshold below which the candidates are filtered out.
    This means that if a certain candidates appears less than <value> times in a
    corpus named <source>, these candidate be removed from the output. Only 
    candidates occurring <value> times or more in the <source> corpus are 
    considered. Please remark that the <source> name must be provided exactly as
    it appears in the candidate list. If no <source> is given, all the corpora
    will be considered with the same threshold value (this might not be a good 
    idea when corpora sizes differ significantly). The <value> argument must be
    a non-negative integer, but setting <value> to 0 is the same as not 
    filtering the candidates at all.

-e <name>:<value> OR --equals <name>:<value>
    Defines an equality filter on the value of a feature. Only the candidates
    where the feature <name> is equal to <value> will be kept in the list.

-r OR --reverse
    Reverses the filtering mechanism, in order to print out only those 
    candidates that do NOT obey the criteria.
    
-a OR --maxlength
-i OR --minlength
    Defines the maximum/minimum number of tokens for a given element to be kept.
    Can be useful, for instance, to remove too long and/or short sentences from
    a given corpus, or candidates from a list. Both options can be defined at 
    the same time, but the maximum cannot be inferior to the minimum, e.g. 
    -a 10 -i 11 will return an empty list.    

--min-mweoccurs <n>
--max-mweoccurs <n>
    Defines the minimum/maximum number of MWE occurrences for a sentence
    in a corpus.  Note that other types of entity do not have MWE occurrences,
    so this flag will be ignored if applied on anything other than a corpus.

{common_options}
"""
reverse = False
thresh_source = None
thresh_value = 0
equals_name = None
equals_value = None
patterns = []
minlength = 0
maxlength = float("inf")
min_mweoccurs = 0
max_mweoccurs = float("inf")

input_filetype_ext = None
output_filetype_ext = None


################################################################################

class FilterHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)


    def _fallback_entity(self, entity, info={}) :
        """For each candidate, verifies whether its number of occurrences in a 
        given source corpus is superior or equal to the threshold. If no source
        corpus was provided (thresh_source is None), then all the corpora will
        be considered when verifying the threshold constraint. A candidate is
        printed to stdout only if it occurrs thres_value times or more in the
        corpus names thresh_source.
        
        @param entity: The `Ngram` that is being read from the XML file.
        """
        global thresh_source
        global thresh_value
        global equals_name
        global equals_value
        global reverse
        global patterns
        global maxlength
        global minlength

        print_it = True
        ngram_to_print = entity

        # Threshold test
        if entity.freqs :
            for freq in entity.freqs :
                if thresh_source :
                    if ( thresh_source == freq.name or
                         thresh_source == freq.name + ".xml" ) and \
                         freq.value < thresh_value :
                        print_it = False
                else :
                    if freq.value < thresh_value :
                        print_it = False

        # Equality test
        if print_it and equals_name :
            print_it = False
            for feat in entity.features :
                if feat.name == equals_name and feat.value == equals_value :
                    print_it = True


        # NOTE: Different patterns may match the same ngram, with different
        # results, when the 'ignore' pattern attribute is involved. Currently,
        # we are only printing the first such match.
        if print_it and patterns :
            print_it = False
            words = entity
            for pattern in patterns :
                for (match_ngram, wordnums) in pattern.matches(words,
                        anchored_begin=True, anchored_end=True):
                    print_it = True
                    ngram_to_print = match_ngram
                    break
                if print_it :
                    break

        # Filter out too long or too short elements
        lenentity = len(entity)
        if lenentity < minlength or lenentity > maxlength :
            print_it = False
            verbose("Filtered out: %d tokens" % lenentity)

        # Filter out sentences with too few/too many MWE candidates
        if info["kind"] == "sentence":
            n = len(entity.mweoccurs)
            if not (min_mweoccurs <= n <= max_mweoccurs):
                print_it = False

        if reverse :
            print_it = not print_it

        if print_it :   
            self.chain.handle(ngram_to_print, info)


################################################################################

def interpret_threshold( a ) :
    """
        Interprets the argument of the -t option, that describes a threshold 
        value given a certain source corpus name, in the form <source>:<value>.
        The first part, <source>:, might be ommited, in which case the threshold
        will be applied for all corpora in which the candidate was counted.
        
        @param a The string argument of the -t option
        
        @return a tuple containing (source, value) - where source can be None if
        undefined - that corresponds to the argument. If the provided argument
        is not valid (not a valid pair <source>:<value>), this function returns
        None. No verification is made in order to assure whether <source> is a 
        valid corpus name: this should be done by the user.
    """
    argument_parts = a.split( ":" )
    try :
        if len(argument_parts) == 1 :
            return ( None, int( argument_parts[0] ) )
        elif len(argument_parts) == 2 :
            return ( argument_parts[ 0 ], int( argument_parts[ 1 ] ) )
        else :
            return None
    except TypeError :
        return None        
    except ValueError : # No integer provided in second part
        return None

################################################################################

def interpret_equals( a ) :
    """
        Interprets the argument of the -e option, that describes an equality
        filter.
        
        @param a The string argument of the -e option
        
        @return A pair of strings with the name and the value of the filtering
        criterium. None if the argument is invalid.
    """
    argument_parts = a.split( ":" )
    if len(argument_parts) == 2 :
        return ( argument_parts[ 0 ], argument_parts[ 1 ] )
    else :
        return None

################################################################################

def interpret_length( l, maxormin ):
    """
    Transform argument given to -a or -i options into integer + error checks.

    @param l: A string passed as argument to -i or -a
    @param maxormin: A string indicating whether this is "maximum" or "minimum"
    @return: An integer corresponding to l
    """
    try :
        result = int( l )
        if result < 0:
            raise ValueError
        verbose( "%s length: %d" % (maxormin, result) )
        return result
    except ValueError:
        error("Argument of must be non-negative integer, got " + repr(l))

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global thresh_source
    global thresh_value
    global equals_name
    global equals_value
    global reverse
    global minlength
    global maxlength
    global min_mweoccurs
    global max_mweoccurs
    
    treat_options_simplest( opts, arg, n_arg, usage_string )    
    
    for ( o, a ) in opts:
        if o in ( "-t", "--threshold" ) : 
            threshold = interpret_threshold( a )
            if threshold :
                (thresh_source, thresh_value) = threshold
            else :
                error( "The format of the -t argument must be <source>:"
                       "<value>\n<source> must be a valid corpus name and "
                       "<value> must be a non-negative integer")
        elif o in ( "-e", "--equals" ) :
            equals = interpret_equals( a )
            if equals :
                ( equals_name, equals_value ) = equals
            else :
                error( "The format of the -e argument must be <name>:"
                       "<value>\n<name> must be a valid feat name and "
                       "<value> must be a non-empty string")

        elif o in ("-p", "--patterns") :
            verbose( "Reading patterns file" )
            global patterns
            patterns = filetype.parse_entities([a])
        elif o in ("-r", "--reverse") :
            reverse = True
            verbose("Option REVERSE active")

        elif o in ("-i", "--minlength") :
            minlength = interpret_length( a, "minimum" )
        elif o in ("-a", "--maxlength") :
            maxlength = interpret_length( a, "maximum" )
        elif o == "--min-mweoccurs":
            min_mweoccurs = interpret_length(a, "minimum")
        elif o == "--max-mweoccurs":
            max_mweoccurs = interpret_length(a, "maximum")
        elif o == "--from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)

    if minlength > maxlength:
        warn("minlength should be <= maxlength")
    if min_mweoccurs > max_mweoccurs:
        warn("min-mweoccurs should be <= max-mweoccurs")
            

################################################################################
# MAIN SCRIPT

longopts = [ "threshold=", "equals=", "patterns=", "reverse", "maxlength=",
             "minlength=", "min-mweoccurs=", "max-mweoccurs=", "from=", "to=" ]
args = read_options( "t:e:p:ra:i:", longopts, treat_options, -1, usage_string )
filetype.parse(args, FilterHandler(), input_filetype_ext)

#!/usr/bin/python
# -*- coding:UTF-8 -*-

# ###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# util.py is part of mwetoolkit
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
    Set of utility functions that are common to several scripts.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import getopt
import sys
import traceback
import xml.sax

################################################################################

verbose_on = False
debug_mode = False

common_options_usage_string = """\
-v OR --verbose
    Print messages that explain what is happening.

-D or --debug
    Print debug information when an error occurs.
    
-h or --help
    Print usage information about parameters and options"""



################################################################################

def set_verbose(value):
    """
        Sets whether to show verbose messages.
    """
    global verbose_on
    verbose_on = value


################################################################################

def verbose(message):
    """
        Prints a message if in verbose mode.
    """
    global verbose_on
    if verbose_on:
        print(message, file=sys.stderr)


################################################################################

def set_debug_mode(value):
    """
        Sets whether to dump a stack trace when an unhandled exception occurs.
    """
    global debug_mode
    debug_mode = value
    if debug_mode:
        print("Debug mode on", file=sys.stderr)


################################################################################

def usage(usage_string):
    """
        Print detailed instructions about the use of this program. Each script
        that uses this function should provide a variable containing the
        usage string.
    """
    usage_string = usage_string % {
        "program": sys.argv[0],
        "common_options": common_options_usage_string
    }
    usage_string = usage_string.format(program=sys.argv[0],
            common_options=common_options_usage_string,
            descriptions=FiletypeDescriptions())
    print(usage_string, end='', file=sys.stderr)


class FiletypeDescriptions(object):
    @property
    def input(self):
        from . import filetype
        return self._descriptions(filetype.INPUT_INFOS)

    @property
    def output(self):
        from . import filetype
        return self._descriptions(filetype.OUTPUT_INFOS)

    def _descriptions(self, category2ftis):
        return {category: "\n    ".join("* \"{}\": {}".format(
            fti.filetype_ext, fti.description) for fti in ftis)
                for (category, ftis) in category2ftis.iteritems()}


################################################################################

def treat_options_simplest(opts, arg, n_arg, usage_string):
    """
        Verifies that the number of arguments given to the script is correct.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.
    """
    if n_arg >= 0 and len(arg) != n_arg:
        print("You must provide {n} arguments to this script" \
              .format(n=n_arg), file=sys.stderr)
        usage(usage_string)
        sys.exit(2)

    new_opts = []
    for (o, a) in opts:
        if o in ("-v", "--verbose"):
            set_verbose(True)
            verbose("Verbose mode on")
        elif o in ("-D", "--debug"):
            set_debug_mode(True)
        elif o in ("-h", "--help"):
            usage(usage_string)
            sys.exit(0)
        else:
            new_opts.append((o, a))
    opts[:] = new_opts


################################################################################

def read_options(shortopts, longopts, treat_options, n_args, usage_string):
    """
        Generic function that parses the input options using the getopt module.
        The options are then treated through the `treat_options` callback.
        
        @param shortopts Short options as defined by getopts, i.e. a sequence of
        letters and colons to indicate arguments.
        
        @param longopts Long options as defined by getopts, i.e. a list of 
        strings ending with "=" to indicate arguments.
        
        @param treat_options Callback function, receives a list of strings to
        indicate parsed options, a list of strings to indicate the parsed 
        arguments and an integer that expresses the expected number of arguments
        of this script.
    """

    for opt in ['v', 'D', 'h']:
        if opt not in shortopts:
            shortopts += opt

    for opt in ['verbose', 'debug', 'help']:
        if opt not in longopts:
            longopts += [opt]

    try:
        opts, arg = getopt.getopt(sys.argv[1:], shortopts, longopts)
    except getopt.GetoptError as err:
        # will print something like "option -a not recognized"
        print(err, file=sys.stderr)
        usage(usage_string)
        sys.exit(-1)

    treat_options(opts, arg, n_args, usage_string)
    return arg


################################################################################             

def strip_xml(the_string):
    """
    	Escapes the XML special characters in the string by replacing them with
    	the corresponding XML entities. The five special characters in XML are :
    	' " < > &

    	@param the_string The unicode object whose characters should be escaped

    	@return an equivalent unicode object where special XML characters were
    	replaced by their corresponding entities
    """
    if not isinstance(the_string, unicode):
        warn_once("Will fail to replace in `bytes` instance")

    cleanContent = the_string
    # First, replace entities with their characters, guaranteeing that, if the
    # text already contains escaped entities, they won't become something like
    # &amp;quot; 
    cleanContent = cleanContent.replace("&apos;", "\'")  # Escape sequence
    cleanContent = cleanContent.replace("&quot;", "\"")  # Escape sequence
    cleanContent = cleanContent.replace("&gt;", ">")  # Escape sequence
    cleanContent = cleanContent.replace("&lt;", "<")  # Escape sequence
    cleanContent = cleanContent.replace("&amp;", "&")  # Escape sequence
    ## Now, replace the characters with the entities
    #cleanContent = cleanContent.replace("&", "&amp;")  # Escape sequence
    #cleanContent = cleanContent.replace("<", "&lt;")  # Escape sequence
    #cleanContent = cleanContent.replace(">", "&gt;")  # Escape sequence
    #cleanContent = cleanContent.replace("\"", "&quot;")  # Escape sequence
    #cleanContent = cleanContent.replace("\'", "&apos;")  # Escape sequence
    ##cleanContent = cleanContent.replace( "*", "&lowast;" ) # Escape WILDCARD
    return cleanContent


################################################################################

def interpret_ngram(argument):
    """
        Parses the argument of the "-n" option. This option is of the form
        "<min>:<max>" and defines the length of n-grams to extract. For 
        instance, "3:5" extracts ngrams that have at least 3 words and at most 5
        words. If you define only <min> or only <max>, the default is to 
        consider that both have the same value. The value of <min> must be at
        least 1. Generates an exception if the syntax is 
        incorrect, generates a None value if the arguments are incoherent 
        (e.g. <max> < <min>)
        
        @param argument String argument of the -n option, has the form 
        "<min>:<max>"
        
        @return A tuple (<min>,<max>) with the two integer limits, or None if
        the argument is incoherent.
    """
    try:
        if ":" in argument:
            [n_min, n_max] = argument.split(":")
            n_min = int(n_min)
            n_max = int(n_max)
        else:
            n_min = int(argument)
            n_max = int(argument)

        if n_min <= n_max:
            if n_min >= 1:
                return ( n_min, n_max )
            else:
                print("Error parsing argument for -n: <min> "
                      "must be at least 1", file=sys.stderr)
                return None
        else:
            print("Error parsing argument for -n: <min> is greater than <max>",
                  file=sys.stderr)
            return None

    except IndexError:
        return None
    except TypeError:
        return None
    except ValueError:
        return None


################################################################################

class MWEToolkitInputError(Exception):
    r"""Raised when the MWE Toolkit detects a bad user input.

    Full stack traces will not be usually provided for these errors,
    as they are NOT supposed to be internal errors in the toolkit.
    For internal errors, use any other exception class.
    """
    def __init__(self, message, depth=0, **extra_info):
        super(MWEToolkitInputError, self).__init__(message.format(**extra_info))
        self.depth = depth
        self.extra_info = extra_info


def error(message, depth=0, **extra_info):
    """Utility function to show error message and quit."""
    raise MWEToolkitInputError(message, depth=depth+1, **extra_info)


################################################################################

_warned = set()

def warn(message, only_once=False, **extra_info):
    """Utility function to show warning message."""
    formatted_message = message.format(**extra_info)
    if only_once:
        # (Maybe we should use a bloom filter, just in case?)
        if formatted_message in _warned: return
        _warned.add(formatted_message)

    if debug_mode:
        print("-" * 40)
        traceback.print_stack()
    print("WARNING:", formatted_message, file=sys.stderr)


def warn_once(message, **extra_info):
    r"""Same as `warn(message, only_once=True)`. Warns only once per error message."""
    warn(message, only_once=True, **extra_info)


################################################################################

def default_exception_handler(type, value, trace):
    """The default exception handler. This replaces Python's standard behavior
    of printing a stack trace and exiting. We don't print a stack trace on some
    user input errors, unless 'debug_mode' is on.
    """
    global debug_mode

    if type == MWEToolkitInputError and not debug_mode:
        import os
        here = os.path.dirname(__file__)
        tb = traceback.extract_tb(trace)[-1-value.depth]
        fname, lineno, func, text = tb
        fname = os.path.relpath(fname, '.')
        print("ERROR:")
        print("=>", value, file=sys.stderr)
        print("-" * 40)
        print("Detected in: \"%s\" (line %d)" % (fname, lineno), file=sys.stderr)
        print("For a full traceback, run with --debug.", file=sys.stderr)

    else:
        traceback.print_exception(type, value, trace)

    if type == KeyboardInterrupt:
        sys.exit(130)  # 128 + SIGINT; Unix standard
    sys.exit(1)


if not hasattr(sys, "ps1"):
    # If not running in interpreter (interactive),
    # set up pretty exception handler
    sys.excepthook = default_exception_handler

#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# index.py is part of mwetoolkit
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
    This script creates an index file for a given corpus. 

    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
from util import usage, read_options, treat_options_simplest, verbose
from libs.indexlib import index_from_corpus, Index

usage_string = """Usage: 
    
python %(program)s OPTIONS -i <index> <corpus.xml>

-i <index> OR --index <index>
    Base name for the output index files. This is used as a prefix for all index
    files generated, such as <index>.lemma.corpus, <index>.lemma.suffix, etc.
    
OPTIONS may be:    

-a <attrs> OR --attributes <attrs>
    Generate indices only for the specified attributes. <attrs> is a
    colon-separated list of attributes (e.g. lemma:pos).

-o OR --old
    Use the old (slower) Python indexer, even when the C indexer is available.

%(common_options)s

    The <corpus.xml> file must be valid XML (dtd/mwetoolkit-corpus.dtd). The -i
<index> option is mandatory.
"""

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global used_attributes, name, build_entry

    treat_options_simplest( opts, arg, n_arg, usage_string )    

    used_attributes = None
    name = None
    for ( o, a ) in opts:
        if o in ("-i", "--index") :
            try :
                name = a
            except IOError :        
                print >> sys.stderr, "Error opening the index."
                print >> sys.stderr, "Try again with another index filename."
                sys.exit( 2 )
        elif o in ("-a", "--attributes"): 
            used_attributes = a.split(":")
        elif o in ("-o", "--old"):
            Index.use_c_indexer(False)
            
    if name is None:     
        print >> sys.stderr, "ERROR: You must provide a filename for the index."
        print >> sys.stderr, "Option -i is mandatory."
        usage( usage_string )
        sys.exit( 2 )   
                            

# MAIN SCRIPT

longopts = ["index=", "attributes=", "old" ]
arg = read_options( "i:a:o", longopts, treat_options, 1, usage_string )

index_from_corpus(arg[0], name, used_attributes)    

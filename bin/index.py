#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import error, treat_options_simplest, read_options
from libs.filetype import indexlib

################################################################################

usage_string = """Usage: 
    
python {program} OPTIONS -i <index> <corpus>

-i <index> OR --index <index>
    Base name for the output index files. This is used as a prefix for all index
    files generated, such as <index>.lemma.corpus, <index>.lemma.suffix, etc.
    
The <corpus> input file must be in one of the filetype
formats accepted by the `--from` switch.

The -i <index> option is mandatory.


OPTIONS may be:    

-a <attrs> OR --attributes <attrs>
    Generate indices only for the specified attributes. <attrs> is a
    colon-separated list of attributes (e.g. lemma:pos:lemma+pos).

-o OR --old
    Use the old (slower) Python indexer, even when the C indexer is available.

--from <input-filetype-ext>
    Force reading of corpus with given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}
   

-m OR --moses
    (DEPRECATED. Use --from=Moses instead).
    Uses Moses factored corpus format as input. This format must be pure text in
    UTF-8, one sentence per line, tokens separated by spaces, each token being:
    surface|lemma|POStag|deprel:head
    Which are equivalent to the xml fields. Empty fields should be left blank,
    but every token must have 3 vertical bars. The actual character for vertical
    bars must be escabed and replaced by a placeholder that does not contain
    this character (e.g. %%VERTICAL_BAR%%)
    
-c OR --conll
    (DEPRECATED. Use --from=CONLL instead).
    Uses CoNLL shared task format as input. This format must be pure text in 
    UTF-8, one word per line, sentences separated by blank lines, each line 
    containing 10 tab-separated fields:
    
    ID	form	lemma	cPOStag	POStag	feats	head	deprel	pHead	pDeprel
    
    Fields POStag, feats, pHead and pDeprel are ignored. ID is a numerical token 
    identifier (1,2,3...), form is the surface form, lemma is the lemma, cPOStag
    is the coarse part of speech, head is the ID of the token on which the 
    current token depends syntactically, and deprel is the type of syntactic 
    relation. Empty fields should contain an underscore "_"

{common_options}
"""
use_text_format = None
input_filetype_ext = None
basename = None


################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global used_attributes
    global basename
    global build_entry
    global use_text_format
    global input_filetype_ext

    treat_options_simplest( opts, arg, n_arg, usage_string )

    used_attributes = ["lemma", "pos", "surface", "syn"]
    for ( o, a ) in opts:
        if o in ("-i", "--index") :
            basename = a
        elif o == "--from":
            input_filetype_ext = a
        elif o in ("-a", "--attributes"):
            used_attributes = a.split(":")
        elif o in ("-m", "--moses"):
            use_text_format = "moses"
        elif o in ("-c", "--conll"):
            use_text_format = "conll"            
        elif o in ("-o", "--old"):
            indexlib.Index.use_c_indexer(False)
            
    if basename is None:     
        error("You must provide a filename for the index.\n"
              "Option -i is mandatory.")

                            
################################################################################
# MAIN SCRIPT

longopts = ["from=", "index=", "attributes=", "old", "moses", "conll" ]
arg = read_options( "i:a:omc", longopts, treat_options, -1, usage_string )

simple_attrs = [a for a in used_attributes if '+' not in a]
composite_attrs = [a for a in used_attributes if '+' in a]

for attrs in [attr.split('+') for attr in composite_attrs]:
    for attr in attrs:
        if attr not in simple_attrs:
            simple_attrs.append(attr)


index = indexlib.Index(basename, simple_attrs)
indexlib.populate_index(index, arg, input_filetype_ext)
for attr in composite_attrs:
    index.make_fused_array(attr.split('+'))
index.build_suffix_arrays()
index.save_main()

#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
# 
# transform.py is part of mwetoolkit
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
    Executes python string for each element of given input.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs import util
from libs import filetype


################################################################################
# GLOBALS

usage_string = """Usage:

python {program} -w <python-code> OPTIONS <input-file>

-w <python-code> OR --each-word <python-code>
    Run python code for each word in the input files.

    The only things guaranteed to exist in the
    environment are the __builtins__ and the following:
    * `word.surface`: a settable string with the surface form, or None.
    * `word.lemma`: a settable string with the word's lemma, or None.
    * `word.pos`: a settable string with the word's part-of-speech, or None.

The <input-file> must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--begin <python-code>
    Run python code before parsing input.
    Only __builtins__ is guaranteed to exist in the environment.

--end <python-code>
    Run python code after everything else.
    Only __builtins__ is guaranteed to exist in the environment.

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[ALL]}

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, keeps input in original format):
    {descriptions.output[ALL]}

{common_options}
"""
executable_w = ""
executable_beg = ""
executable_end = ""
input_filetype_ext = None
output_filetype_ext = None


################################################################################

class TransformHandler(filetype.ChainedInputHandler):
    """For each entity in the file, prints it if the limit is still not
    achieved. No buffering as in tail, this is not necessary here.
    """
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
            self.global_dict = {}
            exec(executable_beg, self.global_dict)
        self.chain.before_file(fileobj, info)

    def finish(self):
        self.chain.finish()
        exec(executable_end, self.global_dict)

    def _fallback_entity(self, entity, info={}):
        for word in entity.word_list:
            self.global_dict["word"] = self.global_dict["w"] = word
            exec(executable_w, self.global_dict)
        self.chain.handle(entity, info)
        
    def handle_pattern(self, pattern, info={}):
        self.chain.handle_pattern(pattern, info)


################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.
    """
    global executable_w
    global executable_beg
    global executable_end
    global input_filetype_ext
    global output_filetype_ext
    
    util.treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o == "--from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        elif o == "--begin":
            executable_beg = compile(a, "<cmdline:--begin>", "exec")
        elif o == "--end":
            executable_end = compile(a, "<cmdline:--end>", "exec")
        elif o in ("-w", "--each-word"):
            executable_w = compile(a, "<cmdline:--each-word>", "exec")
        else:
            raise Exception("Bad arg " + o)

################################################################################
# MAIN SCRIPT

longopts = ["from=", "to=", "begin=", "end=", "each-word="]
args = util.read_options("w:", longopts, treat_options, -1, usage_string)
filetype.parse(args, TransformHandler(), input_filetype_ext)

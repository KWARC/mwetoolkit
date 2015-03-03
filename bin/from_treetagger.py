#!/usr/bin/python
# -*- coding:UTF-8 -*-

# ###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# treetagger2xml.py is part of mwetoolkit
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
    This script transforms the output format of TreeTagger to the XML format of
    a corpus, as required by the mwetoolkit scripts. The script is language
    independent as it does not transform the information. You can chose either
    to use sentence splitting of the treetagger (default) or to keep the 
    original sentence splitting. In the latter case, you should add a sentence
    delimiter </s> at the end of each sentence before tagging the text. Only
    UTF-8 text is accepted.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import read_options, treat_options_simplest, warn
from libs.base.word import Word
from libs.base.sentence import Sentence
from libs import filetype


################################################################################     
# GLOBALS     

usage_string = """Usage: 
    
python {program} OPTIONS <corpus.TreeTagger>

The TreeTagger input must have a "</s>" line at the end of each
sentence. This tag will be used to discover the original sentence splitting. 
This behavior is particularly useful when dealing with parallel corpora in 
which the sentence alignment cannot be messed up by the tagger.

IMPORTANT: If you do not have a "</s>"-delimited input file, you must
use the `--sentence` option to select the POS-tag that indicates the
sentence splitting character, otherwise, the result may look like a
corpus with a single (very long) line.


OPTIONS may be:

-s <sent> OR --sentence <sent>
    Name of the POS tag that the TreeTagger uses to separate sentences. Please,
    specify this if you're not using the "</s>" segmentation. For example,
    when parsing English texts, one should indicate `--sentence="SENT"`.

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, converts input to "XML" format):
    {descriptions.output[corpus]}

{common_options}
"""
sent_split = None
output_filetype_ext = "XML"


################################################################################     


class TreeTaggerInfo(filetype.common.FiletypeInfo):
    r"""FiletypeInfo subclass for TreeTagger format."""
    description = "3-field tab-separated format output by TreeTagger"
    filetype_ext = "TreeTagger"
  
    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("|", "${pipe}"), ("#", "${hash}"),
                    ("<", "${lt}"), (">", "${gt}"), (" ", "${space}"),
                    ("\t", "${tab}")]

    def operations(self):
        return filetype.common.FiletypeOperations(
                None, None, TreeTaggerParser)


INFO = TreeTaggerInfo()


class TreeTaggerParser(filetype.common.AbstractTxtParser):
    r"""Parse file in TreeTagger TAB-separated format:
    One word per line, each word is in format "surface\tpos\tlemma".
    Optional sentence separators "</s>" may also constitute a word on a line.
    """
    filetype_info = INFO
    valid_categories = ["corpus"]

    def __init__(self, *args):
        super(TreeTaggerParser, self).__init__(*args)
        self.category = "corpus"
        self.words = []
        self.s_id = 0

    def _parse_line(self, line, handler, info={}):
        global sent_split
        sentence = None

        if not self.words:
            self.new_partial(self.finish_sentence, handler)

        if line == "</s>":
            self.flush_partial_callback()

        else:
            fields = line.split("\t")
            if len(fields) != 3:
                warn("Ignoring line {} (it has {} entries)" \
                        .format(info["linenum"], len(fields)))
                return

            surface, pos, lemma = fields
            word = Word(surface, lemma, pos)
            self.words.append(word)

            if pos == sent_split:
                self.flush_partial_callback()

    def finish_sentence(self, handler):
        r"""Finish building sentence and call handler."""
        handler.handle_sentence(Sentence(self.words, self.s_id), {})
        self.s_id += 1
        self.words = []


################################################################################

def treat_options(opts, arg, n_arg, usage_string):
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.
    @param usage_string Instructions that appear if you run the program with
    the wrong parameters or options.
    """
    global sent_split
    global output_filetype_ext

    treat_options_simplest(opts, arg, n_arg, usage_string)

    for ( o, a ) in opts:
        if o in ("-s", "--sentence"):
            sent_split = a
        elif o == "--to":
            output_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)



################################################################################     
# MAIN SCRIPT

longopts = ["sentence=", "to="]
args = read_options("s:", longopts, treat_options, -1, usage_string)
printer = filetype.AutomaticPrinterHandler(output_filetype_ext)
TreeTaggerParser(args, "utf-8").parse(filetype.FirstInputHandler(printer))

#!/usr/bin/python
# -*- coding:UTF-8 -*-

"""
    This script converts an XML corpus into plain-text, one word per line,
    with a blank line ending each sentence.  Only the word attributes specified
    by the -a option are output.
    
    All specified attributes of a word are output in the same line, separated by
    the ATTRIBUTE_SEPARATOR character. The produced output is suitable as input
    for the C indexer.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.sentence import Sentence
from xmlhandler.classes.word import Word, WORD_ATTRIBUTES
from xmlhandler.classes.__common import ATTRIBUTE_SEPARATOR
from util import usage, read_options, treat_options_simplest, verbose

def xml2txt(corpus, outfile, attributes):
	def print_sentence(sentence):
		for word in sentence.word_list:
			vals = [getattr(word, attr) for attr in attributes]
			print >>outfile, ATTRIBUTE_SEPARATOR.join(vals)
		print >>outfile, ""

	parser = xml.sax.make_parser()
	parser.setContentHandler(CorpusXMLHandler(print_sentence))
	parser.parse(corpus)


### Main script.

usage_string = """Usage:

python %(program)s -a <attributes> <corpus.xml>

-a <attributes> OR --attributes <attributes>
    A colon-separated list of attributes to output.

<corpus.xml> must be a valid XML file (mwetoolkit-corpus.dtd).
"""

attributes = None

def treat_options(opts, arg, n_arg, usage_string):
	global attributes
	for (o, a) in opts:
		if o in ("-a", "--attributes"):
			attributes = a.split(":")
			for attr in attributes:
				if attr not in WORD_ATTRIBUTES:
					print >>sys.stderr, "Unknown attribute '%s'!" % attr
					sys.exit(2)

	if attributes is None:
		print >>sys.stderr, "The option -a <attributes> is mandatory."
		usage(usage_string)
		sys.exit(2)

	treat_options_simplest( opts, arg, n_arg, usage_string )

longopts = ["atttibutes="]
arg = read_options("a:", longopts, treat_options, 1, usage_string)

try:
	xml2txt(arg[0], sys.stdout, attributes)

except Exception, err:
	print >>sys.stderr, err
	sys.exit(3)

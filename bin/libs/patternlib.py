"""
	patternlib.py - Functions for manipulating complex ngram patterns.
"""

from xml.dom import minidom
from xmlhandler.classes.word import Word, WORD_ATTRIBUTES
from xmlhandler.classes.__common import ATTRIBUTE_SEPARATOR, WORD_SEPARATOR
import re
import sys

ATTRIBUTE_WILDCARD = "[^" + ATTRIBUTE_SEPARATOR + WORD_SEPARATOR + "]*"
WORD_FORMAT = ATTRIBUTE_SEPARATOR.join(map(lambda s: "%(" + s + ")s", WORD_ATTRIBUTES))

def parse_patterns_file(path):
	patterns = []
	doc = minidom.parse(path)
	
	for root in doc.childNodes:
		if isinstance(root, minidom.Element):
			# Found root element.
			for node in root.childNodes:
				if isinstance(node, minidom.Element):
					patterns.append(parse_pattern(node))

	return patterns

class State:
	pass

def parse_pattern(node):
	# TODO: Eliminate duplication.

	state = State()
	state.pattern = WORD_SEPARATOR

	def parse(node):
		if node.nodeName == "pat":
			id = node.getAttribute("id")
			repeat = node.getAttribute("repeat")
			if id:
				state.pattern += "(?P<%s>" % id
			elif repeat:
				state.pattern += "(?:"

			for subnode in node.childNodes:
				if isinstance(subnode, minidom.Element):
					parse(subnode)

			if id or repeat:
				state.pattern += ")"
			if repeat:
				state.pattern += repeat

		elif node.nodeName == "either":
			id = node.getAttribute("id")
			repeat = node.getAttribute("repeat")
			if id:
				state.pattern += "(?P<%s>" % id
			else:
				state.pattern += "(?:"

			first_pattern = True
			for subnode in node.childNodes:
				if isinstance(subnode, minidom.Element):
					if first_pattern:
						first_pattern = False
					else:
						state.pattern += "|"

					parse(subnode)

			state.pattern += ")"
			if repeat:
				state.pattern += repeat

		elif node.nodeName == "backpat":
			id = node.getAttribute("id")
			state.pattern += "(?P=%s)" % id

		elif node.nodeName == "w":
			attrs = {}
			id = node.getAttribute("id")
			for attr in WORD_ATTRIBUTES:
				val = re.escape(node.getAttribute(attr)).replace("\\*", ATTRIBUTE_WILDCARD)
				attrs[attr] = val or ATTRIBUTE_WILDCARD
				if id:
					attrs[attr] = "(?P<%s_%s>%s)" % (id, attr, attrs[attr])

			state.pattern += WORD_FORMAT % attrs + WORD_SEPARATOR

		elif node.nodeName == "backw":
			attrs = {}
			for attr in WORD_ATTRIBUTES:
				id = node.getAttribute(attr)
				if id:
					attrs[attr] = "(?P=%s_%s)" % (id, attr)
				else:
					attrs[attr] = ATTRIBUTE_WILDCARD

			state.pattern += WORD_FORMAT % attrs + WORD_SEPARATOR

		else:
			raise Exception, "Invalid node name '%s'" % node.nodeName


	parse(node)
	return re.compile(state.pattern)


def match_pattern(pattern, words):
	# Returns an iterator over all matches of the pattern in the word list.

	wordstring = WORD_SEPARATOR
	positions = []
	for word in words:
		positions.append(len(wordstring))
		attrs = {}
		for attr in WORD_ATTRIBUTES:
			attrs[attr] = getattr(word, attr)
		wordstring += WORD_FORMAT % attrs + WORD_SEPARATOR

	limit = len(wordstring)

	for current_start in positions:
		current_end = limit
		while True:
			result = pattern.match(wordstring, current_start - 1, current_end)
			if result:
				start = result.start()
				end = result.end()
				current_end = end - 1
				ngram = []
				for i in xrange(len(words)):	
					if positions[i] >= start and positions[i] < end:
						ngram.append(words[i])
				yield ngram

			else:
				break


def build_generic_pattern(min, max):
	# Returns a pattern matching any ngram of size min~max.

	pattern = WORD_SEPARATOR + "(?:[^%s]*" % WORD_SEPARATOR + \
	          WORD_SEPARATOR + ")" + "{%d,%d}" % (min, max)

	return re.compile(pattern)


def patternlib_test():
	# For debugging.

	def show(lls):
		for ls in lls:
			print ' '.join(map(lambda x: x.surface, ls))

	p = parse_patterns_file("/tmp/a.xml")  # pattern: N+
	ws = [Word("the", "the", "Det", "x", []),
	      Word("foos", "foo", "N", "x", []),
	      Word("bars", "bar", "V", "x", []),
	      Word("quuxes", "quux", "N", "x", []),
	      Word("foose", "foo", "N", "x", [])]
	show(match_pattern(p[0], ws))
	#show(match_pattern(build_generic_pattern(2,3), ws))

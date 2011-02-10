"""
	patternlib.py - Functions for manipulating complex ngram patterns.
"""

from xml.dom import minidom
from xmlhandler.classes.word import Word
import re
import sys

ATTRIBUTE_SEPARATOR="\35"   # ASCII level 2 separator
WORD_SEPARATOR="\34"        # ASCII level 1 separator
WORD_ATTRIBUTES = ["surface", "lemma", "pos", "syn"]

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
			ref = node.getAttribute("ref")
			repeat = node.getAttribute("repeat")
			if ref:
				state.pattern += "(?P<%s>" % ref
			elif repeat:
				state.pattern += "(?:"

			for subnode in node.childNodes:
				if isinstance(subnode, minidom.Element):
					parse(subnode)

			if ref or repeat:
				state.pattern += ")"
			if repeat:
				state.pattern += repeat

		elif node.nodeName == "either":
			ref = node.getAttribute("ref")
			repeat = node.getAttribute("repeat")
			if ref:
				state.pattern += "(?P<%s" % ref
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

		elif node.nodeName == "backref":
			ref = node.getAttribute("ref")
			state.pattern += "(?P=%s)" % ref

		elif node.nodeName == "w":
			attrs = {}
			for attr in WORD_ATTRIBUTES:
				attrs[attr] = re.escape(node.getAttribute(attr)) or ATTRIBUTE_WILDCARD
			state.pattern += WORD_FORMAT % attrs + WORD_SEPARATOR

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

	current_start = 0
	limit = len(wordstring)
	match_found = True

	while match_found:
		match_found = False
		current_end = limit
		start = None

		while True:
			result = pattern.search(wordstring, current_start, current_end)
			if result:
				match_found = True
				if start is None:
					start = result.start()     # Find least start with a match
				end = result.end()
				current_end = end - 1
				ngram = []
				for i in xrange(len(words)):	
					if positions[i] >= start and positions[i] < end:
						ngram.append(words[i])
				yield ngram

			else:
				if start is not None:
					current_start = start + 1
				break

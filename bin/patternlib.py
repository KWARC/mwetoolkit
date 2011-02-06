from xml.dom import minidom
from xmlhandler.classes.word import Word
import re

ATTRIBUTE_SEPARATOR=":"
WORD_SEPARATOR="#"
WORD_ATTRIBUTES = ["surface", "lemma", "pos", "syn"]

ATTRIBUTE_WILDCARD = "[^" + ATTRIBUTE_SEPARATOR + WORD_SEPARATOR + "]*"
WORD_FORMAT = ATTRIBUTE_SEPARATOR.join(map(lambda s: "%(" + s + ")s", WORD_ATTRIBUTES))
# TODO: Python's lambda syntax is horrible...

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
	state.last_ref_num = 0
	state.ref_to_num = {}
	state.pattern = WORD_SEPARATOR

	def parse(node):
		if node.nodeName == "pat":
			ref = node.getAttribute("ref")
			star = node.getAttribute("star")
			if ref:
				state.last_ref_num += 1
				state.ref_to_num += {ref: state.last_ref_num}
				state.pattern += "("

			for subnode in node.childNodes:
				if isinstance(subnode, minidom.Element):
					parse(subnode)

			if ref:
				state.pattern += ")"
			if star:
				state.pattern += "*"

		elif node.nodeName == "either":
			ref = node.getAttribute("ref")
			star = node.getAttribute("star")
			state.last_ref_num += 1
			state.pattern += "("
			if ref:
				state.ref_to_num += {ref: state.last_ref_num}

			first = True
			for subnode in node.childNodes:
				if isinstance(subnode, minidom.Element):
					if first:
						first = False
					else:
						state.pattern += "|"

					parse(subnode)

			state.pattern += ")"
			if star:
				state.pattern += "*"

		elif node.nodeName == "backref":
			ref = node.getAttribute("ref")
			state.pattern += ("\\" + state.ref_to_num[ref])

		elif node.nodeName == "w":
			attrs = {}
			for attr in WORD_ATTRIBUTES:
				attrs[attr] = node.getAttribute(attr) or ATTRIBUTE_WILDCARD
			state.pattern += WORD_FORMAT % attrs + WORD_SEPARATOR

	parse(node)
	# print "Read:", state.pattern
	return re.compile(state.pattern)


def match_pattern_single(pattern, words):
	wordstring = WORD_SEPARATOR
	positions = []
	for word in words:
		positions.append(len(wordstring))
		attrs = {}
		for attr in WORD_ATTRIBUTES:
			attrs[attr] = getattr(word, attr)
		wordstring += WORD_FORMAT % attrs + WORD_SEPARATOR

	result = pattern.search(wordstring)
	if result:
		start = result.start()
		end = result.end()
		ngram = []
		for i in xrange(len(words)):	
			if positions[i] > start and positions[i] < end:
				ngram.append(words[i])

		return ngram  ## TODO: return multiple matches

	else:
		return None

def match_pattern(pattern, words):
	# Returns an iterator over all matches of the pattern in the word list.
	# TODO: Overlapping matches with the *same* start are not caught.
	# E.g.: matching N+ on N N.

	wordstring = WORD_SEPARATOR
	positions = []
	for word in words:
		positions.append(len(wordstring))
		attrs = {}
		for attr in WORD_ATTRIBUTES:
			attrs[attr] = getattr(word, attr)
		wordstring += WORD_FORMAT % attrs + WORD_SEPARATOR

	current_position = 0
	while True:
		result = pattern.search(wordstring, current_position)
		if result:
			start = result.start()
			end = result.end()
			current_position = start + 1
			ngram = []
			for i in xrange(len(words)):	
				if positions[i] >= start and positions[i] < end:
					ngram.append(words[i])
			yield ngram

		else:
			return


t=parse_patterns_file("/tmp/foo.xml")

ws = [Word("a", "ae", "N", "", []),
      Word("a", "ae", "Adj", "", []),
      Word("foos", "foo", "T", "", []),
      Word("a", "ae", "V", "", []),
      Word("ae", "quux", "N", "", [])]

m =  match_pattern(t[0], ws)

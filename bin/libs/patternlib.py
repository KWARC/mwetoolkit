"""
	patternlib.py - Functions for manipulating complex ngram patterns.
"""

from xml.dom import minidom
from xmlhandler.classes.word import Word, WORD_ATTRIBUTES
from xmlhandler.classes.__common import ATTRIBUTE_SEPARATOR, WORD_SEPARATOR
import re
import sys

ATTRIBUTE_WILDCARD = "[^" + ATTRIBUTE_SEPARATOR + WORD_SEPARATOR + "]*"
WORD_FORMAT = ATTRIBUTE_SEPARATOR.join(map(lambda s: "%(" + s + ")s", ["wordnum"] + WORD_ATTRIBUTES))

def parse_patterns_file(path):
	"""
		Generates a list of precompiled regular expressions, one for each
		pattern in `file`.

		@param `file` The path for a patterns XML file (mwetoolkit-patterns.dtd).
	"""

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
	"""
		Generates a precompiled regular expression from a pattern description.

		@param node An `xml.dom.Element` from the patterns file representing
		a single pattern.
	"""

	state = State()
	state.pattern = WORD_SEPARATOR
	state.temp_id = 0
	state.defined_ids = []
	state.forepattern_ids = {}	

	def parse(node):
		if node.nodeName == "pat":
			id = node.getAttribute("id")
			repeat = node.getAttribute("repeat")
			ignore = node.getAttribute("ignore")

			if ignore:
				state.pattern += "(?P<ignore_%d>" % state.temp_id
				state.temp_id += 1

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

			if ignore:
				state.pattern += ")"

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
			attrs = { "wordnum": ATTRIBUTE_WILDCARD }
			id = node.getAttribute("id")
			for attr in WORD_ATTRIBUTES:
				val = node.getAttribute(attr)
				if val.startswith("back:"):
					(refid, refattr) = val.split(":")[1].split(".")
					val = "(?P=%s_%s)" % (refid, refattr)

				elif val:
					val = re.escape(val).replace("\\*", ATTRIBUTE_WILDCARD)

				else:
					val = ATTRIBUTE_WILDCARD

				attrs[attr] = val

			
			if id:
				if id in state.forepattern_ids:
					attrs["wordnum"] = "(?P=%s)" % state.forepattern_ids[id]
				for attr in attrs:
					attrs[attr] = "(?P<%s_%s>%s)" % (id, attr, attrs[attr])
				if id in state.defined_ids:
					raise Exception, "Id '%s' defined twice" % id
				state.defined_ids.append(id)

			syndep = node.getAttribute("syndep")
			if syndep:
				(deptype, depref) = syndep.split(":")
				if depref in state.defined_ids:
					# Backreference.
					attrs["syn"] = (ATTRIBUTE_WILDCARD +
					               ";%s:(?P=%s_wordnum);" % (deptype, depref) +
					               ATTRIBUTE_WILDCARD)
				else:
					# Fore-reference.
					foredep = "foredep_%d" % state.temp_id
					state.temp_id += 1
					state.forepattern_ids[depref] = foredep

					attrs["syn"] = (ATTRIBUTE_WILDCARD +
					                ";%s:(?P<%s>[0-9]*);" % (deptype, foredep) +
					                ATTRIBUTE_WILDCARD)

			state.pattern += WORD_FORMAT % attrs + WORD_SEPARATOR

		elif node.nodeName == "backw":
			# Obsolete. Use "back:id.attribute" syntax instead.
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
	"""
		Returns an iterator over all matches of the pattern in the word list.
	"""

	wordstring = WORD_SEPARATOR
	positions = []
	wordnum = 1
	for word in words:
		positions.append(len(wordstring))
		attrs = { "wordnum": wordnum }
		for attr in WORD_ATTRIBUTES:
			attrs[attr] = getattr(word, attr)
		attrs["syn"] = ";" + attrs["syn"] + ";"
		wordstring += WORD_FORMAT % attrs + WORD_SEPARATOR
		wordnum += 1

	limit = len(wordstring)

	for current_start in positions:
		current_end = limit
		while True:
			result = pattern.match(wordstring, current_start - 1, current_end)

			if result:
				# Beware: [x for x ...] exposes the variable x to the surrounding environment.
				ignore_ids = [id for id in result.groupdict().keys() if id.startswith("ignore_")]
				ignore_spans = [result.span(id) for id in ignore_ids]

				start = result.start()
				end = result.end()
				current_end = end - 1
				ngram = []
				for i in xrange(len(words)):
					if positions[i] >= start and positions[i] < end:
						while ignore_spans and ignore_spans[0][1] <= positions[i]:
							# If the ignore-end is before this point, we don't need it anymore.
							ignore_spans = ignore_spans[1:] # Inefficient?
						if not (ignore_spans and positions[i] >= ignore_spans[0][0]):
							ngram.append(words[i])
				yield ngram

			else:
				break


def build_generic_pattern(min, max):
	"""
		Returns a pattern matching any ngram of size min~max.
	"""

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
	      Word("foose", "foo", "N", "x", []),
	      Word("etiam", "etiam", "N", "x", [])]
	show(match_pattern(p[0], ws))
	#show(match_pattern(build_generic_pattern(2,3), ws))

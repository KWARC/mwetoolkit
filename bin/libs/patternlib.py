"""
    patternlib.py - Functions for manipulating complex ngram patterns.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from xml.dom import minidom
from xmlhandler.classes.word import Word, WORD_ATTRIBUTES
from xmlhandler.classes.ngram import Ngram
import re
import sys



def parse_patterns_file(path, anchored=False):
    """Generates a list of precompiled regular expressions, one for each
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
                    if anchored:
                        node.setAttribute("anchor_start", "true")
                        node.setAttribute("anchor_end", "true")
                    patterns.append(parse_pattern(node))
    return patterns


########################################

def parse_pattern(node):
    """Generates a precompiled regular expression from a pattern description.

    @param node An `xml.dom.Element` from the patterns file representing
    a single pattern.
    """
    return Parser().parse(node)


def match_pattern(pattern, words):
    """DEPRECATED: Call `pattern.matches(words)` directly instead.
    Returns an iterator over all matches of the pattern in the word list."""
    return pattern.matches(words)


def build_generic_pattern(min, max):
    """Returns a pattern matching any ngram of size min~max."""
    # TODO make this implementation less hack-ish
    p = Parser()
    p.pattern = p.WORD_SEPARATOR + "(?:[^%s]*" % p.WORD_SEPARATOR + \
              p.WORD_SEPARATOR + ")" + "{%d,%d}" % (min, max)
    p._post_parsing()
    return p


########################################

class Parser(object):
    from xmlhandler.classes.__common import ATTRIBUTE_SEPARATOR, WORD_SEPARATOR
    ATTRIBUTE_WILDCARD = "[^" + ATTRIBUTE_SEPARATOR + WORD_SEPARATOR + "]*"
    WORD_FORMAT = ATTRIBUTE_SEPARATOR.join("%("+s+")s" for s in (["wordnum"] + WORD_ATTRIBUTES))

    def __init__(self):
        self.temp_id = 0
        self.defined_ids = []
        self.forepattern_ids = {}

    def parse(self, node):
        self.node = node
        self.pattern = self.WORD_SEPARATOR
        self._do_parse(node)
        self._post_parsing()
        return self

    def _post_parsing(self):
        self.compiled_pattern = re.compile(self.pattern)

    def _do_parse(self, node):
        if node.nodeName == "pat":
            self._parse_pat(node)
        elif node.nodeName == "neg":
            self._parse_neg(node)
        elif node.nodeName == "either":
            self._parse_either(node)

        elif node.nodeName == "backpat": 
            id = node.getAttribute("id")
            self.pattern += "(?P=%s)" % id

        elif node.nodeName == "w":
            self._parse_w(node)
        elif node.nodeName == "backw":
            # Obsolete. Use "back:id.attribute" syntax instead.
            self._parse_backw(node)
        else:
            raise Exception, "Invalid node name '%s'" % node.nodeName


    def _parse_pat(self, node):
        id = node.getAttribute("id")
        repeat = node.getAttribute("repeat")
        ignore = node.getAttribute("ignore")
        anchor_start = node.getAttribute("anchor_start")
        anchor_end = node.getAttribute("anchor_end")

        if anchor_start:
            if self.pattern == self.WORD_SEPARATOR:
                self.pattern = "^" + self.WORD_SEPARATOR
            else:
                raise Exception, "Pattern anchoring is currently only supported in non-nested <pat> elements."

        if ignore:
            self.pattern += "(?P<ignore_%d>" % self.temp_id
            self.temp_id += 1

        if id:
            self.pattern += "(?P<%s>" % id
        elif repeat:
            self.pattern += "(?:"

        for subnode in node.childNodes:
            if isinstance(subnode, minidom.Element):
                self._do_parse(subnode)

        if id or repeat:
            self.pattern += ")"
        if repeat:
            if repeat != "*" and repeat != "?" and repeat != "+" and \
                not re.match(r"^\{[0-9]*,[0-9]*\}|\{[0-9]+\}$",repeat ) :
                warningrepeat = "WARNING: invalid repeat pattern: " + repeat
                print(warningrepeat, file=sys.stderr)
            self.pattern += repeat

        if ignore:
            self.pattern += ")"

        if anchor_end:
            self.pattern += "$"


    def _parse_either(self, node):
        id = node.getAttribute("id")
        repeat = node.getAttribute("repeat")
        if id:
            self.pattern += "(?P<%s>" % id
        else:
            self.pattern += "(?:"

        first_pattern = True
        for subnode in node.childNodes:
            if isinstance(subnode, minidom.Element):
                if first_pattern:
                    first_pattern = False
                else:
                    self.pattern += "|"

                self._do_parse(subnode)

        self.pattern += ")"
        if repeat:
            self.pattern += repeat


    def _parse_neg(self, node):
        self.pattern += "(?!"
        for subnode in node.childNodes:
            if isinstance(subnode, minidom.Element):
                self._do_parse(subnode)
        self.pattern += ")"


    def _parse_w(self, node):
        negated = node.getAttribute("neg")      
        attrs = { "wordnum": self.ATTRIBUTE_WILDCARD }
        id = node.getAttribute("id")
        for attr in WORD_ATTRIBUTES:
            val = node.getAttribute(attr)
            if val.startswith("back:"):
                (refid, refattr) = val.split(":")[1].split(".")
                val = "(?P=%s_%s)" % (refid, refattr)

            elif val:
                val = re.escape(val).replace("\\*", self.ATTRIBUTE_WILDCARD)

            else:
                val = self.ATTRIBUTE_WILDCARD
            if attr in negated.split(":") :
                if val != self.ATTRIBUTE_WILDCARD :
                    val = "(?!" + val + ")" + self.ATTRIBUTE_WILDCARD
                else :
                    raise Exception, "You cannot negate an undefined \
attribute: " + attr + "\nIn: " + node.toxml()
            attrs[attr] = val

        
        if id:
            if id in self.forepattern_ids:
                attrs["wordnum"] = "(?P=%s)" % self.forepattern_ids[id]
            for attr in attrs:
                attrs[attr] = "(?P<%s_%s>%s)" % (id, attr, attrs[attr])
            if id in self.defined_ids:
                raise Exception, "Id '%s' defined twice" % id
            self.defined_ids.append(id)

        syndep = node.getAttribute("syndep")
        if syndep:
            (deptype, depref) = syndep.split(":")
            if depref in self.defined_ids:
                # Backreference.
                attrs["syn"] = (self.ATTRIBUTE_WILDCARD +
                               ";%s:(?P=%s_wordnum);" % (deptype, depref) +
                               self.ATTRIBUTE_WILDCARD)
            else:
                # Fore-reference.
                foredep = "foredep_%d" % self.temp_id
                self.temp_id += 1
                self.forepattern_ids[depref] = foredep

                attrs["syn"] = (self.ATTRIBUTE_WILDCARD +
                                ";%s:(?P<%s>[0-9]*);" % (deptype, foredep) +
                                self.ATTRIBUTE_WILDCARD)

        self.pattern += self.WORD_FORMAT % attrs + self.WORD_SEPARATOR


    def _parse_backw(self, node):
        # Obsolete. Use "back:id.attribute" syntax instead.
        for attr in WORD_ATTRIBUTES:
            id = node.getAttribute(attr)
            if id:
                attrs[attr] = "(?P=%s_%s)" % (id, attr)
            else:
                attrs[attr] = self.ATTRIBUTE_WILDCARD
        self.pattern += self.WORD_FORMAT % attrs + self.WORD_SEPARATOR


    def matches(self, words, match_distance="All", overlapping=True):
        """Returns an iterator over all matches of the pattern in the word list.
        Each iteration yields a pair `(ngram, match_indexes)`.
        """
        wordstring = self.WORD_SEPARATOR
        positions = []
        wordnum = 1
        for word in words:
            positions.append(len(wordstring))
            attrs = { "wordnum": wordnum }
            for attr in WORD_ATTRIBUTES:
                attrs[attr] = getattr(word, attr)
            attrs["syn"] = ";" + attrs["syn"] + ";"
            wordstring += self.WORD_FORMAT % attrs + self.WORD_SEPARATOR
            wordnum += 1

        i = 0
        while i < len(positions):
            matches_here = list(self._matches_at(words, wordstring,
                    positions[i], len(wordstring), positions))

            if match_distance == "All":
                if not overlapping:
                    raise Exception("All requires Overlapping")
                for m in matches_here:
                    yield m
            elif match_distance == "Longest":
                if matches_here:
                    yield matches_here[0]
                    increment = len(matches_here[0][0])
            elif match_distance == "Shortest":
                if matches_here:
                    yield matches_here[-1]
                    increment = len(matches_here[-1][0])
            else:
                raise Exception("Bad match_distance: " + match_distance)

            i += 1 if overlapping else increment


    def _matches_at(self, words, wordstring, current_start, limit, positions):
        current_end = limit
        matches_here = []
        while True:
            result = self.compiled_pattern.match(wordstring, current_start - 1, current_end)
            if not result: return

            # Beware: [x for x ...] exposes the variable x to the surrounding environment.
            #pdb.set_trace()
            ignore_ids = [id for id in result.groupdict().keys() if id.startswith("ignore_")]
            ignore_spans = [result.span(id) for id in ignore_ids]

            start = result.start()
            end = result.end()
            current_end = end - 1
            ngram = []
            wordnums = []
            for i in xrange(len(words)):
                if positions[i] >= start and positions[i] < end:
                    while ignore_spans and ignore_spans[0][1] <= positions[i]:
                        # If the ignore-end is before this point, we don't need it anymore.
                        ignore_spans = ignore_spans[1:] # Inefficient?
                    if not (ignore_spans and positions[i] >= ignore_spans[0][0]):
                        ngram.append(words[i])
                        wordnums.append(i+1)
            yield (Ngram(copy_word_list(ngram), []), wordnums)


    def printable_pattern(self):
        r"""Return a printable printable of `self.pattern`.
        The pattern follows the syntax `@attr1,attr2,...,attrN@` where
           * @ = word separator (words are surrounded by these)
           * attrK = attribute K ("_" for undefined)
        """
        return self.pattern.replace(self.WORD_SEPARATOR, "@") \
                .replace(self.ATTRIBUTE_SEPARATOR, ",") \
                .replace("[^,@]*", "_")



def copy_word(w):
    return Word(w.surface, w.lemma, w.pos, w.syn, [])

# XXX Do we actually need to copy it?
# In this case isn't it better to use `copy.deepcopy()`?
def copy_word_list(ws):
    return map(copy_word, ws)



########################################


def patternlib_test():
    p = patternlib_make("""<pat repeat="+"> <w pos="N"/> </pat>""")  # pat: N+
    ws = [Word("the", "the", "Det", "x", []),
          Word("foos", "foo", "N", "x", []),
          Word("bars", "bar", "V", "x", []),
          Word("quuxes", "quux", "N", "x", []),
          Word("foose", "foo", "N", "x", []),
          Word("etiam", "etiam", "N", "x", [])]
    patternlib_do_test(p, ws)

    print("-" * 40)
    print("Generic pattern: size 2~3.")
    patternlib_do_test(build_generic_pattern(2,3), ws, "Longest")

    p = patternlib_make("""<w pos="N"/> 
            <pat repeat="+"> <w pos="N"/> </pat>""")  # pat: N N+
    ws = "animal liver cell line".split()
    ws = [Word(w, w, "N", "") for w in ws]
    patternlib_do_test(p, ws, "Shortest")
    patternlib_do_test(p, ws, "Longest")
    patternlib_do_test(p, ws, "All")

    print()
    patternlib_do_test(p, ws, "Shortest", False)
    patternlib_do_test(p, ws, "Longest", False)

    p = patternlib_make("""<w pos="V"/> 
            <pat repeat="*" ignore="true"> <w/> </pat>
            <w pos="P"/>""")  # pat: V (WORD*){ignore} P
    ws = "Verb1 Noun1 Noun2 Prt1 Adj1 Prt2".split()
    ws = [Word(w, w, w[0], "") for w in ws]
    patternlib_do_test(p, ws, "Shortest")
    patternlib_do_test(p, ws, "Longest")
    patternlib_do_test(p, ws, "All")


    p = patternlib_make("""<w pos="V"/> 
            <pat repeat="*"> <w pos="V" neg="pos"/> </pat>
            <w pos="P"/>""")  # pat: V WORD{lemma!="that}* P
    ws = "Verb1 Noun1 Noun2 Prt1 Adj1 Prt2 Verb3 Prt3".split()
    ws = [Word(w, w, w[0], "") for w in ws]
    patternlib_do_test(p, ws, "Longest")

    p = patternlib_make("""<w pos="V"/> 
            <pat repeat="*"> <neg><w pos="V"/></neg> </pat>
            <w pos="P"/>""")  # pat: V (!(WORD{lemma="that}))* P
    ws = "Verb1 Noun1 Noun2 Prt1 Adj1 Prt2 Verb3 Prt3".split()
    ws = [Word(w, w, w[0], "") for w in ws]
    patternlib_do_test(p, ws, "Longest")


def pretty_ngram(ngram):
    return " ".join(w.surface for w in ngram)

def patternlib_do_test(p, words, distance="All", overlapping=True):
    lls = p.matches(words, distance, overlapping)
    print("Match distance:", distance,
            ("(" if overlapping else "(non ") + "overlapping)")
    for ngram, pos in lls:
        print("  ", pretty_ngram(ngram), pos)

def patternlib_make(str_pattern):
    from StringIO import StringIO
    s = "<patterns><pat>{}</pat></patterns>".format(str_pattern)
    p = parse_patterns_file(StringIO(s))[0]
    print("-" * 40)
    print("XML pattern:", re.sub(r"\s+", " ", p.node.toxml()))
    print("Printable-pattern:", p.printable_pattern())
    return p


if __name__ == "__main__":
    patternlib_test()

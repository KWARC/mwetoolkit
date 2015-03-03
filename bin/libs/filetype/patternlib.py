#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# patternlib.py is part of mwetoolkit
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
    patternlib.py - Functions for manipulating complex ngram patterns.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from xml.etree import ElementTree
from ..base.word import Word, WORD_ATTRIBUTES
from ..base.ngram import Ngram
from ..base.__common import ATTRIBUTE_SEPARATOR, WORD_SEPARATOR
from .. import util
import re
import sys



def parse_patterns_file(path, anchored=False):
    raise Exception("DEPRECATED: Use `filetype.parse_entities` instead, anchoring with matches()")


########################################

def parse_pattern(node):
    """Generates a ParsedPattern object, with an internal
    precompiled regular expression following a pattern description.

    @param node: An `xml.etree.Element` from the patterns
    file representing a single pattern.
    """
    return ParsedPattern(node.source_line)._parse(node)


def match_pattern(pattern, words):
    """DEPRECATED: Call `pattern.matches(words)` directly instead.
    Returns an iterator over all matches of the pattern in the word list."""
    return pattern.matches(words)


def build_generic_pattern(min, max):
    """Returns a pattern matching any ngram of size min~max."""
    # TODO make this implementation less hack-ish
    p = ParsedPattern("???")
    p.pattern = p.WORD_SEPARATOR + "(?:[^%s]*" % p.WORD_SEPARATOR + \
              p.WORD_SEPARATOR + ")" + "{%d,%d}" % (min, max)
    p._post_parsing()
    return p


########################################

class ParsedPattern(object):
    # ATTRIBUTE_WILDCARD: Match .* inside an attribute.
    ATTRIBUTE_WILDCARD = "[^" + ATTRIBUTE_SEPARATOR + WORD_SEPARATOR + "]*"
    # WORD_FORMAT: Internal Regex format to match a word with its attributes.
    WORD_FORMAT = ATTRIBUTE_SEPARATOR.join("%("+s+")s" for s in (["wordnum"] + WORD_ATTRIBUTES))

    def __init__(self, source_line):
        self.source_line = source_line
        self.temp_id = 0
        self.defined_w_ids = []
        self.forepattern_ids = {}
        self.WORD_SEPARATOR = WORD_SEPARATOR

    def _parse(self, node):
        self.node = node
        self.pattern = self.WORD_SEPARATOR
        self._do_parse(node, None)
        self._post_parsing()
        return self

    def _post_parsing(self):
        self.compiled_pattern = re.compile(self.pattern)
        self._strid_to_numid = {"id_*": 0}
        self._strid_to_numid.update(self.compiled_pattern.groupindex)
        self.ignored_numids = set(numid for (strid, numid) in
                self.compiled_pattern.groupindex.items() if
                strid.startswith("ignore_"))

    def _do_parse(self, node, scope_repeat):
        if node.tag == ElementTree.Comment:
            pass  # We ignore it :p
        elif node.tag == "pat":
            self._parse_pat(node, scope_repeat)
        elif node.tag == "either":
            self._parse_either(node, scope_repeat)

        elif node.tag == "backpat": 
            id = node.get("id", "")
            self.pattern += "(?P=%s)" % id

        elif node.tag == "w":
            self._parse_w(node, scope_repeat)
        #elif node.tag == "backw":
            # Obsolete. Use "back:id.attribute" syntax instead.
        #    self._parse_backw(node)
        else:
            util.error("Invalid node name {name!r}", name=node.tag)


    def check_scope_repeat(self, scope_repeat, node):
        if scope_repeat is not None:
            util.error("Elem cannot have `id` or `ignore` under a `repeat`" \
                    " scope (line {line}, col {col}; `repeat` in line {line_super}," \
                    " col {col_super})", line=node.source_line,
                    col=node.source_col, line_super=scope_repeat.source_line,
                    col_super=scope_repeat.source_col)


    def _parse_pat(self, node, scope_repeat):
        id = node.get("id", "")
        repeat = node.get("repeat", "")
        ignore = node.get("ignore", "")
        anchor_start = node.get("anchor_start", "")
        anchor_end = node.get("anchor_end", "")

        if anchor_start:
            if self.pattern == self.WORD_SEPARATOR:
                self.pattern = "^" + self.WORD_SEPARATOR
            else:
                raise Exception("Pattern anchoring is currently only "
                                  "supported in non-nested <pat> elements.")

        if ignore:
            self.check_scope_repeat(scope_repeat, node)
            self.pattern += "(?P<ignore_%d>" % self.temp_id
            self.temp_id += 1

        if id:
            self.check_scope_repeat(scope_repeat, node)
            assert "_" not in id, id
            self.pattern += "(?P<id_%s>" % id
        if repeat:
            self.pattern += "(?:"

        if not scope_repeat and repeat != "":
            scope_repeat = node
        for subnode in node:
            self._do_parse(subnode, scope_repeat)

        if repeat:
            self.pattern += ")"
        if repeat:
            if repeat != "*" and repeat != "?" and repeat != "+" and \
                not re.match(r"^\{[0-9]*,[0-9]*\}|\{[0-9]+\}$",repeat ) :
                warningrepeat = "WARNING: invalid repeat pattern: " + repeat
                print(warningrepeat, file=sys.stderr)
            self.pattern += repeat

        if id:
            self.pattern += ")"

        if ignore:
            self.pattern += ")"

        if anchor_end:
            self.pattern += "$"


    def _parse_either(self, node, scope_repeat):
        id = node.get("id", "")
        repeat = node.get("repeat", "")

        if id:
            self.check_scope_repeat(scope_repeat, node)
            assert "_" not in id, id
            self.pattern += "(?P<id_{}>".format(id)
        else:
            self.pattern += "(?:"

        if not scope_repeat and repeat != "":
            scope_repeat = node

        first_pattern = True
        for subnode in node:
            if first_pattern:
                first_pattern = False
            else:
                self.pattern += "|"

            self._do_parse(subnode, scope_repeat)

        self.pattern += ")"
        if repeat:
            self.pattern += repeat


    def _neg_children(self, node, only_attr):
        for subnode in node:
            if subnode.tag != "neg":
                util.error("Elem <w> only accepts subelem <neg>; got " \
                        "<{bad_subelem}> (line {line})",
                        bad_subelem=subnode.tag, line=node.source_line)
            for attr,val in subnode.items():
                if attr == only_attr:
                    yield "(?!" + re.escape(val) + ")"

    def _parse_w(self, node, scope_repeat):
        valid_attrs = set(WORD_ATTRIBUTES + ["id", "neg", "syndep"])
        for attr, value in node.items():
            if attr not in valid_attrs:
                util.warn("Ignoring bad word attr (line {}): {!r}"
                        .format(node.source_line, attr))

        negated = set(node.get("neg", "").split(":"))
        attrs = { "wordnum": self.ATTRIBUTE_WILDCARD }
        id = node.get("id", "")
        for attr in WORD_ATTRIBUTES:
            val = node.get(attr, "")
            if val.startswith("back:"):
                (refid, refattr) = val.split(":")[1].split(".")
                val = "(?P=%s_%s)" % (refid, refattr)
            elif val:
                val = re.escape(val).replace("\\*", self.ATTRIBUTE_WILDCARD)
            else:
                val = self.ATTRIBUTE_WILDCARD

            # XXX DEPRECATED: remove this in the future (now we use <neg>)
            if attr in negated:
                if val != self.ATTRIBUTE_WILDCARD:
                    val = "(?!" + val + ")" + self.ATTRIBUTE_WILDCARD
                else :
                    raise Exception("You cannot negate an undefined "
                                     "attribute: " + attr + "\nIn: " +
                                     ElementTree.tostring(node))

            neg_val = "".join(self._neg_children(node, attr))
            attrs[attr] = neg_val + val

        
        if id:
            self.check_scope_repeat(scope_repeat, node)
            if id in self.forepattern_ids:
                attrs["wordnum"] = "(?P=%s)" % self.forepattern_ids[id]
            # 2015-02-24 silvioricardoc: commenting out, because this looks useless
            #for attr in attrs:
            #    attrs[attr] = "(?P<wid_%s_%s>%s)" % (id, attr, attrs[attr])
            if id in self.defined_w_ids:
                raise Exception("Id '%s' defined twice" % id)
            self.defined_w_ids.append(id)

        syndep = node.get("syndep", "")
        if syndep:
            (deptype, depref) = syndep.split(":")
            if depref in self.defined_w_ids:
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
                                ";%s:(?P<idsyn_%s>[0-9]*);" % (deptype, foredep) +
                                self.ATTRIBUTE_WILDCARD)

        w_pat = self.WORD_FORMAT % attrs + self.WORD_SEPARATOR
        if id:
            w_pat = "(?P<id_{}>{})".format(id, w_pat)
        self.pattern += w_pat


    #def _parse_backw(self, node):
    #    # Obsolete. Use "back:id.attribute" syntax instead.
    #    for attr in WORD_ATTRIBUTES:
    #        id = node.get(attr, "")
    #        if id:
    #            attrs[attr] = "(?P=%s_%s)" % (id, attr)
    #        else:
    #            attrs[attr] = self.ATTRIBUTE_WILDCARD
    #    self.pattern += self.WORD_FORMAT % attrs + self.WORD_SEPARATOR


    def matches(self, words, match_distance="All", overlapping=True,
                id_order=["*"], anchor_begin=False, anchor_end=False):
        """Returns an iterator over all matches of this pattern in the word list.
        Each iteration yields a pair `(ngram, match_indexes)`.
        """
        numid_order = [self.strid_to_numid(strid) for strid in id_order]
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
                    positions[i], len(wordstring), positions, numid_order,
                    anchor_end))

            increment = 1
            if match_distance == "All":
                if not overlapping:
                    raise Exception("All requires Overlapping")
                for m in matches_here:
                    yield m
            elif match_distance == "Longest":
                if matches_here:
                    yield matches_here[0]
                    if not overlapping:
                        increment = len(matches_here[0][0])
            elif match_distance == "Shortest":
                if matches_here:
                    yield matches_here[-1]
                    if not overlapping:
                        increment = len(matches_here[-1][0])
            else:
                raise Exception("Bad match_distance: " + match_distance)

            i += increment
            if anchor_begin: return


    def _matches_at(self, words, wordstring, current_start,
            limit, positions, numid_order, anchor_end):
        current_end = limit
        matches_here = []
        while True:
            result = self.compiled_pattern.match(wordstring, current_start - 1, current_end)
            if not result: return

            start = result.start()
            end = result.end()
            current_end = end - 1
            ngram = []
            wordnums = []

            n_groups = self.compiled_pattern.groups
            spans = [(numid, result.span(numid)) for numid in xrange(n_groups+1)]
            words_by_numid = [[] for _ in xrange(n_groups+1)]
            nums_by_numid = [[] for _ in xrange(n_groups+1)]

            def get_numid(pos):
                for numid, (beg, end) in reversed(spans):
                    if beg <= pos < end:
                        if numid in numid_order:
                            return numid
                        return 0
                assert False, "Not even in ID==0?!?!"

            for num, (pos, word) in enumerate(zip(positions, words)):
                if start <= pos < end:
                    numid = get_numid(pos)
                    if numid not in self.ignored_numids:
                        words_by_numid[numid].append(word)
                        nums_by_numid[numid].append(num)

            self.debug_id_order(words_by_numid)
            for numid in numid_order:
                ngram.extend(words_by_numid[numid])
                wordnums.extend(nums_by_numid[numid])

            yield (Ngram(copy_word_list(ngram), []), wordnums)
            if anchor_end: return


    def strid_to_numid(self, str_id):
        try:
            return self._strid_to_numid["id_" + str_id]
        except KeyError:
            util.warn_once('Pattern does not define id ' \
                    '"{str_id}" (line {linenum})', str_id=str_id,
                    linenum=self.source_line)
            return 0


    def debug_id_order(self, words_by_numid):
        r"""Generate a "{"-separated ngram output.
        Much easier to spot id_order bugs."""
        if util.debug_mode:
            for wbn in words_by_numid:
                if not wbn:
                    wbn.append(Word("", ""))
                wbn[0] = wbn[0].dup()
                wbn[-1] = wbn[-1].dup()
                wbn[0].lemma = "{" + wbn[0].lemma
                wbn[-1].lemma += "}"


    def printable_pattern(self):
        r"""Return a printable printable of `self.pattern`.
        The pattern follows the syntax `@attr1,attr2,...,attrN@` where
           * @ = word separator (words are surrounded by these)
           * attrK = attribute K ("_" for undefined)
        """
        return self.pattern.replace(self.WORD_SEPARATOR, "@") \
                .replace(ATTRIBUTE_SEPARATOR, ",") \
                .replace("[^,@]*", "_")



# XXX Do we actually need to copy it?
# In this case isn't it better to use `copy.deepcopy()`?
def copy_word_list(ws):
    return [w.dup() for w in ws]



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
            <pat repeat="*"> <w lemma="take" pos="V" neg="pos"/> </pat>
            <w pos="P"/>""")  # pat: V WORD{lemma!="that}* P
    ws = "Verb1 Noun1 Noun2 Prt1 Adj1 Prt2 Verb3 Prt3".split()
    ws = [Word(w, w, w[0], "") for w in ws]
    patternlib_do_test(p, ws, "Longest")

    p = patternlib_make("""<w pos="V"/> 
            <pat repeat="*"> <w lemma="take"><neg pos="V"/></w> </pat>
            <w pos="P"/>""")  # pat: V (!(WORD{lemma="that}))* P
    ws = "Verb1 Noun1 Noun2 Prt1 Adj1 Prt2 Verb3 Prt3".split()
    ws = [Word(w, w, w[0], "") for w in ws]
    patternlib_do_test(p, ws, "Longest")

    p = patternlib_make("""<w pos="V"/> 
            <pat repeat="*"> <w><neg pos="V"/><neg pos="N"/><neg lemma="that"/></w> </pat>
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
    print("XML pattern:", re.sub(r"\s+", " ", ElementTree.tostring(p.node)))
    print("Printable-pattern:", p.printable_pattern())
    return p


if __name__ == "__main__":
    patternlib_test()

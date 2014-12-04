#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_xml.py is part of mwetoolkit
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
This module provides classes to manipulate files that are
encoded in mwetoolkit's "XML" filetype.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import itertools
from xml.etree import ElementTree

from . import _common as common

from ..base.__common import XML_HEADER, XML_FOOTER
from ..base.__common import WILDCARD
from ..base.word import Word
from ..base.sentence import Sentence
from ..base.candidate import Candidate
from ..base.mweoccur import MWEOccurrence
from ..base.ngram import Ngram
from ..base.frequency import Frequency
from ..base.feature import Feature
from ..base.tpclass import TPClass
from ..base.meta import Meta
from ..base.corpus_size import CorpusSize
from ..base.meta_feat import MetaFeat
from ..base.meta_tpclass import MetaTPClass



################################################################################


class XMLInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for mwetoolkit's XML."""
    description = "An XML in mwetoolkit format (dtd/mwetoolkit-*.dtd)"
    filetype_ext = "XML"

    # TODO use escape_pairs here... how?
    escape_pairs = []

    def operations(self):
        return common.FiletypeOperations(XMLChecker, XMLParser, XMLPrinter)


INFO = XMLInfo()
r"""Singleton instance of XMLInfo."""



################################################################################

class XMLChecker(common.AbstractChecker):
    r"""Checks whether input is in XML format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(20)
        return header.startswith(b"<?xml") or header.startswith(b"<pattern")



################################################################################

class XMLPrinter(common.AbstractPrinter):
    """Instances can be used to print XML objects."""
    valid_roots = ["dict", "corpus", "candidates", "patterns"]

    def before_file(self, fileobj, info={}):
        self.add_string(XML_HEADER % {"root": self._root, "ns": ""}, "\n")

    def after_file(self, fileobj, info={}):
        self.add_string(XML_FOOTER % {"root": self._root} + "\n")

    def handle_comment(self, comment, info={}):
        self.add_string("<!-- ", self.escape(comment), " -->\n")

    def handle_meta(self, meta_obj, info={}):
        self.add_string(meta_obj.to_xml(), "\n")

    def fallback(self, entity, info={}):
        self.add_string(entity.to_xml(), "\n")



################################################################################

class XMLParser(common.AbstractParser):
    r"""Instances of this class parse the mwetoolkit XML format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["dict", "corpus", "candidates", "patterns"]

    def _parse_file(self, fileobj, handler):
        # Here, fileobj is raw bytes, not unicode, because ElementTree
        # complains if we feed it a pre-decoded stream in python2k
        outer_iterator = ElementTree.iterparse(fileobj, ["start", "end"])

        for event, elem in outer_iterator:
            inner_iterator = itertools.chain(
                    [(event, elem)], outer_iterator)

            if event == "end":
                raise Exception("Unexpected end-tag!")

            elif event == "start":
                info = {"parser": self, "root": elem.tag}

                if elem.tag == "dict":
                    # Delegate all the work to "dict" handler
                    with common.ParsingContext(fileobj, handler, info):
                        from .old.dictXMLHandler import DictXMLHandler
                        self._handle(inner_iterator, DictXMLHandler(
                                treat_meta=handler.handle_meta,
                                treat_entry=handler.handle_candidate))
                elif elem.tag == "corpus":
                    # Delegate all the work to "corpus" handler
                    with common.ParsingContext(fileobj, handler, info):
                        self.parse_corpus(inner_iterator, handler, info)

                elif elem.tag == "candidates":
                    # Delegate all the work to "candidates" handler
                    with common.ParsingContext(fileobj, handler, info):
                        self.parse_candidates(inner_iterator, handler, info)
                        #XXX from .old.candidatesXMLHandler import CandidatesXMLHandler
                        #XXX self._handle(inner_iterator, CandidatesXMLHandler(
                        #XXX         treat_meta=handler.handle_meta,
                        #XXX         treat_candidate=handler.handle_candidate))
                elif elem.tag == "patterns":
                    with common.ParsingContext(fileobj, handler, info):
                        # Delegate all the work to "patterns" handler
                        from .patternlib import iterparse_patterns
                        for pattern in iterparse_patterns(inner_iterator):
                            handler.handle_pattern(pattern)
                else:
                    raise Exception("Bad outer tag in XML filetype: " + repr(elem.tag))


    def _handle(self, iterator, xmlhandler):
        r"""Call startElement/endElement on handler for all sub-elements."""
        depth = 0
        for event, elem in iterator:
            if event == "start":
                xmlhandler.startElement(elem.tag, elem.attrib)
                depth += 1
            elif event == "end":
                xmlhandler.endElement(elem.tag)
                depth -= 1
                if depth == 0:
                    return
            elem.clear()


    #######################################################
    def parse_corpus(self, inner_iterator, handler, info):
        sentence = None
        s_id = -1

        for event, elem in inner_iterator:
            if event == "start":

                if elem.tag == "s" :
                    if "s_id" in elem.attrib:
                        s_id = int(self.unescape(elem.get("s_id")))
                    sentence = Sentence([], s_id)

                elif elem.tag == "w":
                    def get(name):
                        if name not in elem.attrib: return WILDCARD
                        return self.unescape(elem.get(name))

                    surface = get("surface")
                    lemma = get("lemma")
                    pos = get("pos")
                    syn = get("syn")
                    # Add word to the sentence that is currently being read
                    sentence.append(Word(surface, lemma, pos, syn, []))

                elif elem.tag == "mweoccur":
                    occur_cand = Candidate(int(elem.get("candid")))
                    new_occur = MWEOccurrence(sentence, occur_cand, [])
                    sentence.mweoccurs.append(new_occur)

                elif elem.tag == "mwepart":
                    sentence.mweoccurs[-1].indexes.append(int(elem.get("index"))-1)

            elif event == "end":
                if elem.tag == "s":
                    # A complete sentence was read, call the callback function
                    handler.handle_sentence(sentence)


    #######################################################
    def parse_candidates(self, inner_iterator, handler, info):
        id_number_counter = 0
        candidate = None
        ngram = None
        in_bigram = False
        in_occurs = False
        in_vars = False
        word = None
        meta = None

        for event, elem in inner_iterator:
            if event == "start":

                if elem.tag == "cand":
                    # Get the candidate ID or else create a new ID for it          
                    if "candid" in elem.attrib:
                        id_number = self.unescape(elem.get("candid"))
                    else:
                        id_number = id_number_counter
                        id_number_counter += 1
                    candidate = Candidate(id_number, None, [], [], [], [])

                elif elem.tag == "ngram":
                    ngram = Ngram([], [])

                elif elem.tag == "bigrams":
                    in_bigram = True
                elif elem.tag == "occurs" :
                    in_occurs = True
                elif elem.tag == "vars" :
                    in_vars = True

                elif elem.tag == "w":
                    # Instantiates a word. Missing attribute values are 
                    # assigned to a wildcard string, meaning "uninformed" for
                    # candidates or "any" for patterns
                    def get(name):
                        if name not in elem.attrib: return WILDCARD
                        return self.unescape(elem.get(name))

                    surface = get("surface")
                    lemma = get("lemma")
                    pos = get("pos")
                    syn = get("syn")
                    word = Word(surface, lemma, pos, WILDCARD, [])
                    # Add the word to the ngram that is on the stack
                    ngram.append(word)

                elif elem.tag == "freq":
                    self.freq = Frequency(self.unescape(elem.get("name")),
                            int(self.unescape(elem.get("value"))))
                    # If <freq> is inside a word element, then it's the word's
                    # frequency, otherwise it corresponds to the frequency of
                    # the ngram that is being read
                    if word is not None:
                        word.add_frequency( self.freq )            
                    else:
                        ngram.add_frequency( self.freq )

                elif elem.tag == "sources":
                    ngram.add_sources(elem.get("ids").split(';'))

                elif elem.tag == "feat":
                    feat_name = self.unescape(elem.get("name"))
                    feat_value = self.unescape(elem.get("value"))
                    feat_type = meta.get_feat_type( feat_name )
                    if feat_type == "integer":
                        feat_value = int(feat_value)
                    elif feat_type == "real":
                        feat_value = float(feat_value)                
                    f = Feature(feat_name, feat_value)
                    candidate.add_feat(f) 

                elif elem.tag == "tpclass" :
                    tp = TPClass(self.unescape(elem.get("name")), 
                                  self.unescape(elem.get("value")))
                    candidate.add_tpclass(tp)
                    
                # Meta section and elements, correspond to meta-info about the
                # candidates lists. Meta-info are important for generating
                # features and converting to arff files, and must correspond
                # to the info in the candidates (e.g. meta-feature has the 
                # same elem.tag as actual feature)      
                elif elem.tag == "meta":
                    self.meta = Meta([], [], [])
                elif elem.tag == "corpussize":
                    cs = CorpusSize(elem.get("name"), elem.get("value"))
                    meta.add_corpus_size(cs)
                elif elem.tag == "metafeat" :      
                    mf = MetaFeat(elem.get("name"), elem.get("type"))
                    meta.add_meta_feat(mf)  
                elif elem.tag == "metatpclass" :    
                    mtp = MetaTPClass(elem.get("name", elem.get("type")))
                    meta.add_meta_tpclass(mtp)


            elif event == "end":

                if elem.tag == "cand" :
                    # Finished reading the candidate, call callback
                    handler.handle_candidate(candidate, info) 

                elif elem.tag == "ngram":
                    if in_occurs:
                        candidate.add_occur(ngram)
                    elif in_bigram:
                        candidate.add_bigram(ngram)
                    elif in_vars:
                        candidate.add_var(ngram)
                    else:
                        candidate.word_list = ngram.word_list
                        candidate.freqs = ngram.freqs

                elif elem.tag == "w":
                    # Set word to none, otherwise I cannot make the difference between
                    # the frequency of a word and the frequency of a whole ngram
                    word = None        

                elif elem.tag == "meta":
                    # Finished reading the meta header, call callback        
                    handler.handle_meta(meta, info)

                elif elem.tag == "bigram":
                    in_bigram = False
                elif elem.tag == "occurs":
                    in_occurs = False
                elif elem.tag == "vars":
                    in_vars = False

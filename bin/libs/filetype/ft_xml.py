#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
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

from ..base.__common import WILDCARD
from ..base.word import Word
from ..base.sentence import SentenceFactory
from ..base.candidate import Candidate, CandidateFactory
from ..base.entry import Entry
from ..base.mweoccur import MWEOccurrence
from ..base.ngram import Ngram
from ..base.frequency import Frequency
from ..base.feature import Feature
from ..base.tpclass import TPClass
from ..base.meta import Meta
from ..base.corpus_size import CorpusSize
from ..base.meta_feat import MetaFeat
from ..base.meta_tpclass import MetaTPClass
from .. import util



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
        header = self.fileobj.peek(30)
        if header.startswith(b"\xef\xbb\xbf"):
            header = header[3:]  # remove utf8's BOM
        return header.startswith(b"<?xml") \
                or header.startswith(b"<pattern") \
                or header.startswith(b"<!--")



################################################################################

XML_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE {category} SYSTEM "dtd/mwetoolkit-{category}.dtd">
<!-- MWETOOLKIT: filetype="XML" -->
<{category} {ns}>"""

XML_FOOTER = """</{category}>"""


class XMLPrinter(common.AbstractPrinter):
    """Instances can be used to print XML objects."""
    valid_categories = ["dict", "corpus", "candidates", "patterns"]

    def __init__(self, *args, **kwargs):
        super(XMLPrinter, self).__init__(*args, **kwargs)
        self.add_string(XML_HEADER.format(category=self._category, ns=""), "\n")
        self._printed_filetype_directive = True

    def finish(self, info={}):
        self.add_string(XML_FOOTER.format(category=self._category), "\n")
        self.flush()

    def handle_comment(self, comment, info={}):
        self.add_string("<!-- ", self.escape(comment), " -->\n")

    def handle_pattern(self, pattern, info={}):
        # TODO Currently copying node XML from input. This should change in the future...
        self.add_string(ElementTree.tostring(pattern.node))

    def _fallback(self, entity, info={}):
        if type(entity) != common.Directive :
            self.add_string(entity.to_xml(), "\n")
        else:
            self.handle_comment(str(entity))



################################################################################

class XMLParser(common.AbstractParser):
    r"""Instances of this class parse the mwetoolkit XML format,
    calling the `handler` for each object that is parsed.
    """
    valid_categories = ["dict", "corpus", "candidates", "patterns"]


    def _parse_file(self, fileobj):
        # Here, fileobj is raw bytes, not unicode, because ElementTree
        # complains if we feed it a pre-decoded stream in python2k
        parser = CommentHandlingParser()
        if not fileobj.peek(10).startswith(b"<?xml"):
            if b"\n<?xml" in fileobj.peek(1000):
                # Python's XMLParser is unable to handle this, so we just give up
                util.error("XML tag <?xml> cannot appear after first line!")
            util.warn("XML file should start with <?xml> tag!")

        categ_finder_iter = ElementTree.iterparse(
                fileobj, ["start", "end"], parser)
        already_seen = []

        for event, elem in categ_finder_iter:
            if event == "start":
                already_seen.append((event,elem))
                if elem.tag != ElementTree.Comment:
                    if elem.tag == "dict":
                        delegate = self.parse_dict
                    elif elem.tag == "corpus":
                        delegate = self.parse_corpus
                    elif elem.tag == "candidates":
                        delegate = self.parse_candidates
                    elif elem.tag == "patterns":
                        delegate = self.parse_patterns
                    else:
                        util.error("Bad top-level XML elem (line {}): {!r}" \
                                .format(elem.source_line, elem.tag))

                    info = {"parser": self, "fileobj": fileobj, "category": elem.tag}
                    with common.ParsingContext(fileobj, self.handler, info):
                        it = itertools.chain(already_seen, categ_finder_iter)
                        delegate(it, info)



    def unknown_end_elem(self, elem, info):
        r"""Complain about unknown XML element."""
        if elem.tag == ElementTree.Comment:
            self.handler.handle_comment(elem.text.strip(), info)
        else:
            util.warn("Ignoring unknown XML elem (at line {}): {!r}" \
                    .format(elem.source_line, elem.tag))


    #######################################################
    def parse_corpus(self, inner_iterator, info):
        sentence_factory = SentenceFactory()
        sentence = None

        for event, elem in inner_iterator:
            info["linenum"] = elem.source_line
            if event == "start":
                if elem.tag == "s" :
                    s_id = None
                    if "s_id" in elem.attrib:
                        s_id = int(self.unescape(elem.get("s_id")))
                    sentence = sentence_factory.make(id_number=s_id)

                elif elem.tag == "mweoccur":
                    occur_cand = Candidate(int(elem.get("candid")))
                    new_occur = MWEOccurrence(sentence, occur_cand, [])
                    sentence.mweoccurs.append(new_occur)

            elif event == "end":
                if elem.tag == "s":
                    # A complete sentence was read, call the callback function
                    info["fileobj"] = self.input.fileobj
                    info["progress"] = self.input.current_progress()
                    self.handler.handle_sentence(sentence, info)

                elif elem.tag == "w":
                    def get(name):
                        if name not in elem.attrib: return WILDCARD
                        return self.unescape(elem.get(name))

                    surface = get("surface")
                    lemma = get("lemma")
                    pos = get("pos")
                    syn = get("syn")
                    # Add word to the sentence that is currently being read
                    sentence.append(Word(surface, lemma, pos, syn))

                elif elem.tag == "mweoccurs":
                    pass  # This tag is just a wrapper around `mweoccur` tags
                elif elem.tag == "mweoccur":
                    pass  # Already created MWEOccurrence on `start` event

                elif elem.tag == "mwepart":
                    sentence.mweoccurs[-1].indexes.append(int(elem.get("index"))-1)

                elif elem.tag == "corpus":
                    return  # Finished processing
                else:
                    self.unknown_end_elem(elem, info)
                elem.clear()



    #######################################################
    def parse_patterns(self, inner_iterator, info):
        # TODO: move code from ParsedPattern to here and build to build an
        # internal Pattern object (independent from XML)
        from . import patternlib
        depth = 0
        for event, elem in inner_iterator:
            info["linenum"] = elem.source_line
            if elem.tag == ElementTree.Comment:
                if event == "start":
                    self.handler.handle_comment(elem.text.strip(), info)
                continue   # (Does not generate an "end" systematically ¬¬)

            assert depth >= 0, "Not seeing `start` events?"
            if event == "start":
                depth += 1
            elif event == "end":
                depth -= 1
                if depth == 1:
                    # Just closed an element
                    if elem.tag == "pat":
                        self.handler.handle_pattern(patternlib.parse_pattern(elem))
                    else:
                        self.unknown_end_elem(elem, info)
                    elem.clear()
                elif depth == 0:
                    # Just closed </patterns>
                    return


    #######################################################
    def parse_candidates(self, inner_iterator, info):
        candidate_factory = CandidateFactory()
        candidate = None
        ngram = None
        in_bigram = False
        in_occurs = False
        in_vars = False
        word = None
        meta = None

        for event, elem in inner_iterator:
            info["linenum"] = elem.source_line
            if event == "start":

                if elem.tag == "cand":
                    # Get the candidate ID or else create a new ID for it          
                    id_number = None
                    if "candid" in elem.attrib:
                        id_number = self.unescape(elem.get("candid"))
                    candidate = candidate_factory.make([], id_number=id_number)

                elif elem.tag == "ngram":
                    ngram = Ngram()

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
                    word = Word(surface, lemma, pos, syn)
                    # Add the word to the ngram that is on the stack
                    ngram.append(word)

                # Meta section and elements, correspond to meta-info about the
                # candidates lists. Meta-info are important for generating
                # features and converting to arff files, and must correspond
                # to the info in the candidates (e.g. meta-feature has the 
                # same elem.tag as actual feature)      
                elif elem.tag == "meta":
                    meta = Meta(None, None, None)


            elif event == "end":

                if elem.tag == "cand" :
                    # Finished reading the candidate, call callback
                    self.handler.handle_candidate(candidate, info) 

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
                    self.handler.handle_meta(meta, info)

                elif elem.tag == "bigrams":
                    in_bigram = False
                elif elem.tag == "occurs":
                    in_occurs = False
                elif elem.tag == "vars":
                    in_vars = False


                elif elem.tag == "freq":
                    freq = Frequency(self.unescape(elem.get("name")),
                            int(self.unescape(elem.get("value"))))
                    # If <freq> is inside a word element, then it's the word's
                    # frequency, otherwise it corresponds to the frequency of
                    # the ngram that is being read
                    if word is not None:
                        word.add_frequency(freq)            
                    else:
                        ngram.add_frequency(freq)

                elif elem.tag == "sources":
                    ngram.add_sources(elem.get("ids").split(';'))

                elif elem.tag == "feat":
                    feat_name = self.unescape(elem.get("name"))
                    feat_value = self.unescape(elem.get("value"))
                    feat_type = meta.get_feat_type(feat_name)
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
                    
                elif elem.tag == "corpussize":
                    cs = CorpusSize(elem.get("name"), elem.get("value"))
                    meta.add_corpus_size(cs)
                elif elem.tag == "metafeat" :      
                    mf = MetaFeat(elem.get("name"), elem.get("type"))
                    meta.add_meta_feat(mf)  
                elif elem.tag == "metatpclass" :    
                    mtp = MetaTPClass(elem.get("name"), elem.get("type"))
                    meta.add_meta_tpclass(mtp)
                elif elem.tag == "features":
                    pass # nothing to do, but don't WARNING user
                elif elem.tag == "candidates":
                    return  # Finished processing
                else:
                    self.unknown_end_elem(elem, info)
                elem.clear()


    #######################################################
    def parse_dict(self, inner_iterator, info):
        id_number_counter = 1
        entry = None
        word = None
        meta = None

        for event, elem in inner_iterator:
            info["linenum"] = elem.source_line

            if event == "start":

                if elem.tag == "entry":
                    # Get the candidate ID or else create a new ID for it
                    if "entryid" in elem.attrib:
                        id_number_counter = self.unescape(elem.get("entryid"))
                    # Instantiates an empty dict entry that will be treated
                    # when the <entry> tag is closed
                    entry = Entry(id_number_counter)
                    id_number_counter += 1

                elif elem.tag == "w":
                    def get(name):
                        if name not in elem.attrib: return WILDCARD
                        return self.unescape(elem.get(name))

                    surface = get("surface")
                    lemma = get("lemma")
                    pos = get("pos")
                    syn = get("syn")
                    word = Word(surface, lemma, pos, syn)
                    entry.append(word)

                # Meta section and elements, correspond to meta-info about the
                # reference lists. Meta-info are important for generating
                # features and converting to arff files, and must correspond
                # to the info in the dictionary (e.g. meta-feature has the
                # same name as actual feature)
                elif elem.tag == "meta":
                    meta = Meta(None,None,None)

            if event == "end":

                if elem.tag == "entry":
                    self.handler.handle_candidate(entry)
                    entry = None
                elif elem.tag == "w":
                    word = None
                elif elem.tag == "meta":
                    # Finished reading the meta header, call callback 
                    self.handler.handle_meta(meta)

                elif elem.tag == "freq":
                    freq = Frequency(self.unescape(elem.get("name")),
                            int(self.unescape(elem.get("value"))))
                    # If <freq> is inside a word element, then it's the word's
                    # frequency, otherwise it corresponds to the frequency of
                    # the ngram that is being read
                    if word is not None:
                        word.add_frequency(freq)
                    else:
                        entry.add_frequency(freq)

                elif elem.tag == "feat":
                    feat_name = self.unescape(elem.get("name"))
                    feat_value = self.unescape(elem.get("value"))
                    feat_type = meta.get_feat_type(feat_name)
                    if feat_type == "integer":
                        feat_value = int(feat_value)
                    elif feat_type == "real":
                        feat_value = float(feat_value)
                    f = Feature(feat_name, feat_value)
                    entry.add_feat(f)

                elif elem.tag == "corpussize":
                    cs = CorpusSize(elem.get("name"), elem.get("value"))
                    meta.add_corpus_size(cs)
                elif elem.tag == "metafeat" :      
                    mf = MetaFeat(elem.get("name"), elem.get("type"))
                    meta.add_meta_feat(mf)  

                elif elem.tag == "dict":
                    return  # Finished processing
                else:
                    self.unknown_end_elem(elem, info)



class CommentHandlingParser(ElementTree.XMLParser):
    r"""Force XMLParser to handle XML comments and generate source_{line,col}."""
    def __init__(self, **kwargs):
        super(CommentHandlingParser, self).__init__(self, **kwargs)
        self._parser.CommentHandler = self.handle_comment
        self._names[ElementTree.Comment] = ElementTree.Comment

    def handle_comment(self, data):
        self.parser.StartElementHandler(ElementTree.Comment, {})
        self.target.data(data)
        self.parser.EndElementHandler(ElementTree.Comment)

    def _start_list(self, *args, **kwargs):
        element = super(self.__class__, self)._start_list(*args, **kwargs)
        element.source_line = self._parser.CurrentLineNumber
        element.source_col = self._parser.CurrentColumnNumber + 1
        return element

#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_ucs.py is part of mwetoolkit
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
This module provides classes to manipulate files that are encoded in the
"UCS" data set format. Since UCS works only with pairs (2-grams),
all ngrams with sizes other than 2 are discarded.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from ..base.__common import WILDCARD
from .. import util

################################################################################


class UCSInfo(common.FiletypeInfo):
    description = "UCS 2-gram filetype format"
    filetype_ext = "UCS"

    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("/", "${slash}"), (" ", "${space}"),
            ("\t", "${tab}"), ("\n", "${newline}"), ("#", "${hash}")]

    def operations(self):
        return common.FiletypeOperations(None, None, UCSPrinter)


INFO = UCSInfo()
r"""Singleton instance of UCSInfo."""


class UCSPrinter(common.AbstractPrinter):
    filetype_info = INFO
    valid_categories = ["candidates"]

    def __init__(self, category, freq_source=None, lemmapos=False, surface_instead_lemmas=False, **kwargs):
        super(UCSPrinter, self).__init__(category)
        self.freq_source = freq_source
        self.lemmapos = lemmapos
        self.surface_instead_lemmas = surface_instead_lemmas


    def handle_meta(self, meta, info={}):
        """Print the header for the UCS dataset file,
        and save the corpus size."""
        string_cand = "id\tl1\tl2\tf\tf1\tf2\tN"

        #for cs in meta.corpus_sizes :
        #    string_cand = string_cand + cs.name + "\t"
        #string_cand = string_cand + "occurs\tsources\t"

        #for cs in meta.meta_tpclasses :
        #    string_cand = string_cand + cs.name + "\t"
        #for cs in meta.meta_feats :
        #    string_cand = string_cand + cs.name + "\t"  
        xml_meta = meta
        self.corpus_size = self.freq_value(xml_meta.corpus_sizes)
        self.add_string(string_cand, "\n")
       

    def handle_candidate(self, entity, info={}):
        """Print each `Candidate` as a UCS data set entry line.
        @param entity: The `Candidate` that is being read from the XML file.
        """
        string_cand = ""
        if entity.id_number >= 0 :
            string_cand += unicode( entity.id_number )
        string_cand = string_cand.strip() + "\t"    
        
        if len(entity) != 2:
            util.warn("Ignoring entity %s, of length %d!=2" % (entity.id_number, len(entity)))
            return

        for w in entity :
            if self.lemmapos :
                string_cand += self.escape(w.lemma) + "/" + self.escape(w.pos) + "\t"
            elif w.lemma != WILDCARD and not self.surface_instead_lemmas :
                string_cand += w.lemma + "\t"
            else :
                string_cand += w.surface + "\t"
        string_cand += "%f\t" % self.freq_value(entity.freqs)

        try:
            for w in entity:
                string_cand += "%f\t" % self.freq_value(w.freqs)
        except:
            string_cand += "0\t"
            util.warn("Word frequency information missing for"\
                        " entity %d" % entity.id_number)
        string_cand += unicode(self.corpus_size)
        self.add_string(string_cand, "\n")


    def freq_value(self, items):
        """Given a list of items with a `name` and a `value` attribute, return
        the item whose name is the same as that of `freq_source`.
        """
        for item in items:
            if self.freq_source is None or item.name == self.freq_source:
                return item.value

        util.warn("Frequency source '%s' not found!" % self.freq_source)
        return 0


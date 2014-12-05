#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_csv.py is part of mwetoolkit
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
"CSV" filetype, which is useful when exporting data to Office spreadsheet and
related formats

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common

################################################################################


class CSVInfo(common.FiletypeInfo):
    description = "Tab-separated CSV filetype format, one field per column"
    filetype_ext = "CSV"
    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("\t", "${tab}"), ("/", "${slash}"),
                    (" ", "${space}"), (";", "${semicolon}")]

    def operations(self):
        return common.FiletypeOperations(None, None, CSVPrinter)

INFO = CSVInfo()

class CSVPrinter(common.AbstractPrinter):
    filetype_info = INFO
    valid_roots = ["candidates", "corpus"]

    def __init__(self, root, sep="\t", surfaces=False, lemmapos=False, **kwargs):
        super(CSVPrinter, self).__init__(root, **kwargs)
        self.sep = sep
        self.surfaces = surfaces
        self.lemmapos = lemmapos

    def handle_meta(self, meta, info={}):
        """When the `Meta` header is read, this function generates a
        corresponding header for the CSV file. The header includes name of the
        fields, including fixed elements like the candidate n-gram and POS
        sequence, as well as variable elements like TPClasses and feature names

        @param meta: The `Meta` header that is being read from the file.
        @param info: Any extra information as a dictionary
        """
        headers = ["id", "ngram", "pos"]
        headers.extend(self.escape(cs.name) for cs in meta.corpus_sizes)
        headers.append("occurs", "sources")
        headers.extend(self.escape(cs.name) for cs in meta.tpclasses)
        headers.extend(self.escape(cs.name) for cs in meta.meta_feats)
        self.add_string(self.sep.join(headers), "\n")

    def handle_candidate(self, entity, info={}):
        """
            For each `Candidate`,

            @param entity: The `Candidate` that is being read from the XML file.
        """
        values = [str(entity.id_number)]
        ngram_list = map(lambda x: self.escape("%s/%s" % (x.lemma, x.pos))
                                if self.lemmapos else
                                self.escape(x.surface)
                                if self.surfaces or common.WILDCARD == x.lemma
                                else self.escape(x.lemma),
                         entity)
        values.append(" ".join(ngram_list))
        values.append("" if self.lemmapos else " ".join(map(lambda x: x.pos, entity)))
        if getattr(entity,"freqs"):
            values.extend(str(freq.value) for freq in entity.freqs)
        if getattr(entity,"tpclasses"):
            values.extend(str(tpclass.value) for tpclass in entity.tpclasses)
        if getattr(entity,"occurs"):
            values.append(";".join(map(lambda x:" ".join(
                          w.surface for w in x.occur), entity.occurs)))
            values.append(";".join(map(lambda x:x.source,entity.occurs)))
        if getattr(entity,"features"):
            values.extend(str(feat.value) for feat in entity.features)

        self.add_string(self.sep.join(values), "\n")


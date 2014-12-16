#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_arff.py is part of mwetoolkit
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
"ARFF" filetype, which is used by the WEKA machine learning toolkit.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common


################################################################################


class ArffInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for ARFF files."""
    description = "ARFF file type, as defined by the WEKA toolkit"
    filetype_ext = "ARFF"

    comment_prefix = "%"

    def operations(self):
        return common.FiletypeOperations(ArffChecker, None, ArffPrinter)


INFO = ArffInfo()
r"""Singleton instance of ArffInfo."""



class ArffChecker(common.AbstractChecker):
    r"""Checks whether input is in ARFF format."""
    filetype_info = INFO
    def matches_header(self, strict):
        return not strict



class ArffPrinter(common.AbstractPrinter):
    filetype_info = INFO
    valid_categories = ["corpus"]

    def __init__(self, category, relation_name="MWETOOLKIT_RELATION", **kwargs):
        super(ArffPrinter, self).__init__(category, **kwargs)
        self.relation_name = relation_name
        self.all_feats = []

    def handle_meta(self, meta, info={}):
        """When the `Meta` header is read, this function generates a
        corresponding header for the ARFF file. The header includes the name of
        the relation and a description of the attributes. This description is
        based on the `MetaFeat' and `MetaTPClass` entries of the header. If you
        provided invalid types for the features or the TP base, the generated
        ARFF file will not be recognized by WEKA. If necessary, correct it
        manually.
        
        @param meta The `Meta` header that is being read from the file.
        """
        self.add_string("@relation {}\n".format(self.relation_name))
        for meta_feat in meta.meta_feats:
            self.add_string("@attribute {} {}\n".format(
                    meta_feat.name, meta_feat.value))
            # features that will be considered in each candidate
            self.all_feats.append(meta_feat.name)
        for meta_tpclass in meta.meta_tpclasses:
            self.add_string("@attribute {} {}\n".format(
                    meta_tpclass.name, meta_tpclass.value))
        self.add_string("@data\n")


    def handle_candidate(self, candidate, info={}):
        """For each `Candidate`, print a comma-separated line with its feature 
        values as described by the meta-features in the header. If a feature has
        no meta-feature header, it will be ignored. If a feature has an 
        associated meta-feature header but no feature value, it will be
        considered as a missing value "?" in the ARFF file. The True Positive
        base are also considered as features in this context and are printed
        after the standard features of the candidate.
        
        @param candidate The `Candidate` that is being read from the XML file.
        """
        line = []
        for feat_name in self.all_feats:
            feat_value = candidate.get_feat_value(feat_name)
            if type(feat_value) == float:
                feat_value = "{:.8f}".format(feat_value)
            else:
                feat_value = unicode(feat_value)
            line.append(feat_value)
        line.extend(tpc.value for tpc in candidate.tpclasses)
        self.add_string(",".join(line), "\n")

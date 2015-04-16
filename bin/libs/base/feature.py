#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# feature.py is part of mwetoolkit
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
    This module provides the `Feature` class. This class represents a feature of
    the candidate, i.e. a pair attribute-value that describes it.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import collections
from xml.sax.saxutils import quoteattr


################################################################################

class Feature(object) :
    """A MWE candidate feature is a pair name-value that describes a specific
    aspect of the candidate, such as a measure, a linguistic property, a
    count, etc.
    """

################################################################################

    def __init__( self, name, value, xml_class="feat" ) :
        """Instantiates a new `Feature`, which is a general name
        for a pair attribute-value. A feature aims at the description of one
        aspect of the candidate, and is supposed to be an abstraction that
        allows a machine learning algorithm to create generalizations from
        instances.

        @param xml_class String that identifies what kind of feature
        this is.  Subclasses MUST use a unique name.

        @param name String that identifies the `Feature`.
        
        @param value The value of the feature. A value is not typed, it can
        be an integer, a real number, a string or an element of an 
        enumeration (allowed types in WEKA).
        
        @return A new instance of `Feature`.
        """
        assert xml_class in ("feat", "freq", "tpclass", "corpussize"), xml_class
        self.xml_class = xml_class
        self.name = name
        self.value = value

################################################################################

    def __repr__(self):
        return "{}({}, {}, xml_class={})".format(
                self.__class__.__name__, self.name, self.value, self.xml_class)
        
################################################################################

    def copy( self ) :
        r"""Return a copy of this Feature."""
        return self.__class__(self.name, self.value)

################################################################################

    def add_from(self, other):
        r"""Add the value in "other" to "self."""
        self.value += other.value
        
################################################################################

    def __eq__( self, a_feat ) :
        """
            TODO: doc
        """
        return self.name == a_feat.name and self.value == a_feat.value

################################################################################

    def to_xml( self ) :
        """
            (We may deprecate `Feature` objects in the future, in favor
            of namedtuple('featname value'), so let's already disable this
            method)

            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <feat> with its
            attributes, according to mwetoolkit-candidates.dtd.
        """
        raise Exception("DEPRECATED")
        ret = []
        self._to_xml_into(ret)
        return "".join(ret)

    def _to_xml_into( self, output, indent=0 ) :
        output.append(" "*indent)
        output.extend(("<", self.xml_class, " name="))
        output.append(quoteattr(self.name))
        output.append(" value=")
        output.append(quoteattr(unicode(self.value)))
        output.append(" />")


################################################################################



class FeatureSet(object):
    r"""Instances represent groups of features in the form (name, value).
    
    Since two features with the same name may be added, the `merge_op`
    function is used to merge them into a single value.
    If the merge function depends on the featname, use `featname2merge_op`.
    """
    def __init__(self, xml_class, merge_op=None, featname2merge_op=None):
        assert xml_class in ("feat", "freq", "tpclass", "corpussize"), xml_class
        assert merge_op or featname2merge_op
        self._xml_class = xml_class
        self._merge_op = merge_op
        self._featname2merge_op = featname2merge_op
        self._dict = collections.OrderedDict()

    def copy(self):
        r"""Return a copy of this FeatureSet."""
        ret = FeatureSet(self._xml_class,
                self._merge_op, self._featname2merge_op)
        ret.merge_from(self)
        return ret

    def clear(self):
        r"""Remove all features from this FeatureSet."""
        self._dict.clear()

    def __len__(self):
        r"""Return the number of elements in this FeatureSet instance."""
        return len(self._dict)

    def __contains__(self, key):
        r"""Return whether a feature with given key is in this FeatureSet."""
        return key in self._dict

    def __iter__(self):
        for featname, value in self._dict.iteritems():
            yield Feature(featname, value, self._xml_class)

    def get_feature(self, key, default):
        r"""Given a key, return a feature in the form (key, value)."""
        return Feature(key, self._dict.get(key, default), self._xml_class)

    def add(self, featname, new_value):
        r"""Add (featname, value) pair to this FeatureSet."""
        assert new_value is not None
        try:
            old_value = self._dict[featname]
        except KeyError:
            self._dict[featname] = new_value
        else:
            self._dict[featname] = self._merge(featname, old_value, new_value)

    def _merge(self, featname, value1, value2):
        if self._featname2merge_op:
            return self._featname2merge_op(featname)(value1, value2)
        else:
            return self._merge_op(value1, value2)

    def merge_from(self, other):
        r"""Merge another FeatureSet into self, looking for the appropriate
        MetaFeat to understand how the feature should be merged."""
        for key, value in other._dict.iteritems():
            self.add(key, value)

    def to_xml(self):
        """Provides an XML string representation
        of the features inside the current object.
        """
        ret = []
        self._to_xml_into(ret)
        return "".join(ret)

    def _to_xml_into( self, output, indent=0, after_each="" ) :
        for featname, value in self._dict.iteritems() :
            Feature(featname, value, self._xml_class) \
                    ._to_xml_into(output, indent)
            output.append(after_each)


################################################################################


if __name__ == "__main__" :
    import doctest
    doctest.testmod()

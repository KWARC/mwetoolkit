#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# WordPattern.py is part of mwetoolkit
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

from ComponentPattern import *

# List of valid word attributes.
# Must appear in the same order as the arguments for the Word class constructor.
WORD_ATTRIBUTES = ['surface', 'lemma', 'pos', 'syndep']

class WordPattern(ComponentPattern):
	'''docstring for WordPattern'''
	def __init__(self, id, positive = {}, negative = {}):
		'''Create a WordPattern object.

		Keyword arguments:
		positive -- description (default {})
		negative -- description (default {})
		'''
		ComponentPattern.__init__(self)
		self.id = id
		self.positive = positive
		self.negative = negative

	def add_attribute(self, name, value, negated = False):
		'''Add an attribute to a word pattern.

		Keyword arguments:
		name -- The name of the attribute
		value -- The value of the attribute
		negated -- Whether negated or not (default False)
		'''
		if name in WORD_ATTRIBUTES:
			if negated:
				if name not in self.negative:
					self.negative[name] = []
				self.negative[name].append(value)
			else:
				if name not in self.positive:
					self.positive[name] = []
				self.positive[name].append(value)

	def to_xml(self):		
		'''Format the word pattern into XML.'''
		return '<w />'
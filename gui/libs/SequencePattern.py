#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# SequencePattern.py is part of mwetoolkit
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

from CompositePattern import *

class SequencePattern(CompositePattern):
	'''docstring for SequencePattern'''
	def __init__(self, id, repeat = None, ignore = False):
		'''Create a SequencePattern object.

		Keyword arguments:
		id -- description
		repeat -- description (default None)
		ignore -- description (default False)
		'''
		CompositePattern.__init__(self)
		self.id = id
		self.repeat = repeat
		self.ignore = ignore

	def to_xml(self):		
		'''Format the sequence pattern into XML.'''
		xml = ''
		xml += '<pat>'
		for component in self.components:
			xml += component.to_xml()
		xml += '</pat>'
		return xml
#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# XMLFormatter.py is part of mwetoolkit
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

from EitherPattern import *
from SequencePattern import *
from WordPattern import *
from Formatter import *

class XMLFormatter(Formatter):
	'''docstring for XMLFormatter'''
	def __init__(self):
		'''Create a XMLFormatter object.'''
		Formatter.__init__(self)

	def visit(self, pattern):
		if isinstance(pattern, WordPattern):
			if pattern.negative == {}:
				self.content += '<w'
			else:
				self.content += '<w'

			if pattern.id is not None:
				self.content += ' id="%s"' %pattern.id

			# For now, the positive dictionary can't have multiple values for the same attribute
			# So, the first element of the list is taken
			for key in pattern.positive:
				self.content +=  ' %s="%s"' %(key, pattern.positive[key][0])

			if pattern.negative != {}:
				self.content += '>'
				# Create a negation tag for each value
				for key in pattern.negative:
					for value in pattern.negative[key]:
						self.content += '<neg'
						self.content +=  ' %s="%s"' %(key, value)
						self.content += ' />'
				self.content += '</w>'
			else:
				self.content += ' />'
		elif isinstance(pattern, SequencePattern):
			self.content += '<pat'

			if pattern.repeat is not None:
				self.content += ' repeat="%s"' %pattern.repeat

			if pattern.ignore:
				self.content += ' ignore="true"'

			self.content += '>'

			# Loop through its children
			for component in pattern.components:
				component.accept(self)

			self.content += '</pat>'
		elif isinstance(pattern, EitherPattern):
			self.content += '<either>'

			# Loop through its children
			for component in pattern.components:
				component.accept(self)

			self.content += '</either>'
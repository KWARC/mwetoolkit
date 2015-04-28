#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# Patterns.py is part of mwetoolkit
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

class Patterns():
	'''docstring for Patterns'''
	def __init__(self):
		self.components = []

	def add(self, component):
		'''Add a component to the list of components.

		Keyword arguments:
		component -- The component to add
		'''
		self.components.append(component)

	def remove(self, component):
		'''Remove a component from the list of components.

		Keyword arguments:
		component -- The component to remove
		'''
		self.components.remove(component)

	def accept(self, formatter):
		'''Format the patterns.

		Keyword arguments:
		formatter -- A Formatter object
		'''
		formatter.content = '<?xml version="1.0" encoding="UTF-8"?>'
		formatter.content += '<patterns>'
		for component in self.components:
			component.accept(formatter)
		formatter.content += '</patterns>'

	def to_xml(self):
		'''Format the patterns into XML.'''
		xml = '<?xml version="1.0" encoding="UTF-8"?>'
		xml += '<patterns>'
		for component in self.components:
			xml += component.to_xml()
		xml += '</patterns>'
		return xml
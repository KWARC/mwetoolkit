#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# filetypes/compress.py is part of mwetoolkit
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
This module provides fileobj wrappers that automatically
uncompress the underlying fileobjs.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import


from . import _common
import zipfile
import gzip
import bz2



################################################################################

class ZipWrapper(_common.Python2kFileWrapper):
    r"""Wrapper to transparently read zip-compressed files."""
    def __init__(self, fileobj):
        # XXX We need to create an in-memory seek-able file
        # object, because apparently Zip stores some important
        # info at the end of the file... o.O
        import io
        io_contents = io.BytesIO(fileobj.read())
        self._full_wrapped = zipfile.ZipFile(io_contents)
        if len(self._full_wrapped.NameToInfo) != 1:
            from .. import util
            util.error("Input zip-file has more than 1 entry")
        only_name = list(self._full_wrapped.NameToInfo.values())[0]
        wrapped = self._full_wrapped.open(only_name)
        super(ZipWrapper, self).__init__(wrapped)



class Bz2Wrapper(bz2.BZ2File):
    r"""Wrapper to transparently read bz2-compressed files."""
    def __init__(self, fileobj):
        # XXX Does not work before Python 3.3, because nobody
        # thought anyone would ever want to uncompress from a
        # file stream -- that's a very advanced concept, folks! ¬¬
        super(Bz2Wrapper, self).__init__(fileobj=fileobj)



class GzipWrapper(gzip.GzipFile):
    r"""Wrapper to transparently read gzip-compressed files."""
    def __init__(self, fileobj):
        # XXX Load the whole file in memory, because I've just
        # spent a couple of hours of my life looking for a way to
        # pass an io.BufferedReader as argument, but in Python2k
        # it just throws the exception:
        #   TypeError: 'NoneType' object cannot be interpreted as an index
        # with a traceback that starts when `io.BufferedReader.seek` is being
        # called (it doesn't show the actual offending line that tries to acces
        # a None). This is probably a bug in the internal implementation of
        # io.BufferedReader, but right now I don't care about it.
        #
        # TODO check if we need this hack at all in Python3k.
        # (Besides, in Python3k we may not need to explicitly instantiate
        # BufferedReader for e.g. sys.stdin, which is our current headache).
        import io; 
        io_contents = io.BytesIO(fileobj.read())
        super(GzipWrapper, self).__init__(fileobj=io_contents)

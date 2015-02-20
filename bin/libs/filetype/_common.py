#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# filetypes/_common.py is part of mwetoolkit
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
This module provides common classes and abstract base classes
that can be used when implementing a new filetype parser/printer.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import io
import collections
import itertools
import os
import re
import sys

from ..base.__common import WILDCARD
from ..base.candidate import Candidate
from ..base.sentence import Sentence
from ..base.word import Word
from ..base.meta import Meta
from .. import util



################################################################################
####################   Filetype Info   #########################################
################################################################################


class FiletypeInfo(object):
    r"""Instances of this class represent a filetype.

    Subclasses must define the attributes:
    -- `description`
    -- `filetype_ext`
    -- `comment_prefix`  (unless `handle_comment` is overridden).
    Subclasses must also override the method `operations`.

    If the associated Parser/Printer will call `escape`/`unescape`,
    the attribute `escape_pairs` must also be defined.
    """
    @property
    def description(self):
        """A small string describing this filetype."""
        raise NotImplementedError

    def operations(self):
        r"""Return an instance of FiletypeOperations."""
        raise NotImplementedError

    @property
    def filetype_ext(self):
        """A string with the extension for this filetype.
        Also used as a filetype hint."""
        raise NotImplementedError

    @property
    def comment_prefix(self):
        """String that precedes a commentary for this filetype."""
        raise NotImplementedError

    @property
    def escape_pairs(self):
        """List of pairs with (unescaped, escaped) `unicode` instances.
        The first entry MUST be the pair for the escaping character itself."""
        raise NotImplementedError

    def matches_filetype(self, filetype_hint):
        r"""Return whether the binary contents
        of `header` matches this filetype."""
        return self.filetype_ext == filetype_hint

    @property
    def checker_class(self):
        """A subclass of AbstractChecker for this filetype.
        (Exactly equivalent to calling `self.operations().checker_class`)."""
        return self.operations().checker_class

    @property
    def parser_class(self):
        """A subclass of AbstractParser for this filetype.
        (Exactly equivalent to calling `self.operations().parser_class`)."""
        return self.operations().parser_class

    @property
    def printer_class(self):
        """A subclass of AbstractPrinter for this filetype.
        (Exactly equivalent to calling `self.operations().printer_class`)."""
        return self.operations().printer_class


class FiletypeOperations(collections.namedtuple("FiletypeOperations",
        "checker_class parser_class printer_class")):
    r"""A named triple (checker_class, parser_class, printer_class):
    -- checker_class: A subclass of AbstractChecker.
    -- parser_class: Either None or a subclass of AbstractParser.
    -- printer_class: Either None or a subclass of AbstractPrinter.
    """
    pass




################################################################################
####################   Filetype Checking   #####################################
################################################################################


class AbstractChecker(object):
    r"""Instances of this class can be used to peek at a file object
    and test whether its header matches a given filetype.
    
    Constructor Arguments:
    @param fileobj: The file object to be peeked.

    Attributes:
    @param filetype_info: Instance of FiletypeInfo
    that corresponds to the underlying filetype.
    """
    filetype_info = None

    def __init__(self, fileobj):
        self.fileobj = fileobj

    def matches_header(self, strict):
        r"""Return whether the header of `self.fileobj`
        could be interpreted as an instance of this filetype.

        If `strict` is True, perform stricter checks and
        only return True if the header is *known* to be in
        the format of this filetype (usually, one should use
        strict=True when detecting filetypes and strict=False
        when checking for bad matches."""
        raise NotImplementedError

    def check(self):
        r"""Check if `self.fileobj` belongs to this filetype
        and raise an exception if it does not."""
        if not self.matches_header(strict=False):
            raise Exception("Bad \"{}\" input".format(
                self.filetype_info.filetype_ext))



################################################################################
####################   File parsing   ##########################################
################################################################################


class StopParsing(Exception):
    """Raised to warn the parser that it should stop parsing the current file.
    Conceptually similar to StopIteration.
    """
    pass


class FileList(object):
    r"""A FileList represents a list of files to be read.

    IMPORTANT: The `starting_positions` list should have an extra
    last element indicating the size of it all."""
    def __init__(self, list_of_files, starting_positions):
        assert isinstance(list_of_files, list), list_of_files
        self._list = list_of_files
        self.starting_positions = starting_positions

    def sublists(self):
        r"""Yield a FileList instance for each file."""
        size = self.starting_positions[-1]
        for f, cl in zip(self._list, self.starting_positions):
            yield FileList([f], [cl, size])

    def only(self):
        r"""Return the only file in this FileList.
        If the list has more than one file, raise an error."""
        if len(self._list) != 1:
            raise Exception("BUG: Expected 1 file, got " + self._list)
        return self._list[0]

    @staticmethod
    def make_from(list_of_files):
        r"""Return a FileList for given list_of_files."""
        if isinstance(list_of_files, FileList):
            return list_of_files

        list_of_files = list_of_files or ["-"]
        files = [FileList._open_file(f) for f in list_of_files]

        starting_positions = [0]
        for f in files:
            last = starting_positions[-1]
            starting_positions.append(last + os.fstat(f.fileno()).st_size)
        return FileList(files, starting_positions)

    @staticmethod
    def _open_file(path):
        r"""(Return buffered file object for given path)"""
        if isinstance(path, io.BufferedReader):
            return path
        if path == "-":
            path = sys.stdin
        if isinstance(path, basestring):
            path = open(path, "rb")
        f = Python2kFileWrapper(path)
        return io.BufferedReader(f)


class AbstractParser(object):
    r"""Base class for file parsing objects.

    Subclasses should override `_parse_file`,
    calling the appropriate `handler` methods.

    Constructor Arguments:
    @param input_files: A list of target file paths,
    or an instance of FileList.
    """
    filetype_info = None
    valid_categories = []

    def __init__(self, input_files):
        self.filelist = FileList.make_from(input_files)
        self.partial_fun = None
        self.partial_obj = None
        self.partial_kwargs = None
        self._meta_handled = False

    def flush_partial_callback(self):
        r"""Finally perform the callback `self.partial_fun(...args...)`."""
        if self.partial_fun is not None:
            self.partial_fun(self.partial_obj, **self.partial_kwargs)
        self.partial_fun = self.partial_obj = self.partial_kwargs = None

    def new_partial(self, new_partial_fun, obj, **kwargs):
        r"""Add future callback `partial_fun(...args...)`."""
        self.flush_partial_callback()
        self.partial_fun = new_partial_fun
        self.partial_obj = obj
        self.partial_kwargs = kwargs


    def parse(self, handler):
        r"""Parse all files with this parser.

        @param handler: An instance of InputHandler.
        Callback methods will be called on `handler`.
        """
        for f in self.filelist._list:
            try:
                self._parse_file(f, handler)
            except StopParsing:  # Reading only part of file
                pass  # Just interrupt parsing
        self.close()
        return handler


    def _parse_comment(self, handler, comment, info):
        r"""Parse contents of comment string and chain to 
        `handler.handle_{directive,comment}` accordingly.
        """
        comment = comment.strip()
        directive = Directive.from_string(comment)
        if directive:
            handler.handle_directive(directive, info)
        else:
            handler.handle_comment(comment)


    def unescape(self, string):
        r"""Return an unescaped version of `string`, using
        `self.filetype_info.escape_pairs` and whatever else is needed."""
        # The escaper character must be the last to be unescaped
        # Example: in XML, you should replace &amp; by & as the last operation,
        # otherwise the sequence &amp;quot; will be wrongly unescaped as simple
        # quote " instead of &quot;
        for unescaped, escaped in reversed(self.filetype_info.escape_pairs):
            string = string.replace(escaped, unescaped)
        return string


    def _parse_file(self, fileobj, handler):
        r"""(Called to parse file `fileobj`)"""
        raise NotImplementedError


    def close(self):
        r"""Close all files opened by this parser."""
        for f in self.filelist._list:
            if hasattr(f, "close"):
                if f != sys.stdin:  # XXX 2014-11-07 broken by Python2kFileWrapper
                    f.close()
        self.filelist = FileList([], [0])
    
################################################################################

class AbstractTxtParser(AbstractParser):
    r"""Base class for plaintext-file parsing objects.
    (For example, CONLL parsers, Moses parsers...)

    Subclasses should override `_parse_line`,
    calling the appropriate `handler` methods.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    @param encoding: The encoding to use when reading files.
    """
    def __init__(self, input_files, encoding):
        super(AbstractTxtParser, self).__init__(input_files)
        cp = re.escape(self.filetype_info.comment_prefix)
        self.comment_pattern = re.compile("^ *" + cp + " *(?P<contents>.*?) $")
        self.encoding = encoding
        self.encoding_errors = "replace"
        self.category = "<unknown-category>"

    def _parse_file(self, fileobj, handler):
        info = {"parser": self, "category": self.category}
        with ParsingContext(fileobj, handler, info):
            if self.category == "<unknown-category>":
                raise Exception("Subclass should have set `self.category`")
            just_saw_a_comment = False

            for i, line in enumerate(fileobj):
                line = line.rstrip()
                line = line.decode(self.encoding, self.encoding_errors)
                cp = self.filetype_info.comment_prefix

                if line.startswith(cp):
                    comment = line[len(cp):]
                    self._parse_comment(handler, comment, {})
                    just_saw_a_comment = True

                elif line == "" and just_saw_a_comment:
                    self._parse_comment(handler, "", {})
                    just_saw_a_comment = False

                else:
                    progr = (self.filelist.starting_positions[0] + fileobj.tell(),
                            self.filelist.starting_positions[-1])
                    self._parse_line(line, handler, {"fileobj": fileobj,
                            "linenum": i+1, "progress": progr})
                    just_saw_a_comment = False

    def _parse_line(self, line, handler, info={}):
        r"""Called to parse a line of the TXT file.
        Not called for comments and SOMETIMES not called
        for empty lines.

        Subclasses may override."""
        raise NotImplementedError


class ParsingContext(object):
    r"""(Call `handler.{before,after}_file`.)"""
    def __init__(self, fileobj, handler, info):
        self.fileobj, self.handler, self.info = fileobj, handler, info

    def __enter__(self):
        self.handler.before_file(self.fileobj, self.info)
    
    def __exit__(self, t, v, tb):
        if v is None:
            # If StopParsing was raised, we don't want
            # to append even more stuff in the output
            # (Especially since that would re-raise StopParsing
            # from inside __exit__, which will make a mess)
            self.info["parser"].flush_partial_callback()

        if v is None or isinstance(v, StopParsing):
            self.handler.after_file(self.fileobj, self.info)


class Python2kFileWrapper(object):
    r"""Wrapper to make Python2k stdin/stdout
    behave as in Python3k.  When wrapping io.BytesIO,
    this will also fix Python Issue 1539381."""
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def __getattr__(self, name):
        r"""Behave like the underlying file."""
        return getattr(self._wrapped, name)

    def readable(self):
        r"""(Override required by `sys.stdin`)."""
        try:
            return self._wrapped.readable()
        except AttributeError:
            return True  # Very deeply though-out code...

    def readinto(self, b):
        r"""(Override required by `io.StringIO`)."""
        try:
            return self._wrapped.readinto(b)
        except AttributeError:
            b[:] = self._wrapped.read(len(b))
            
    def tell(self):
        try:
            return self._wrapped.tell()
        except IOError:
            return 0
 



################################################################################
####################   Input Handlers   ########################################
################################################################################


class InputHandler(object):
    r"""Handler interface with callback methods that
    are called by the parser during its execution."""

    def flush(self):
        r"""May be called to flush outputs."""
        pass  # By default, do nothing

    def before_file(self, fileobj, info={}):
        r"""Called before parsing file contents."""
        pass  # By default, do nothing

    def after_file(self, fileobj, info={}):
        r"""Called after parsing file contents."""
        self.flush()  # By default, just flush whatever is in

    def handle_sentence(self, sentence, info={}):
        r"""Called to treat a Sentence object."""
        info["kind"] = "sentence"
        return self._fallback_entity(sentence, info)

    def handle_candidate(self, candidate, info={}):
        r"""Called to treat a Candidate object."""
        info["kind"] = "candidate"
        return self._fallback_entity(candidate, info)

    def handle_pattern(self, pattern, info={}):
        r"""Called to treat a ParsedPattern object."""
        info["kind"] = "pattern"
        return self._fallback_entity(pattern, info)

    def handle_meta(self, meta_obj, info={}):
        r"""Called to treat a Meta object."""
        info["kind"] = "meta"
        return self._fallback(meta_obj, info)

    def handle_comment(self, comment, info={}):
        r"""Called when parsing a comment."""
        info.setdefault("kind", "comment")
        return self._fallback(comment, info)

    def handle_directive(self, directive, info={}):
        r"""Default implementation when seeing a directive."""
        if directive.key == "filetype":
            # We don't care about the input filetype directive,
            # as we will generate an output filetype directive regardless.
            #self.handle_comment("[Converted from " + directive.value + "]")
            pass
        else:
            util.warn_once("Unknown directive: " + directive.key)


    def handle(self, obj, info):
        r"""Alternative to calling `self.handle_{kind}` methods.
        Useful as a catch-all when delegating from another InputHandler."""
        kind = info["kind"]
        return getattr(self, "handle_"+kind)(obj, info=info)

    def _fallback_entity(self, entity, info={}):
        r"""Called to treat a generic entity (sentence/candidate/pattern)."""
        self._fallback(entity, info)

    def _fallback(self, obj, info):
        r"""Called to handle anything that hasn't been handled explicitly."""
        if info["kind"] == "meta" and obj.is_dummy():
            return  # We don't want to complain about dummy metas
        util.warn("Ignoring " + info["kind"])


    def make_printer(self, info, forced_filetype_ext):
        r"""Create and return a printer.
        In the case of ChainedInputHandler's, the returned printer
        should be assigned to `self.chain`.

        The printer is created based on either
        the value of `forced_filetype_ext` or info["parser"],
        and uses the category from info["category"].
        """
        from .. import filetype
        ext = forced_filetype_ext \
                or info["parser"].filetype_info.filetype_ext
        return filetype.printer_class(ext)(info["category"])

################################################################################

class ChainedInputHandler(InputHandler):
    r"""InputHandler that delegates all methods to `self.chain`.
    """
    chain = None

    def flush(self):
        self.chain.flush()

    def before_file(self, fileobj, info={}):
        self.chain.before_file(fileobj, info)

    def after_file(self, fileobj, info={}):
        self.chain.after_file(fileobj, info)
        self.flush()

    def handle_directive(self, directive, info={}):
        info.setdefault("kind", "directive")
        return self._fallback(directive, info)

    def _fallback(self, entity, info={}):
        self.chain.handle(entity, info)




################################################################################
####################   File Printers ###########################################
################################################################################


class AbstractPrinter(InputHandler):
    r"""Base implementation of a printer-style class.

    Required Constructor Arguments:
    @param category The category of the output file. This value
    must be in the subclass's `valid_categories

    Optional Constructor Arguments:
    @param output An IO-like object, such as sys.stdout
    or an instance of StringIO.
    @param flush_on_add If True, calls `self.flush()` automatically
    inside `self.add_string()`, before actually adding the element(s).
    """
    valid_categories = []

    @property
    def filetype_info(self):
        r"""The singleton instance of FiletypeInfo
        for this printer's file type. Must be overridden."""
        raise NotImplementedError
    
    def __init__(self, category, output=None, flush_on_add=True):
        if category not in self.valid_categories:
            raise Exception("Bad printer: {}(category=\"{}\")"
                    .format(type(self).__name__, category))
        self._printed_filetype_directive = False
        self._category = category
        self._output = output or sys.stdout
        self._flush_on_add = flush_on_add
        self._waiting_objects = []
        self._scope = 0

    def before_file(self, fileobj, info={}):
        r"""Begin processing by printing filetype."""
        if not self._printed_filetype_directive:
            directive = Directive("filetype",
                    self.filetype_info.filetype_ext)
            self.handle_comment(unicode(directive), info)
            self._printed_filetype_directive = True

    def after_file(self, fileobj, info={}):
        r"""Flush outputs after execution."""
        self.flush()


    def add_string(self, *strings):
        r"""Queue strings to be printed."""
        if self._flush_on_add:
            self.flush()
        for string in strings:
            bytestring = string.encode('utf-8')
            self._waiting_objects.append(bytestring)
        return self  # enable call chaining

    def escape(self, string):
        r"""Return an escaped version of `unicode`, using
        `self.filetype_info.escape_pairs` and whatever else is needed."""
        # NEVER change the order in which you go through the list. The first
        # character to escape must always be the escaper itself.
        for unescaped, escaped in self.filetype_info.escape_pairs:
            string = string.replace(unescaped, escaped)
        return string

    def last(self):
        r"""Return last (non-flushed) added object."""
        return self._waiting_objects[-1]

    def flush(self):
        r"""Eagerly print the current contents."""
        for obj in self._waiting_objects:
            self._write(obj)
        del self._waiting_objects[:]
        return self  # enable call chaining

    def _write(self, bytestring, end=""):
        r"""(Print bytestring in self._output)"""
        assert isinstance(bytestring, bytes)
        self._output.write(bytestring)

    def handle_comment(self, comment, info={}):
        r"""Default implementation to output comment."""
        for c in comment.split("\n"):
            if c == "":
                self.add_string("\n")
            else:
                self.add_string(self.filetype_info.comment_prefix + " " + c + "\n")



################################################################################
####################   Other classes   #########################################
################################################################################

class Directive(object):
    RE_PATTERN = m = re.compile(
            r' *MWETOOLKIT: *(\w+)="(.*?)" *$', re.MULTILINE)
    def __init__(self, key, value):
        self.key, self.value = key, value
        assert not "\"" in value

    def __str__(self):
        return "MWETOOLKIT: {}=\"{}\"".format(self.key, self.value)

    @staticmethod
    def from_string(string, on_error=lambda: None):
        r"""Return an instance of Directive or None."""
        m = Directive.RE_PATTERN.match(string)
        if m is None: return None
        return Directive(*m.groups())

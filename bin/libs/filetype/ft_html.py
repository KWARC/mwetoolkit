#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_html.py is part of mwetoolkit
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
"HTML" filetype, which is a useful output corpus format.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from .. import util


class HTMLInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for HTML format."""
    description = "Pretty HTML for in-browser visualization"
    filetype_ext = "HTML"

    # TODO use python-based HTML escape
    escape_pairs = []

    def operations(self):
        return common.FiletypeOperations(HTMLChecker, None, HTMLPrinter)


class HTMLChecker(common.AbstractChecker):
    r"""Checks whether input is in HTML format."""
    def matches_header(self, strict):
        return not strict
        #header = self.fileobj.peek(1024)
        #return b"<html>" in header


class HTMLPrinter(common.AbstractPrinter):
    """Instances can be used to print HTML format."""
    valid_categories = ["corpus"]

    def before_file(self, fileobj, info={}):
        html_header="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>MWETOOLKIT annotated corpus: {corpusname}</title>
    <!--<link rel="stylesheet" href="mwetk-corpus.css" type="text/css" media="screen"/>-->
    <style>
    h1{{margin:0}}
    p.notice{{font-family:Arial;font-size:10pt;margin:0}}
    hr{{margin:10px 0}}
    p.sent{{margin:2px 100px 2px 0;line-height:145%%;padding:4px 2px}}
    p.sent:hover{{background-color:#FFC}}
    p.sent span.sid{{border:1px solid #000;border-radius:2px;padding:1px 5px}}
    p.sent:hover span.sid{{background:#F22;color:#FFF}}
    p.sent:hover a.word{{border-color:#03A}}
    span.mwepart a.word{{border:2px solid #000}}
    span.mwe1 a.word{{background-color:#F66}}
    span.mwe2 a.word{{background-color:#9C0}}
    span.mwe3 a.word{{background-color:#69F}}
    span.mwe4 a.word{{background-color:#F90}}
    a.word{{position:relative;border:1px solid #CCF;border-radius:2px;padding:1px 2px;margin:auto 0;font-family:Verdana sans-serif;text-decoration:none;color:#000}}
    a.word:hover{{background-color:#03A;border-color:#000;color:#FFF}}
    a.word span.surface{{font-weight:700}}
    a.word span.wid{{font-size:70%%;position:relative;top:.3em;font-style:italic;padding-left:3px}}
    a.word span.lps{{color:#000;padding:2px 5px;top:1em;z-index:1;height:auto;opacity:0;position:absolute;visibility:hidden;background-color:#AAA;border:1px solid #000;border-radius:2px;box-shadow:#000 2px 2px 6px}}
    a.word:hover span.lps{{opacity:.95;visibility:visible}}
    a.word span.lps span.lemma{{font-style:italic;display:block}}
    a.word span.lps span.pos{{font-weight:700;display:block}}
    a.word span.lps span.syn{{font-weight:400;display:block;font-family:Arial}}
    </style>
</head>
<body>
<h1>Corpus: {corpusname}</h1>
<p class="notice">Generated automatically by the <a href="http://mwetoolkit.sf.net/" target="_blank">mwetoolkit</a> </p>
<p class="notice"> Timestamp: {timestamp}</p>
<p class="notice">Source: <tt>{filename}</tt></p>
<hr/>"""
        s = fileobj.name
        import os, datetime
        # XXX escape these parameters

        timestamp = datetime.datetime.now()
        if util.deterministic_mode:
            timestamp = "[MWETOOLKIT_DETERMINISTIC_MODE]"

        self.add_string(html_header.format(timestamp=timestamp,
                corpusname=s[s.rfind("/")+1:],
                filename=os.path.abspath(s)))


    def after_file(self, fileobj, info={}):
        self.add_string("</body>\n</html>")
        self.flush()

    def escape(self, text):
        return text  # XXX use a python native html escaper

    def handle_comment(self, comment, info={}):
        self.add_string("<!-- ", self.escape(comment), " -->\n")

    def handle_sentence(self, sentence, info={}):
        self.add_string(sentence.to_html(), "\n")


#! /usr/bin/env python

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

__all__ = [
    "parser", "Main"
]

import argparse
import os
import json
import re
import sys
from textwrap import dedent

FILE_ENC = "UTF-8"
HERE = os.path.dirname(os.path.realpath(__file__))


RE_PARAGRAPH = re.compile(r"(\n *)+\n(?! )")

COMMANDS = {}

def make_command(func):
    COMMANDS[func.__name__] = func
    return func


def print_dict(obj):
    json.dump(obj, sys.stdout, sort_keys=True, indent=3)
    print()


###########################################################


def get_usage(toolname):
    r"""Run `toolname` with `-h` and return output."""
    assert toolname != "c-indexer", "TODO: add -h to c-indexer"
    from subprocess import Popen, PIPE
    # XXX make this escape-friendly...
    p = Popen("./" + toolname + " -h",
            shell=True, stderr=PIPE, stdout=PIPE)
    return "".join(p.communicate())

def usage_paragraphs(text):
    r"""Split text and return a list of paragraphs."""
    p = RE_PARAGRAPH.split(text)
    p = [line.strip() for line in p]
    return [line for line in p if line]


############################################################

@make_command
def list_tools():
    r"""List all tools in the toolkit."""
    output = []
    for fname in os.listdir("."):
        if os.path.isfile(fname) and os.stat(fname).st_mode & os.X_OK:
            output.append(fname)
    print_dict({"toolnames": output})


############################################################

@make_command
def tool_args(toolname):
    r"""List arguments for a tool."""
    ToolArgsParser().parse(usage_paragraphs(get_usage(toolname)))


class ToolArgsParser(object):
    def __init__(self):
        # doing_required: whether we're still handling the
        # `required` section of the help message
        self.doing_required = True

        # Required section (first part) of the help message
        self.required = []
        # Map flag_name -> JSON_obj  (to be further updated)
        self.req_flags = {}
        # Map argument -> JSON_obj  (to be further updated)
        self.req_arguments = {}

        # Optional section (second part) of the help message
        self.optional = []


    def parse(self, paragraphs):
        r"""Parse list of paragraphs and return JSON object."""
        for paragraph in paragraphs:
            self.current_p = paragraph
            if self.doing_required:
                if paragraph.startswith("Usage:"):
                    continue
                if paragraph.startswith("OPTIONS may"):
                    self.doing_required = False
                    continue
                if self.try_header():
                    continue
                if paragraph.startswith("-"):
                    arg = self.parse_paragraph_arg(paragraph)
                    self.update_req_flags(arg)
                    continue
                if self.try_input_human():
                    continue
                self.required.append({"unknown": paragraph})
            else:
                if paragraph.startswith("-"):
                    arg = self.parse_paragraph_arg(paragraph)
                    self.optional.append(arg)
                    continue
                self.optional.append({"unknown": paragraph})

        print_dict({"required": self.required,
                "optional": self.optional})


    def update_req_flags(self, arg):
        r"""Update `self.req_flags` with `arg`."""
        try:
            self.req_flags[arg["flag"]].update(arg)
        except KeyError:
            self.req_flags[arg["miniflag"]].update(arg)



    RE_HEADER = re.compile(r"python (?P<progpath>\S+) " \
            "(?P<mandatory1>.*?) ?\[?OPTIONS\]? (?P<mandatory2>.*)")

    def try_header(self):
        r"""Interpret command header, as in `self.RE_HEADER`."""
        m = self.RE_HEADER.match(self.current_p)
        if not m: return False
        self.required.extend(self.parse_args(m.group("mandatory1")))
        self.required.extend(self.parse_args(m.group("mandatory2")))
        return True



    RE_INPUT_HUMAN = re.compile(r"The (?P<inputname><\S+>).* must be.*")

    def try_input_human(self):
        r"""Interpret paragraph "The BLABLA must be..."."""
        m = self.RE_INPUT_HUMAN.match(self.current_p)
        if not m: return False
        self.req_arguments[m.group("inputname")]["human_descr"] = m.string
        return True



    RE_PARAGRAPH_HEADER_ARG = re.compile(
            "((?P<miniflag>-\S+)(?P<miniflag_arg> <\S+>)? (OR|or) )?" \
            "(?P<flag>--?\S+)(?P<flag_arg> <\S+>)?")

    def parse_paragraph_arg(self, paragraph):
        r"""Interpret paragraph starting with: "-f <arg> OR --flag <arg>"."""
        head, tail = paragraph.split("\n", 1)
        head = head.strip()  # Remove trailing spaces (so common...)
        m = self.RE_PARAGRAPH_HEADER_ARG.match(head)
        if m.end() != len(head):
            print("WARNING: Bad flag in tool:", head, file=sys.stderr)
        D = m.groupdict()
        ret = {"flag": D["flag"], "flag_arguments":
                self.parse_args(D["flag_arg"] or "")}
        if D["miniflag"]: ret["miniflag"] = D["miniflag"]
        ret["human_descr"] = dedent(tail)
        extract_from_human(ret)
        return ret



    RE_HEADER_ARG = re.compile(
            r"\[(?P<choice>.*?)\]" \
            "|(?P<flag>--?\S+?)(?P<flag_arg> <\S+?>(:<\S+?>)*)?" \
            "|(?P<argument_name><\S+?>(:<\S+?>)*)" \
            "|(?P<unknown>\S+?)")


    def parse_args(self, arg_string):
        r"""Parse a line such as: "[--flag <arg> | -g] --another-flag"."""
        ret = []
        for arg in self.RE_HEADER_ARG.finditer(arg_string):
            D = arg.groupdict()
            if D["choice"]:
                ret.append({"choice": [self.parse_args(a)[0]
                        for a in D["choice"].split("|")]})

            elif D["flag"]:
                ret.append({"flag": D["flag"], "flag_arguments":
                        self.parse_args(D["flag_arg"] or "")})

                if self.doing_required:
                    self.req_flags[D["flag"]] = ret[-1]

            elif D["argument_name"]:
                a = D["argument_name"]
                descr = argument_description(a)
                ret.append({"argument_name": a, "description": descr})

                if self.doing_required:
                    self.req_arguments[a] = ret[-1]

            else:
                ret.append({"unknown_arg": D["unknown"]})
        return ret



def argument_description(argument):
    r"""Parse an argument such as "<pattern-list>" or "<min>"."""
    if ">:<" in argument:
        a, b = argument.split(":", 1)
        return {"argument_type": "range", "components":
                [argument_description(a) for a in argument.split(":")],
                "separator": ":"}
    elif "pattern" in argument:
        return {"argument_type": "file", "category": "patterns"}
    elif "corpus" in argument:
        return {"argument_type": "file", "category": "corpus"}
    elif "candidate" in argument:
        return {"argument_type": "file", "category": "candidates"}
    elif "dict" in argument:
        return {"argument_type": "file", "category": "dict"}
    elif "min" in argument or "max" in argument:
        return {"argument_type": "int", "argument_name": argument}
    else:
        return {"argument_type": "unknown"}



RE_HUMAN_CHOICE = re.compile('^\* "([^"]*)"', re.MULTILINE)

def extract_from_human(arg):
    r"""Read `human_descr` field of `arg` and improve
    its data if finding descriptions of choice, such as
    the choice "Foo" in: '* "Foo": Bar bar baz'.
    """
    human = arg["human_descr"]
    if arg.get("flag_arguments", None):
        D = arg["flag_arguments"][0]["description"]
        if D["argument_type"] == "unknown":
            choice_strings = RE_HUMAN_CHOICE.findall(human)
            if choice_strings:
                D["argument_type"] = "choice_string"
                D["choice_strings"] = RE_HUMAN_CHOICE.findall(human)


###########################################################

parser = argparse.ArgumentParser(add_help=False, description="""
        Output information about the tools in the MWETOOLKIT.

        This information is captured by running each tool with
        the `-h` flag and parsing the output.

        This data can be used e.g. by graphical interfaces, when
        presenting the functionality of the toolkit in a higher-level
        user interface.  Each command-line option described in a tool's
        output is represented as a sub-object in the JSON output.
        """)
parser.add_argument("-h", "--help", action="help",
        help=argparse.SUPPRESS)
parser.add_argument("COMMAND", choices=tuple(COMMANDS.keys()),
        help="""Run this command (choices: {choices})""".format(
            choices=",".join(COMMANDS.keys())))
parser.add_argument("ARGS", nargs='*',
        help="""Pass on these arguments to `COMMAND`""")


class Main(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        os.chdir(os.environ.get("MWETOOLKIT", HERE+"/../bin"))
        COMMANDS[self.args.COMMAND](*self.args.ARGS)


#####################################################

if __name__ == "__main__":
    Main(parser.parse_args()).run()

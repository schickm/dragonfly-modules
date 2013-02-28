#
# This file is a command-module for Dragonfly.
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#

"""
Command-module for **Chrome** editor
=======================================

This module offers various commands for Chrome
, as well as integration with the Vimium plugin
to allow clicking of links via Telephony character names.

"""


#---------------------------------------------------------------------------

from dragonfly import (Grammar, AppContext, MappingRule,
                       Dictation, Choice, IntegerRef, NumberRef,
                       Key, Text, Repeat, Repetition, Alternative,
                       RuleRef, CompoundRule)

import os, sys
sys.path.append(os.path.dirname(__file__))
from shared_rules import ScrollRule
#---------------------------------------------------------------------------
# Create the main command rule.

class TelephonyRule(MappingRule):
    exported = False

    mapping = {
        "alpha": Key("a"),
        "bravo": Key("b"),
        "charlie": Key("c"),
        "delta": Key("d"),
        "echo": Key("e"),
        "foxtrot": Key("f"),
        "golf": Key("g"),
        "hotel": Key("h"),
        "india": Key("i"),
        "juliet": Key("j"),
        "kilo": Key("k"),
        "lima": Key("l"),
        "mike": Key("m"),
        "november": Key("n"),
        "oscar": Key("o"),
        "papa": Key("p"),
        "quebec": Key("q"),
        "romeo": Key("r"),
        "sierra": Key("s"),
        "tango": Key("t"),
        "uniform": Key("u"),
        "victor": Key("v"),
        "whiskey": Key("w"),
        "xray": Key("x"),
        "yankee": Key("y"),
        "zulu": Key("z"),
        "zero": Key("0"),
        "one": Key("1"),
        "two": Key("2"),
        "tree": Key("3"),
        "four": Key("4"),
        "fife": Key("5"),
        "six": Key("6"),
        "seven": Key("7"),
        "eight": Key("8"),
        "niner": Key("9"),
    }

telephony_single = Alternative([RuleRef(rule=TelephonyRule())])
telephony_sequence = Repetition(telephony_single, min=1, max=10, name="telephony_sequence")

class RepeatTelephony(CompoundRule):
    spec = '<telephony_sequence>'
    extras = [telephony_sequence]

    def _process_recognition(self, node, extras):
        for action in extras['telephony_sequence']:
            action.execute()


class CommandRule(MappingRule):

    mapping = {
        # Press escape to the blur focus on any input fields
        "click": Key("c-b"),
        "close tab": Key("c-w"),
        "new tab": Key("c-t"),
        "next tab [<n>]": Key('c-pgdown:%(n)d'),
        'pre tab [<n>]': Key('c-pgup:%(n)d'),
        'first tab': Key('c-1'),
        'second tab': Key('c-2'),
        'third tab': Key('c-3'),
        'fourth tab': Key('c-4'),
        'fifth tab': Key('c-5'),
        'sixth tab': Key('c-6'),
        'seventh tab': Key('c-7'),
        'eighth tab': Key('c-8'),
        'last tab': Key('c-9'),
        'bar': Key('c-l'),
        'back [<n>]': Key('a-left:%(n)d'),
        'forward [<n>]': Key('a-right:%(n)d'),
        'search <text>': Key('c-k/4') + Text('%(text)s'),
        'find next': Key('c-g'),
        'find pre': Key('cs-g'),
        'find <text>': Key('c-f') + Text('%(text)s\n'),
        'copy url': Key('c-l, c-c'),
    }
    extras = [
        IntegerRef('n', 1, 20),
        Dictation('text'),
    ]
    defaults = {
        'n': 1,
    }


#---------------------------------------------------------------------------

context = AppContext(executable="chrome")
grammar = Grammar("Chrome", context=context)
grammar.add_rule(CommandRule())
grammar.add_rule(RepeatTelephony())
grammar.add_rule(ScrollRule()) 
grammar.load() 

def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
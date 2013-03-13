from dragonfly import (Grammar, AppContext, MappingRule, Key, IntegerRef, Text, Dictation)

# Use wacky method to import a local file
import os, sys
sys.path.append(os.path.dirname(__file__))
from shared_rules import ScrollRule


class CommandRule(MappingRule):

    mapping = {
        "kline [<n>]": Key("cs-k:%(n)d"),
        "close tab": Key("c-w"),
        "save": Key("c-s"),
        'open file': Key('c-o'),
        "next tab [<n>]": Key('c-pgdown:%(n)d'),
        'pre tab [<n>]': Key('c-pgup:%(n)d'),
        'first tab': Key('a-1'),
        'second tab': Key('a-2'),
        'third tab': Key('a-3'),
        'fourth tab': Key('a-4'),
        'fifth tab': Key('a-5'),
        'sixth tab': Key('a-6'),
        'seventh tab': Key('a-7'),
        'eighth tab': Key('a-8'),
        'ninth tab': Key('a-9'),
        'left column': Key('c-1'),
        'right column': Key('c-2'),
        'go to file': Key('c-p'),
        'toggle sidebar': Key('c-k, c-b'),
        'find <text>': Key('c-f') + Text('%(text)s\n'),
        'find all <text>': Key('cs-f') + Text('%(text)s\n'),
        'find next': Key('f3'),
        'cancel': Key('escape'),
        'single column': Key('as-1'),
        'two column': Key('as-2'),
        'go to line <bn>': Key('c-g') + Text('%(bn)s') + Key('enter'),
    }
    extras = [
        IntegerRef('n', 1, 20),
        IntegerRef('bn', 1, 10000),
        Dictation('text'),
    ]
    defaults = {
        'n': 1,
    }


#---------------------------------------------------------------------------

context = AppContext(executable="sublime_text")
grammar = Grammar("Sublime Text 2", context=context)
grammar.add_rule(CommandRule())
grammar.add_rule(ScrollRule())
grammar.load()

def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
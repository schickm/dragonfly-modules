from dragonfly import (Grammar, AppContext, MappingRule, Key, IntegerRef)

# Use wacky method to import a local file
import os, sys
sys.path.append(os.path.dirname(__file__))
from shared_rules import ScrollRule


class CommandRule(MappingRule):

    mapping = {
        "kline [<n>]": Key("cs-k:%(n)d"),
        "open file": Key("c-x, c-f"),
        "save": Key("c-x, c-s"),
        "kill buff": Key("c-x, k, enter"),
        "left buff": Key("a-e"),
        "right buff": Key("a-u"),
    }
    extras = [
        IntegerRef('n', 1, 20),
    ]
    defaults = {
        'n': 1,
    }


#---------------------------------------------------------------------------

context = AppContext(executable="emacs")
grammar = Grammar("Emacs", context=context)
grammar.add_rule(CommandRule())
grammar.add_rule(ScrollRule())
grammar.load()

def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
import os
import subprocess

from dragonfly import (Grammar, AppContext, MappingRule, Key, IntegerRef,
                       ActionBase, Alternative, Compound, CompoundRule,
                       RuleRef, Rule)

# Use wacky method to import a local file
import os, sys
sys.path.append(os.path.dirname(__file__))
from shared_rules import ScrollRule

os.environ['PATH'] += os.pathsep + 'C:\\cygwin\\bin'
 

class MainRule(MappingRule):

    mapping = {
        'run app': Key('c-f11'),
    }



#---------------------------------------------------------------------------
context = AppContext(executable="eclipse")
grammar = Grammar("Eclipse", context=context)
grammar.add_rule(MainRule())
grammar.load()

def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
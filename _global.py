from dragonfly import (Grammar, MappingRule, Playback)


class MainRule(MappingRule):
    mapping = {
        'reload dragon': Playback([(["stop", "listening"], 0.5),
                                   (["wake", 'up'], 0.0)])
    }

grammar = Grammar('Global')
grammar.add_rule(MainRule())
grammar.load()

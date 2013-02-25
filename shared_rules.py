from dragonfly import MappingRule, Key


class ScrollRule(MappingRule):

    mapping = {
        'down': Key('pgdown'),
        'up': Key('pgup')
        }
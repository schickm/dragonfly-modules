import os
import subprocess

from dragonfly import (Grammar, AppContext, MappingRule, Key, IntegerRef,
                       ActionBase, Alternative, Compound, CompoundRule,
                       RuleRef, Rule, Dictation, Repetition)

# Use wacky method to import a local file
import os, sys
sys.path.append(os.path.dirname(__file__))
from shared_rules import ScrollRule

os.environ['PATH'] += os.pathsep + 'C:\\cygwin\\bin'


def make_alternative(name, options, default=None):
    compounds = []
    for data in options:
        if isinstance(data, str):
            value = data
        else:
            value = data[1]
            data = data[0]
        compounds.append(Compound(data, name=data, value=value))

    return Alternative(compounds, name=name, default=default)


#---------------------------------------------------------------------------
# emacsclient connection stuff 

class ShellCommand(ActionBase):

    def __init__(self, command, wait=None):
        self._command = self.format_command(command)
        self._wait = wait
        super(ShellCommand, self).__init__()

    def format_command(self, command):
        return command

    def _execute(self, data=None):
        print 'data'
        from pprint import pprint
        pprint(data)
        command = self._command % data
        #command = self._command.format(data)

        standard_out_value = subprocess.PIPE if self._wait else None
        print command
        process = subprocess.Popen(command, 
            stdout=standard_out_value,
            shell=True)
        if standard_out_value:
            output = process.communicate()[0].rstrip()
            print "out from shell: " + output
            return output 


class EmacsCommand(ShellCommand):
    def __init__(self, command, message=None, wait=None):
        """
        message - A string that will display in the echo area, 
                  upon completion of the command.
        """
        self._message = message
        super(EmacsCommand, self).__init__(command, wait)  


    def format_command(self, command):
        formatted_command = '(' + command + ')'
        if self._message:
            formatted_command = '(progn %s (message "%s"))' % (formatted_command, self._message)

        # Need to escape double quotes for the command line
        formatted_command = formatted_command.replace('"', '\\"')
        return 'emacsclient.exe -e "%s"' % formatted_command


class BufferCommand(EmacsCommand):
    def format_command(self, command):
        string = 'with-current-buffer (window-buffer (selected-window)) (%s)' % command
        return super(BufferCommand, self).format_command(string)


class CompoundCommand(BufferCommand):
    """
    Executes the initial command, waits for output, and then passes it to the
    extra commands.

    extra_commands - Singular command call afterwards, or a list of commands.
    message - Optional message to display in the Emacs echo area.
    """
    def __init__(self, command, extra_commands, message=None):
        super(CompoundCommand, self).__init__(command, message, True)
        
        if isinstance(extra_commands, EmacsCommand):
            extra_commands = [extra_commands]

        self._extra_commands = extra_commands

    def _execute(self, data=None):
        output = super(CompoundCommand, self)._execute(data)

        if data:
            data['output'] = output
        else:
            data = {'output': output}
        
        for command in self._extra_commands:
            output = command.execute(data=data)


irc_channel = make_alternative('irc_channel',
    options=(('dev', '#dev'),
             ('play', '#playground'),
             ('webco', '#webco')),
    default='#dev')

#---------------------------------------------------------------------------
# short talk stuff

def make_alternative(name, options, default=None):
    compounds = []
    for data in options:
        if isinstance(data, str):
            value = data
        else:
            value = data[1]
            data = data[0]
        compounds.append(Compound(data, name=data, value=value))

    return Alternative(compounds, name=name, default=default)

numeral = make_alternative('numeral',
    options=(('ane', 1),
             ('twain', 2),
             ('traio', 3),
             ('fairn', 4),
             ('faif', 5),
             ('oon', -1),
             ('twoon', -2),
             ('truo', -3),
             ('foorn', -4),
             ('foof', -5)),
    default=1)

struct_simple = make_alternative('struct_simple',
    options=('char', 'stretch', 'ting', 'word', 'eed', 
             'chunk', 'tier', 'line'))

struct_complex = make_alternative('struct_complex',
    options=('term', 'inner', 'block', 'defi', 'senten',
             'parra', 'buffer'))

struct = Alternative([struct_simple, struct_complex], name='struct',)

class DefaultingCompound(Compound):
    def __init__(self, spec, extras=None, actions=None, name=None,
                 value=None, elements=None, default=None):
        super(DefaultingCompound, self).__init__(spec, 
            extras=extras, actions=actions, name=name,
            value=value, elements=elements, default=default)
        self._value_func = self.return_extras

    def return_extras(self, node, extras):
        return extras


struct_range = DefaultingCompound(name='struct_range', 
    spec='<struct> [<numeral>]',
    extras=[struct, numeral])


class FlipFlopAction(ActionBase):
    """
    Action class that runs the negative or positive action based
    on value passed in data to execute.  value in data will be made
    into an absolute value when executing the negative action.
    """
    def __init__(self, negative, positive, key):
        super(FlipFlopAction, self).__init__()
        self._negative = negative
        self._positive = positive
        self._key = key

    def _execute(self, data=None):
        value = data[self._key]
        if value > 0:
            self._positive.execute(data)
        elif value < 0:
            data[self._key] = abs(value)
            self._negative.execute(data)
        

def make_key_flip_flop(negative_spec, positive_spec, key='numeral'):
    return FlipFlopAction(
        negative=Key(negative_spec), positive=Key(positive_spec),
        key=key)

emacs_delete_commands = {
    'char': make_key_flip_flop('backspace:%(numeral)d', 'c-d:%(numeral)d'),
    'word': make_key_flip_flop('a-backspace:%(numeral)d', 'a-d:%(numeral)d'),
    'term': BufferCommand('kill-sexp %(numeral)d'),
}

def execute_delete_action(data, struct, numeral):
    if numeral < 0:
        action = data[struct][0]
    else:
        action = data[struct][1]

    return action.execute(data={'numeral': abs(numeral)})


class DeleteRule(CompoundRule):
    spec = 'smack <struct_range>'
    extras = [struct_range]

    def _process_recognition(self, node, extras):
        struct_range = extras['struct_range']
        struct = struct_range['struct']
        numeral = struct_range['numeral']
        emacs_delete_commands[struct].execute({'numeral': numeral})


any_rule = Alternative([RuleRef(rule=DeleteRule()), Dictation('dict')])
repetition_any = Repetition(any_rule, min=1, max=5, name="any_rule")


move_actions = {
    'char': make_key_flip_flop('c-b:%(numeral)d', 'c-f:%(numeral)d'),
    'word': make_key_flip_flop('a-b:%(numeral)d', 'a-f:%(numeral)d, a-f, a-b'),
    'line': make_key_flip_flop('c-p:%(numeral)d', 'c-n:%(numeral)d'),
    'term': make_key_flip_flop('ca-b:%(numeral)d', 'ca-f:%(numeral)d, ca-f, ca-b'),

}

class MoveCommand(CompoundRule):
    spec = '<struct_range>'
    extras = [struct_range]

    def _process_recognition(self, node, extras):
        struct_range = extras['struct_range']
        struct = struct_range['struct']
        numeral = struct_range['numeral']
        move_actions[struct].execute({'numeral': numeral})


class RepeatAllRules(CompoundRule):
    spec = '<any_rule>'
    extras = [repetition_any]

    def _process_recognition(self, node, extras):
        from pprint import pprint
        #print node.pretty_string()
        for child in node.get_child_by_name('any_rule').children:
            #pprint(node.value())
            #pprint(node.children)
            print node.__str__()




#---------------------------------------------------------------------------
# Main

class MainRule(MappingRule):

    mapping = {
        "kline [<n>]": Key("cs-k:%(n)d"),
        'gline <bn>': BufferCommand('goto-line %(bn)d'),
        "open file": Key("c-x, c-f"),
        "save": Key("c-x, c-s"), 
        'save all': EmacsCommand('save-some-buffers'),
        'undo [<numeral>]': Key('c-underscore:%(numeral)d'),
        'quit emacs': EmacsCommand('save-buffers-kill-terminal'),
        'switch buff': EmacsCommand('ido-switch-buffer'),
        "kill buff": Key("c-x, k, enter"),
        "left win": EmacsCommand("windmove-left"),
        "right win": EmacsCommand("windmove-right"), 
        'up win': EmacsCommand('windmove-up'),
        'down win': EmacsCommand('windmove-down'),
        'close other win': EmacsCommand('delete-other-windows'),
        'vertical split win': EmacsCommand('split-window-right'),
        'horizontal split win': EmacsCommand('split-window-below'),
        'move buff right': EmacsCommand('buf-move-right'),
        'move buff left': EmacsCommand('buf-move-left'),
        'move buff up': EmacsCommand('buf-move-up'),
        'move buff down': EmacsCommand('buf-move-down'),
        'trace function': CompoundCommand('function-called-at-point', 
                                          EmacsCommand("trace-function-background '%(output)s", 'trace function %(output)s')),
        'untrace function': CompoundCommand('function-called-at-point', 
                                            EmacsCommand("untrace-function '%(output)s", 'untrace function %(output)s')),
        'untrace all': EmacsCommand('untrace-all', 'untrace all'), 
        'find function': CompoundCommand('function-called-at-point',
                                         EmacsCommand("find-function '%(output)s")),
        'folding mode': BufferCommand('hs-minor-mode'),
        'show all': Key('c-c, at, ca-s'),
        'hide all': Key('c-c, at, ca-h'), 
        'show block': Key('c-c, at, c-s'),
        'hide block': Key('c-c, at, c-h'),
        'toggle block': Key('c-c, at, c-c'),
        'start irk': EmacsCommand('onshore-irc'),
        'quit irk': BufferCommand(
            'progn (switch-to-buffer "irc.onshored.com:6667")' +
            '      (erc-quit-server "done")'),
        'irc [<irc_channel>]': EmacsCommand('switch-to-buffer "%(irc_channel)s"')

    }
    extras = [
        IntegerRef('n', 1, 20),
        IntegerRef('bn', 1, 10000),
        numeral,
        irc_channel,
    ]
    defaults = {
        'n': 1,
    }



#---------------------------------------------------------------------------
context = AppContext(executable="xwin", title="emacs")
grammar = Grammar("Emacs", context=context)
#grammar.add_rule(RepeatAllRules())
grammar.add_rule(MainRule())
grammar.add_rule(ScrollRule())
grammar.add_rule(DeleteRule())
grammar.add_rule(MoveCommand())
grammar.load()

def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
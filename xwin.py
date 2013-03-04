import os
import subprocess

from dragonfly import (Grammar, AppContext, MappingRule, Key, IntegerRef,
                       ActionBase)

# Use wacky method to import a local file
import os, sys
sys.path.append(os.path.dirname(__file__))
from shared_rules import ScrollRule

os.environ['PATH'] += os.pathsep + 'C:\\cygwin\\bin'
 

class ShellCommand(ActionBase):

    def __init__(self, command, wait=None):
        self._command = self.format_command(command)
        self._wait = wait
        super(ShellCommand, self).__init__()

    def format_command(self, command):
        return command

    def _execute(self, data=None):
        command = self._command.format(data)

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
        for command in self._extra_commands:
            output = command.execute(output)


class CommandRule(MappingRule):

    mapping = {
        "kline [<n>]": Key("cs-k:%(n)d"),
        "open file": Key("c-x, c-f"),
        "save": Key("c-x, c-s"), 
        'save all': EmacsCommand('save-some-buffers'),
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
                                          EmacsCommand("trace-function-background '{0}", 'trace function {0}')),
        'untrace function': CompoundCommand('function-called-at-point', 
                                            EmacsCommand("untrace-function '{0}", 'untrace function {0}')),
        'untrace all': EmacsCommand('untrace-all', 'untrace all'), 
        'find function': CompoundCommand('function-called-at-point',
                                         EmacsCommand("find-function '{0}")),

    }
    extras = [
        IntegerRef('n', 1, 20),
    ]
    defaults = {
        'n': 1,
    }


#---------------------------------------------------------------------------
# short talk redo

short_talk_symbols = {
    'per': '%',
}

short_talk_numerals = {
    'ane': 1,
    'oon': -1,
    'twain': 2,
    'twoon': -2
}


class SearchRule(CompoundCommand):
    pass

class DeleteRule(CompoundCommand):
    spec = 'smack <'

#---------------------------------------------------------------------------
context = AppContext(executable="xwin")
grammar = Grammar("Emacs Old", context=context)
grammar.add_rule(CommandRule())
grammar.add_rule(ScrollRule())
grammar.load()

def unload():
    global grammar
    if grammar: grammar.unload()
    grammar = None
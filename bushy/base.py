""" The base class for bushy script processing.
"""

import sys
from commands import getoutput

        
class Base(object):

    def __init__(self, input=sys.stdin, output=sys.stdout, args=sys.argv):
        self.input = input
        self.output = output
        
        parser = self.init_parser()
        (option_values, args) = parser.parse_args(args)
        
        options = option_values.__dict__
        gitconfig = self.parse_gitconfig()
        
        options.update(gitconfig)
        self.options = options

    def init_parser(self):
        raise NotImplementedError('This method should be written specifically for the platform being used')
        
    def parse_gitconfig(self):
        raise NotImplementedError('This method should be written specifically for the platform being used')
    
    _integration_branch = None
    @property
    def integration_branch(self):
        if self._integration_branch is None:
            integration_branch = self.options.get('integration_branch')
            self._integration_branch = integration_branch
        return self._integration_branch or 'master'
            
    def __call__(self):
        if None in (self.options.get('api_token'), self.options.get('project_id')):
            raise RuntimeError('Pivotal Tracker API Token and Project ID are required')

    # convenience

    def put(self, msg, newline=True):
        if not self.options.get('quiet', False):
            if not isinstance(msg, basestring):
                msg = str(msg)
            self.output.write(msg.encode('ascii', 'replace'))
            if newline:
                self.output.write('\n')

    def sys(self, cmd):
        if self.options.get('verbose'):
            self.put('Running command: ', False)
            self.put(cmd)
        return getoutput(cmd)
        

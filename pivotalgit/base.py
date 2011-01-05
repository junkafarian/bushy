""" The base class for pivotalgit script processing.
"""

import sys
import optparse
from commands import getoutput
from pivotal import Pivotal

def init_parser(self):
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option('-k', '--api-key', dest='api_token', help='Pivotal Tracker API key')
    parser.add_option('-p', '--project-id', dest='project_id', help='Pivotal Tracker project id')
    parser.add_option('-n', '--full-name', dest='full_name', help='Pivotal Tracker full name')
    parser.add_option('-b', '--integration-branch', dest='integration_branch', help='The branch to merge finished stories back down onto')
    parser.add_option('-m', '--only-mine', dest='only_mine', help='Only select Pivotal Tracker stories assigned to you')
    parser.add_option('-q', '--quiet', action="store_true", dest='quiet', help='Quiet, no-interaction mode')
    parser.add_option('-v', '--verbose', action="store_true", dest='verbose', help='Run verbosely')
    return parser

def parse_gitconfig():
    config = {}
    keys = [
        'api-token',
        'project-id',
        'full-name',
        'integration-branch',
        'only-mine'
        ]
    for key in keys:
        val = getoutput('git config --get pivotal.%s' % key)
        if val:
            config[key.replace('-', '_')] = val.strip()
    if 'only_mine' in config:
        config['only_mine'] = bool(config['only_mine'])
    return config
        
        
class Base:

    def __init__(self, input=sys.stdin, output=sys.stdout, args=sys.argv):
        self.input = input
        self.output = output
        
        parser = self.init_parser()
        (option_values, args) = parser.parse_args(args)
        
        options = option_values.__dict__
        gitconfig = parse_gitconfig()
        
        options.update(gitconfig)
        self.options = options

    _api = None
    @property
    def api(self):
        if self._api is None:
            api = Pivotal(self.options['api_token'])
            self._api = api
        return self._api
            
    _project = None
    @property
    def project(self):
        if self._project is None:
            project = self.api.projects(self.options['project_id'])
            self._project = project
        return self._project
            
    _integration_branch = None
    @property
    def integration_branch(self):
        if self._integration_branch is None:
            integration_branch = self.options.get('integration_branch')
            self._integration_branch = integration_branch
        return self._integration_branch or 'master'
            
    def __call__(self):
        if None in (self.options['api_token'], self.options['project_id']):
            raise RuntimeError('Pivotal Tracker API Token and Project ID are required')

    # convenience

    def put(self, msg, newline=True):
        if not self.options.get('quiet', False):
            self.output.write(msg and '\n' if newline else '')

    def sys(self, cmd):
        if self.options.get('verbose'):
            self.put('Running command: ', False)
            self.put(cmd)
        return getoutput(cmd)
        

'''
require 'optparse'

module Commands
  class Base

    attr_accessor :input, :output, :options
  
    def initialize(input=STDIN, output=STDOUT, *args)
      @input = input
      @output = output
      @options = {}
      
      parse_gitconfig
      parse_argv(*args)
    end
  
    def put(string, newline=true)
      @output.print(newline ? string + "\n" : string) unless options[:quiet]
    end

    def sys(cmd)
      put cmd if options[:verbose]
      system cmd
    end

    def get(cmd)
      put cmd if options[:verbose]
      `#{cmd}`
    end
    
    def run!
      unless options[:api_token] && options[:project_id]
        put "Pivotal Tracker API Token and Project ID are required"
        return 1
      end
    end

  protected

    def project
      @project ||= api.projects.find(:id => options[:project_id])
    end

    def api
      @api ||= Pivotal::Api.new(:api_token => options[:api_token])
    end

    def integration_branch
      options[:integration_branch] || "master"
    end

  private

    def parse_gitconfig
      token = get("git config --get pivotal.api-token").strip
      id = get("git config --get pivotal.project-id").strip
      name = get("git config --get pivotal.full-name").strip
      integration_branch = get("git config --get pivotal.integration-branch").strip
      only_mine = get("git config --get pivotal.only-mine").strip

      options[:api_token] = token unless token == ""
      options[:project_id] = id unless id == ""
      options[:full_name] = name unless name == ""
      options[:integration_branch] = integration_branch unless integration_branch == ""
      options[:only_mine] = (only_mine != "") unless name == ""
    end

    def parse_argv(*args)
      OptionParser.new do |opts|
        opts.banner = "Usage: git pick [options]"
        opts.on("-k", "--api-key=", "Pivotal Tracker API key") { |k| options[:api_token] = k }
        opts.on("-p", "--project-id=", "Pivotal Trakcer project id") { |p| options[:project_id] = p }
        opts.on("-n", "--full-name=", "Pivotal Trakcer full name") { |n| options[:full_name] = n }
        opts.on("-b", "--integration-branch=", "The branch to merge finished stories back down onto") { |b| options[:integration_branch] = b }
        opts.on("-m", "--only-mine", "Only select Pivotal Tracker stories assigned to you") { |m| options[:only_mine] = m }
        opts.on("-q", "--quiet", "Quiet, no-interaction mode") { |q| options[:quiet] = q }
        opts.on("-v", "--[no-]verbose", "Run verbosely") { |v| options[:verbose] = v }
        opts.on_tail("-h", "--help", "This usage guide") { put opts.to_s; exit 0 }
      end.parse!(args)
'''

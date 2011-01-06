""" Utilities for interfacing with a Pivotal Tracker project
"""

import optparse
from commands import getoutput
from pivotal import Pivotal, anyetree
from bushy.base import Base

class PivotalBase(Base):
    
    def init_parser(self):
        parser = optparse.OptionParser(description=__doc__)
        parser.add_option('-k', '--api-key', dest='api_token', help='Pivotal Tracker API key')
        parser.add_option('-p', '--project-id', dest='project_id', help='Pivotal Tracker project id')
        parser.add_option('-n', '--full-name', dest='full_name', help='Pivotal Tracker full name')
        parser.add_option('-b', '--integration-branch', dest='integration_branch', default='master', help='The branch to merge finished stories back down onto')
        parser.add_option('-m', '--only-mine', dest='only_mine', help='Only select Pivotal Tracker stories assigned to you')
        parser.add_option('-q', '--quiet', action="store_true", dest='quiet', help='Quiet, no-interaction mode')
        parser.add_option('-v', '--verbose', action="store_true", dest='verbose', help='Run verbosely')
        return parser

    def parse_gitconfig(self):
        config = {}
        keys = [
            'api-token',
            'project-id',
            'full-name',
            'integration-branch',
            'only-mine'
            ]
        for key in keys:
            val = getoutput('git config --get bushy-pivotal.%s' % key)
            if val:
                config[key.replace('-', '_')] = val.strip()
        if 'only_mine' in config:
            config['only_mine'] = bool(config['only_mine'])
        return config
        
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

def format_filter(qs):
    filters = ['%s:%s' % (k,v) for k,v in qs.items()]
    return ' '.join(filters)

from datetime import datetime
import httplib2

def etree_text(etree, element):
    if etree.find(element) is not None:
        return etree.find(element).text
    return ''

def etree_int(etree, element):
    if etree.find(element) is not None:
        return int(etree.find(element).text)
    return 0

def etree_datetime(etree, element):
    if etree.find(element) is not None:
        return datetime.strptime(etree.find(element).text, '%Y/%m/%d %H:%M:%S UTC')
    return None

class Story(object):
    def __init__(self, etree):
        self._update(etree)

    def _update(self, etree):
        self.id = etree_int(etree, 'id')
        self.project_id = etree_int(etree, 'project_id')
        self.story_type = etree_text(etree, 'story_type')
        self.url = etree_text(etree, 'url')
        self.estimate = etree_int(etree, 'estimate')
        self.current_state = etree_text(etree, 'current_state')
        self.description = etree_text(etree, 'description')
        self.name = etree_text(etree, 'name')
        self.requested_by = etree_text(etree, 'requested_by')
        self.owned_by = etree_text(etree, 'owned_by')
        self.created_at = etree_datetime(etree, 'created_at')
        self.updated_at = etree_datetime(etree, 'updated_at')

    def update_status(self, token, status):
        h = httplib2.Http()
        h.force_exception_to_status_code = True
        
        url = 'http://www.pivotaltracker.com/services/v3/projects/%s/stories/%s' % (self.project_id, self.id)
        headers = {'X-TrackerToken': token, 'Content-type': 'application/xml'}
        body = '<story><current_state>%s</current_state></story>' % status
        
        resp, content = h.request(url, 'PUT', headers=headers, body=body)
        
        etree = anyetree.etree.fromstring(content)
        self._update(etree)
        
    def start(self, token):
        self.update_status(token, 'started')
        
class Pick(PivotalBase):
    
    @property
    def type(self):
        raise NotImplementedError('Must define in subclass')

    @property
    def plural_type(self):
        raise NotImplementedError('Must define in subclass')

    @property
    def branch_suffix(self):
        raise NotImplementedError('Must define in subclass')

    _story = None
    @property
    def story(self):
        if not self._story:
            qs = {'state': 'unstarted',
                  'type': self.type,
                  }
            if self.options.get('only_mine'):
                qs['owned_by'] = self.options['full_name']
            stories = self.project.stories(filter=format_filter(qs)).get_etree()
            story = stories.find('story')
            if story:
                self._story = Story(story)
        return self._story
        
    
    def __call__(self):
        super(Pick, self).__call__()
        
        msg = 'Retrieving latest %s from Pivotal Tracker' % self.plural_type
        if self.options['only_mine']:
            msg += " for" + self.options['full_name']

        self.put(msg)
        
        story = self.story
        
        if story is None:
            self.put('No %s available!' % self.plural_type)
            return
        
        self.put('Story: %s' % story.name)
        self.put('URL: %s' % story.url)

        self.put('Updating %s status in Pivotal Tracker...' % self.type)

        story.start(self.api.token)
        if story.owned_by == self.options['full_name']:
            suffix = default = self.branch_suffix
            if not self.options['quiet']:
                suffix = raw_input('Enter branch name (will be prepended by %s) [%s]: ' % (story.id, default))
                if suffix == '':
                    suffix = default

            branch = '%s-%s' % (story.id, suffix)
            branches = self.sys('git branch')
            if branch not in branches:
                self.put('Creating new branch: ', False)
                self.put(branch)
                self.sys('git checkout -b %s' % branch)
            else:
                self.put('Switching to branch %s' % branch)
                self.sys('git checkout %s' % branch)

        else:
            self.put('Unable to update ', False)
            self.put(story.id)
            

class Feature(Pick):
    type = 'feature'
    plural_type = 'features'
    branch_suffix = 'feature'
    

class Bug(Pick):
    type = 'bug'
    plural_type = 'bugs'
    branch_suffix = 'bug'

class Finish(PivotalBase):

    @property
    def current_branch(self):
        branches = self.sys('git branch')
        branches = branches.split('\n')
        for b in branches:
            if b.startswith('* '):
                return b.strip('* ')
        
        return ''

    @property
    def story_id(self):
        current_branch = self.current_branch
        story_id,_ = current_branch.split('-', 1)
        return story_id
    
    _story = None
    @property
    def story(self):
        if not self._story:
            qs = {}
            qs['owned_by'] = self.options['full_name']
            
            stories = self.project.stories(filter=format_filter(qs)).get_etree()
            for story in stories.getchildren():
                if story.find('id').text == self.story_id:
                    self._story = Story(story)
            
        return self._story
    
    def __call__(self):
        super(Finish, self).__call__()
      
        if not self.story_id:
            self.put('The current branch name (%s) does not follow the '+\
                     'correct format, please checkout the correct '+\
                     'branch then re-run this command' % self.current_branch)
            return

        story = self.story
        self.put('Marking Story %s as finished...' % story.id)
        story.update_status(self.api.token, 'finished')
        if story.current_state == 'finished':
            integration_branch = self.options['integration_branch']
            current_branch = self.current_branch
            self.put('Merging %s into %s' % (current_branch, integration_branch))
            out = self.sys('git checkout %s' % integration_branch)
            if 'error: ' in out:
                # TODO: error handling for each command (or before running commands)
                self.put('There was an error checking out master:\n%s' % out)
                return
            self.sys('git merge --no-ff %s' % current_branch)
            
            self.put('Removing %s branch' % current_branch)
            self.sys('git branch -d %s' % current_branch)

        else:
            self.put('Unable to mark Story %s as finished' % story.id)
        


""" Utilities for interfacing with a Pivotal Tracker project
"""

import sys
import optparse
import httplib2
from datetime import datetime
from commands import getoutput
from pivotal import Pivotal, anyetree
from bushy.base import Base

__all__ = ['Bug',
           'Feature',
           'Finish',
           ]

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

class Story(PivotalBase):
    def __init__(self, etree, input=sys.stdin, output=sys.stdout, args=sys.argv):
        super(Story, self).__init__(input, output, args)
        self._update(etree)
        self.h = httplib2.Http()
        self.h.force_exception_to_status_code = True

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

    def update_status(self, status):
        h = self.h
        
        url = 'http://www.pivotaltracker.com/services/v3/projects/%s/stories/%s' % (self.project_id, self.id)
        headers = {'X-TrackerToken': self.api.token, 'Content-type': 'application/xml'}
        body = '<story><current_state>%s</current_state></story>' % status
        
        resp, content = h.request(url, 'PUT', headers=headers, body=body)
        
        etree = anyetree.etree.fromstring(content)
        self._update(etree)
        
    def update_owner(self, owner):
        h = self.h
        
        url = 'http://www.pivotaltracker.com/services/v3/projects/%s/stories/%s' % (self.project_id, self.id)
        headers = {'X-TrackerToken': self.api.token, 'Content-type': 'application/xml'}
        body = '<story><owned_by>%s</owned_by></story>' % owner
        
        resp, content = h.request(url, 'PUT', headers=headers, body=body)
        
        etree = anyetree.etree.fromstring(content)
        self._update(etree)
        
    def comment(self, comment):
        h = self.h
        
        url = 'http://www.pivotaltracker.com/services/v3/projects/%s/stories/%s/notes' % (self.project_id, self.id)
        headers = {'X-TrackerToken': self.api.token, 'Content-type': 'application/xml'}
        body = '<note><text>%s</text></note>' % comment
        
        resp, content = h.request(url, 'POST', headers=headers, body=body)
        return content
        
    def start(self):
        self.update_status('started')
        self.update_owner(self.options['full_name'])
        self.comment('Story started by %s' % self.options['full_name'])
    

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
            if story: # pragma: no cover
                self._story = Story(story)
        return self._story
        
    
    def __call__(self, args=sys.argv, raw_input=raw_input):
        super(Pick, self).__call__()

        if len(args) == 3 and args[-1] != self.type:
            # the command was run in the format `git TYPE STORY_NUMBER`
            pass
        elif len(args) == 2 and args[-1] != self.type:
            # the command was run in the format `git-TYPE STORY_NUMBER`
            pass
        else:
            # there was no story number provided so just pick the first one
            msg = 'Retrieving latest %s from Pivotal Tracker' % self.plural_type
            if self.options['only_mine']:
                msg += " for " + self.options['full_name']

        self.put(msg)
        
        story = self.story
        
        if story is None:
            self.put('No %s available!' % self.plural_type)
            return
        
        self.put('Story: %s' % story.name)
        self.put('URL: %s' % story.url)

        self.put('Updating %s status in Pivotal Tracker...' % self.type)

        story.start()
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


## Command line API ##

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
        if '-' not in current_branch:
            return ''
        
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
                if hasattr(story.find('id'), 'text') and story.find('id').text == self.story_id: # pragma: no cover
                    self._story = Story(story)
                    break
            
        return self._story
    
    def __call__(self):
        super(Finish, self).__call__()
      
        if self.story_id == '':
            self.put('The current branch name (%s) does not follow the '
                     'correct format, please checkout the correct '
                     'branch then re-run this command' % self.current_branch)
            return

        story = self.story
        self.put('Marking Story %s as finished...' % story.id)
        story.update_status('finished')
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

            story.comment('Development work for this story has been merged into the trunk')
            
            self.put('Merged code into trunk. Please push upstream and notify the release manager if necessary')

        else:
            self.put('Unable to mark Story %s as finished' % story.id)
        


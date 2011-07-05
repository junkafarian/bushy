import unittest
from cStringIO import StringIO

class TestFormatFilter(unittest.TestCase):
    def _callFUT(self, qs):
        from bushy._pivotal import format_filter
        return format_filter(qs)

    def test_format(self):
        qs = {'key1': 'value1',
              'key2': 2,
              }

        res = self._callFUT(qs)

        self.assertEqual(res, 'key2:2 key1:value1')

class TestEtreeUtils(unittest.TestCase):
    def setUp(self):
        self.xml = '''\
          <xml>
            <text_attr>foobar</text_attr>
            <int_attr>1</int_attr>
            <datetime_attr>2021/12/21 21:21:21 UTC</datetime_attr>
          </xml>
        '''

    def _makeOne(self, xml):
        from pivotal import anyetree
        return anyetree.etree.fromstring(xml)

    def test_text(self):
        etree = self._makeOne(self.xml)

        from bushy._pivotal import etree_text
        self.assertEqual(etree_text(etree, 'text_attr'), 'foobar')
        self.assertEqual(etree_text(etree, 'non_attr'), '')
        
    def test_int(self):
        etree = self._makeOne(self.xml)

        from bushy._pivotal import etree_int
        self.assertEqual(etree_int(etree, 'int_attr'), 1)
        self.assertEqual(etree_int(etree, 'non_attr'), 0)
        self.assertRaises(ValueError, etree_int,
                          etree, 'text_attr')
        

    def test_datetime(self):
        etree = self._makeOne(self.xml)

        from bushy._pivotal import etree_datetime
        from datetime import datetime
        self.assertEqual(etree_datetime(etree, 'datetime_attr'), datetime(2021, 12, 21, 21, 21, 21))
        self.assertEqual(etree_datetime(etree, 'non_attr'), None)
        self.assertRaises(ValueError, etree_datetime,
                          etree, 'text_attr')
        

class TestPivotalBase(unittest.TestCase):
    def setUp(self):
        self._input = StringIO()
        self._output = StringIO()

    def tearDown(self):
        import bushy._pivotal
        bushy._pivotal.getoutput = self._getoutput
    
    def _patch_getoutput(self, value):
        import bushy._pivotal
        self._getoutput = bushy._pivotal.getoutput
        bushy._pivotal.getoutput = lambda x: value

    def _makeOne(self, args):
        from bushy._pivotal import PivotalBase
        return PivotalBase(self._input, self._output, args)
    
    def test_parser(self):
        self._patch_getoutput('')
        
        base = self._makeOne([])

        self.assertEqual(base.options['integration_branch'], 'master',
                         'The integration branch should be the default')

    def test_gitconfig(self):
        self._patch_getoutput('true')
        
        base = self._makeOne([])

        self.assertEqual(base.options['integration_branch'], 'true',
                         'The integration branch should overridden by gitconfig')

    def test_api(self):
        self._patch_getoutput('true')
        
        base = self._makeOne([])
        base.options['api_token'] = 'token'

        self.assertEqual(base.api.token, 'token')
        
    def test_project(self):
        self._patch_getoutput('true')
        
        base = self._makeOne([])
        base.options['api_token'] = 'token'
        base.options['project_id'] = 'uniqueproject'

        self.assertTrue(base.project.url.endswith('/uniqueproject'))
        self.assertEqual(base.project.token, 'token')
        
class TestStory(unittest.TestCase):
    def setUp(self):
        self._input = StringIO()
        self._output = StringIO()
        
    def _makeOne(self, xml, args):
        from bushy._pivotal import Story
        from pivotal import anyetree

        etree = anyetree.etree.fromstring(xml)
        return Story(etree, input=self._input, output=self._output, args=args)

    def test_init(self):
        story = self._makeOne('<xml></xml>', [])

        self.assertEqual(story.id, 0)
        self.assertEqual(story.project_id, 0)
        self.assertEqual(story.story_type, '')
        self.assertEqual(story.url, '')
        self.assertEqual(story.estimate, 0)
        self.assertEqual(story.current_state, '')
        self.assertEqual(story.description, '')
        self.assertEqual(story.name, '')
        self.assertEqual(story.requested_by, '')
        self.assertEqual(story.owned_by, '')
        self.assertEqual(story.created_at, None)
        self.assertEqual(story.updated_at, None)

    def test_update_status(self):
        story = self._makeOne('<xml></xml>', [])

        status = 'started'
        
        story.h = DummyHttp()
        story.h.content = '<story><current_state>%s</current_state></story>' % status

        self.assertEqual(story.current_state, '')
        
        story.update_status(status)

        self.assertEqual(story.current_state, status)
        
    def test_update_owner(self):
        story = self._makeOne('<xml></xml>', [])

        owner = 'user'
        
        story.h = DummyHttp()
        story.h.content = '<story><owned_by>%s</owned_by></story>' % owner

        self.assertEqual(story.owned_by, '')
        
        story.update_owner(owner)

        self.assertEqual(story.owned_by, owner)
        
    def test_comment(self):
        story = self._makeOne('<xml></xml>', [])

        comment = 'started'
        
        story.h = DummyHttp()

        story.comment(comment)

        self.assertEqual(story.h.requests[0][3], '<note><text>%s</text></note>' % comment)

    def test_start(self):
        story = self._makeOne('<xml></xml>', [])

        story.options['full_name'] = 'Mr Test'
        
        story.h = DummyHttp()
        story.h.responses.append('<story><current_state>%s</current_state></story>' % 'started')
        story.h.responses.append('<story><current_state>%s</current_state><owned_by>%s</owned_by></story>' % ('started', story.options['full_name']))

        story.start()
        
        self.assertEqual(story.current_state, 'started')
        self.assertEqual(story.owned_by, story.options['full_name'])
        self.assertEqual(story.h.requests[2][3], '<note><text>Story started by %s</text></note>' % story.options['full_name'])
        

    
class TestPick(unittest.TestCase):
    def setUp(self):
        self._input = StringIO()
        self._output = StringIO()
        
    def _makeOne(self, args):
        from bushy._pivotal import Pick

        return Pick(input=self._input, output=self._output, args=args)

    def test_type(self):
        pick = self._makeOne([])

        self.assertRaises(NotImplementedError, lambda: pick.type)

    def test_plural_type(self):
        pick = self._makeOne([])

        self.assertRaises(NotImplementedError, lambda: pick.plural_type)

    def test_branch_suffix(self):
        pick = self._makeOne([])

        self.assertRaises(NotImplementedError, lambda: pick.branch_suffix)


class TestFeature(unittest.TestCase):
    def setUp(self):
        self._input = StringIO()
        self._output = StringIO()
        
    def _makeOne(self, args):
        from bushy._pivotal import Feature

        return Feature(input=self._input, output=self._output, args=args)

    def _patch_getoutput(self, value):
        import bushy._pivotal
        self._getoutput = bushy._pivotal.getoutput
        bushy._pivotal.getoutput = lambda x: value

    def test_type(self):
        pick = self._makeOne([])

        self.assertEqual(pick.type, 'feature')

    def test_plural_type(self):
        pick = self._makeOne([])

        self.assertEqual(pick.plural_type, 'features')

    def test_branch_suffix(self):
        pick = self._makeOne([])

        self.assertEqual(pick.branch_suffix, 'feature')

    def test_story(self):
        self._patch_getoutput('true')
        
        pick = self._makeOne([])
        pick.options['api_token'] = 'token'
        pick.options['project_id'] = 'uniqueproject'

        # make sure we've got sufficient access to the pick.project attribute
        self.assertTrue(pick.project.url.endswith('/uniqueproject'))
        self.assertEqual(pick.project.token, 'token')

        # test badly configured api / project values don't break the machinery
        self.assertEqual(pick._story, None)
        self.assertEqual(pick.story, None) # call the property
        self.assertEqual(pick._story, None)

        
class DummyHttp(object):
    def __init__(self):
        self.requests = []
        self.headers = {'status': '200',
                        }
        self.content = ''
        self.responses = []

    def request(self, url, method, headers={}, body=''):
        self.requests.append((url, method, headers, body))
        if len(self.responses):
            print self.responses
            return self.headers, self.responses.pop(0)
        return self.headers, self.content
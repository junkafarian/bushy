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

    

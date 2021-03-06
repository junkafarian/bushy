import unittest
import optparse
from cStringIO import StringIO
from bushy.base import Base

class TestBase(unittest.TestCase):
    def setUp(self):
        self._input = StringIO()
        self._output = StringIO()
        
    def _patch_getoutput(self, value):
        import bushy.base
        self._getoutput = bushy.base.getoutput
        bushy.base.getoutput = lambda x: x

    def tearDown(self):
        if hasattr(self, '_getoutput'):
            import bushy.base
            bushy.base.getoutput = self._getoutput
    
    def _makeOne(self, args):
        return DummyBase(self._input, self._output, args)

    def test_init(self):
        base = self._makeOne([])

        self.assertEqual(base.input, self._input)
        self.assertEqual(base.output, self._output)
        self.assertEqual(base.options, {})

    def test_empty_integration_branch(self):
        base = self._makeOne([])

        self.assertEqual(base.integration_branch, 'master')
        self.assertEqual(base._integration_branch, None)

    def test_integration_branch(self):
        base = self._makeOne([])
        base.options['integration_branch'] = 'integration'

        self.assertEqual(base._integration_branch, None)
        self.assertEqual(base.integration_branch, 'integration')
        self.assertEqual(base._integration_branch, 'integration')

    def test_call(self):
        base = self._makeOne([])

        self.assertRaises(RuntimeError, base)

        base.options['api_token'] = 'token'
        base.options['project_id'] = '1'
        
        self.assertEqual(base(), None)
    
    def test_put(self):
        base = self._makeOne([])

        base.put('hello world')
        self._output.seek(0)
        out = self._output.read()
        self.assertEqual(out, 'hello world\n')

    def test_put_non_string(self):
        base = self._makeOne([])

        base.put(0)
        self._output.seek(0)
        out = self._output.read()
        self.assertEqual(out, '0\n')
    
    def test_put_no_newline(self):
        base = self._makeOne([])

        base.put('hello world', newline=False)
        self._output.seek(0)
        out = self._output.read()
        self.assertEqual(out, 'hello world')

    def test_put_options(self):
        base = self._makeOne([])
        
        base.options['quiet'] = True

        base.put('hello world')
        self._output.seek(0)
        out = self._output.read()
        self.assertEqual(out, '')
        
        base.options['quiet'] = False

        base.put('hello world')
        self._output.seek(0)
        out = self._output.read()
        self.assertEqual(out, 'hello world\n')

    def test_sys(self):
        self._patch_getoutput('')
        base = self._makeOne([])

        self.assertEqual(base.sys('foo'), 'foo')
        self._output.seek(0)
        out = self._output.read()
        self.assertEqual(out, '')
    
    def test_sys_verbose(self):
        self._patch_getoutput('')
        base = self._makeOne([])

        base.options['verbose'] = True

        self.assertEqual(base.sys('foo'), 'foo')
        self._output.seek(0)
        out = self._output.read()
        self.assertEqual(out, 'Running command: foo\n')
        

class DummyBase(Base):
    """ Provide the most minimal implementation of the mixin class to
        allow testing.
    """
    def init_parser(self):
        return optparse.OptionParser()
    
    def parse_gitconfig(self):
        return {}
    


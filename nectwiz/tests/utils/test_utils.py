import unittest

from nectwiz.core.core import utils
from nectwiz.core.core.utils import unmuck_primitives


class TestUtils(unittest.TestCase):
  
  def test_deep_get2(self):
    src = {'x': 'y'}
    self.assertEqual(src, utils.deep_get2(src, ''))

    src = {'x': 'y'}
    self.assertEqual('y', utils.deep_get2(src, 'x'))

    src = {'x': 'y'}
    self.assertEqual(None, utils.deep_get2(src, 'x2'))

    src = {'x': {'x': 'y'}}
    self.assertEqual('y', utils.deep_get2(src, 'x.x'))

    src = {'x': {'x': 'y'}}
    self.assertEqual({'x': 'y'}, utils.deep_get2(src, 'x'))

    src = {'x': {'x': 'y'}}
    self.assertEqual(None, utils.deep_get2(src, 'x.x2'))

  def test_deep_set(self):
    root = dict(x='x', y='y')
    utils.deep_set(root, ['x'], 'y')
    self.assertEqual(root, dict(x='y', y='y'))

    root = dict(x=dict(x='x', y='y'), y='y')
    utils.deep_set(root, ['x', 'x'], 'y')
    expect = dict(x=dict(x='y', y='y'), y='y')
    self.assertEqual(root, expect)

    root = dict()
    utils.deep_set(root, ['x', 'x'], 'x')
    self.assertEqual(root, dict(x=dict(x='x')))

  def test_keyed2dict(self):
    actual = utils.keyed2dict([('bar', 'foo'), ('foo.bar', 'baz')])
    expected = dict(bar='foo', foo=dict(bar='baz'))
    self.assertEqual(expected, actual)

  def test_dict_to_keyed(self):
    actual = utils.dict2keyed(dict(
      bar='foo',
      foo=dict(
        bar='baz',
        foo=dict(bar='baz')
      )
    ))
    expected = [('bar', 'foo'), ('foo.bar', 'baz'), ('foo.foo.bar', 'baz')]
    self.assertEqual(expected, actual)

  def test_hybrid_dict_to_keyed(self):
    actual = utils.dict2keyed({
      'foo.bar': 'baz',
      'bar.foo': 'zab'
    })

    expected = [('foo.bar', 'baz'), ('bar.foo', 'zab')]
    self.assertEqual(expected, actual)

  def test_kao2log(self):
    self.assertEqual("apps.deployment/foo created", utils.kao2log(dict(
      api_group='apps',
      kind='deployment',
      name='foo',
      verb='created'
    )))

    self.assertEqual("pod/bar unchanged", utils.kao2log(dict(
      api_group='',
      kind='pod',
      name='bar',
      verb='unchanged'
    )))

    self.assertEqual("pod/baz error text", utils.kao2log(dict(
      kind='pod',
      name='baz',
      error='error text'
    )))

  def test_log2ktlapplyoutcome(self):
    log = "pod/foo created"
    result = utils.log2kao(log)
    self.assertEqual('pod', result['kind'])
    self.assertEqual('foo', result['name'])
    self.assertEqual('created', result['verb'])
    self.assertEqual('', result['api_group'])

    log = "deployment.apps/foo created"
    result = utils.log2kao(log)
    self.assertEqual('deployment', result['kind'])
    self.assertEqual('foo', result['name'])
    self.assertEqual('created', result['verb'])
    self.assertEqual('apps', result['api_group'])

    log = "role.rbac.authorization.k8s.io/foo unchanged"
    result = utils.log2kao(log)
    self.assertEqual('role', result['kind'])
    self.assertEqual('foo', result['name'])
    self.assertEqual('unchanged', result['verb'])
    self.assertEqual('rbac.authorization.k8s.io', result['api_group'])

  def test_unmuck_primitives(self):
    actual = 'foo'
    self.assertEqual(actual, unmuck_primitives(actual))

    actual = dict(x='y')
    self.assertEqual(actual, unmuck_primitives(actual))

    actual = dict(x=0)
    self.assertEqual(actual, unmuck_primitives(actual))

    actual, exp = dict(x='0'), dict(x=0)
    self.assertEqual(exp, unmuck_primitives(actual))

    actual, exp = [dict(x='0')], [dict(x=0)]
    self.assertEqual(exp, unmuck_primitives(actual))

    actual, exp = [[0], '0'], [[0], 0]
    self.assertEqual(exp, unmuck_primitives(actual))

    actual, exp = [dict(x=['false'])], [dict(x=[False])]
    self.assertEqual(exp, unmuck_primitives(actual))

    actual = dict(x=[[dict(x=False)]], y=[True])
    self.assertEqual(actual, unmuck_primitives(actual))

import unittest

from nectwiz.core.core import utils


class TestUtils(unittest.TestCase):
  
  def test_deep_get2(self):
    src = {'x': 'y'}
    self.assertEqual('y', utils.deep_get2(src, 'x'))

    src = {'x': 'y'}
    self.assertEqual(None, utils.deep_get2(src, 'x2'))

    src = {'x': {'x': 'y'}}
    self.assertEqual('y', utils.deep_get2(src, 'x.x'))

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

  def test_log2ktlapplyoutcome(self):
    log = "pod/foo created"
    self.assertEqual(dict(
      kind='pod',
      name='foo',
      verb='created',
      api_group=''
    ), utils.log2outkome(log))

    log = "deployment.apps/foo created"
    self.assertEqual(dict(
      kind='deployment',
      name='foo',
      verb='created',
      api_group='apps'
    ), utils.log2outkome(log))

    log = "role.rbac.authorization.k8s.io/foo unchanged"
    self.assertEqual(dict(
      kind='role',
      name='foo',
      verb='unchanged',
      api_group='rbac.authorization.k8s.io'
    ), utils.log2outkome(log))

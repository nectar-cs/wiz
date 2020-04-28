import unittest

from tests.test_helpers.cluster_test import ClusterTest
from tests.test_helpers.helper import simple_tec_setup
from wiz.core import tec_prep, tec_client
from wiz.core.res_match_rule import ResMatchRule
from wiz.core.tec_client import deep_set, filter_res
from wiz.core.wiz_globals import wiz_globals


def g_rule(expr):
  return ResMatchRule(expr)


def g_res(_tuple):
  return dict(
    kind=_tuple[0],
    metadata=dict(
      name=_tuple[1],
      namespace=_tuple[2] if len(_tuple) == 3 else _tuple[1]
    )
  )


def g_res_list(*tuples):
  return [g_res(t) for t in tuples]


class TestTecClient(ClusterTest):

  def test_deep_set(self):
    root = dict(x='x', y='y')
    deep_set(root, ['x'], 'y')
    self.assertEqual(root, dict(x='y', y='y'))

    root = dict(x=dict(x='x', y='y'), y='y')
    deep_set(root, ['x', 'x'], 'y')
    expect = dict(x=dict(x='y', y='y'), y='y')
    self.assertEqual(root, expect)

    root = dict()
    deep_set(root, ['x', 'x'], 'x')
    self.assertEqual(root, dict(x=dict(x='x')))

  def test_filter_res(self):
    res_list = g_res_list(('k1', 'n1'), ('k1', 'n2'))
    result = filter_res(res_list, [g_rule("k1:n1")])
    self.assertEqual(result, [res_list[0]])

  def test_gen_raw_manifest(self):
    wiz_globals.ns = 'n1'
    tec_prep.create('n1', simple_tec_setup())
    tec_client.tec_pod().wait_until_running()
    res_list = tec_client.gen_raw_manifest()
    kinds = sorted([r['kind'] for r in res_list])
    self.assertEqual(len(res_list), 2)
    self.assertEqual(kinds, sorted(['Pod', 'Service']))

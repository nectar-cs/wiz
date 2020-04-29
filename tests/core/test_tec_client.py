import yaml

from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.res.svc.kat_svc import KatSvc
from k8_kat.utils.testing import ns_factory
from tests.test_helpers.cluster_test import ClusterTest
from tests.test_helpers.helper import simple_tec_setup, create_base_master_map
from wiz.core import tec_prep, tec_client
from wiz.core.res_match_rule import ResMatchRule
from wiz.core.tec_client import deep_set, filter_res
from wiz.core.wiz_globals import wiz_globals


class TestTecClient(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestTecClient, cls).setUpClass()
    cls.n1, cls.n2, cls.n3, cls.n4 = ns_factory.request(4)

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
    tec_prep.create(self.n1, simple_tec_setup())
    tec_client.tec_pod().wait_until_running()
    res_list = tec_client.load_raw_manifest()
    kinds = sorted([r['kind'] for r in res_list])
    self.assertEqual(len(res_list), 2)
    self.assertEqual(kinds, sorted(['Pod', 'Service']))

  def test_write_manifest(self):
    wiz_globals.ns = self.n2
    tec_prep.create(self.n2, simple_tec_setup())
    tec_client.tec_pod().wait_until_running()
    tec_client.write_manifest([g_rule("Pod:*")])
    file = open(tec_client.tmp_file_mame).read()
    logical = list(yaml.load_all(file, Loader=yaml.FullLoader))
    self.assertEqual(len(logical), 1)

  def test_apply(self):
    pod, svc = find_pod_svc(self.n3)
    self.assertEqual([pod, svc], [None, None])
    wiz_globals.ns = self.n3
    tec_prep.create(self.n3, simple_tec_setup())
    tec_client.tec_pod().wait_until_running()
    tec_client.apply([g_rule("*:*")])
    pod, svc = find_pod_svc(self.n3)
    self.assertIsNotNone(pod)
    self.assertIsNotNone(svc)

  def test_commit_values(self):
    create_base_master_map(self.n4)
    wiz_globals.ns = self.n4
    tec_client.commit_values([('foo', 'bar')])
    new_values = tec_client.master_map().json('master')
    self.assertEqual(new_values, dict(foo='bar'))

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


def find_pod_svc(ns):
  return [KatPod.find(ns, 'pod'), KatSvc.find(ns, 'service')]

import yaml

from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.res.svc.kat_svc import KatSvc
from k8_kat.utils.testing import ns_factory
from nectwiz.core import tami_client
from nectwiz.model.base.res_match_rule import ResMatchRule
from nectwiz.core.tami_client import deep_set, filter_res
from nectwiz.core.wiz_app import wiz_app
from nectwiz.tests.t_helpers.cluster_test import ClusterTest
from nectwiz.tests.t_helpers import helper


class TestTamiClient(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)
    helper.create_base_master_map(self.ns)

  def tearDown(self) -> None:
    super().tearDown()
    ns_factory.relinquish(self.ns)

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

  def test_fmt_inline_assigns(self):
    str_assignments = [('foo.bar', 'baz'), ('x', 'y')]
    actual = tami_client.fmt_inline_assigns(str_assignments)
    self.assertEqual(actual, "--set foo.bar=baz --set x=y")

  def test_filter_res(self):
    res_list = g_res_list(('k1', 'n1'), ('k1', 'n2'))
    result = filter_res(res_list, [g_rule("k1:n1")])
    self.assertEqual(result, [res_list[0]])

  def test_load_raw_manifest(self):
    res_list = tami_client.load_raw_manifest()
    kinds = sorted([r['kind'] for r in res_list])
    self.assertEqual(len(res_list), 2)
    self.assertEqual(kinds, sorted(['Pod', 'Service']))

  def test_load_raw_manifest_with_inlines(self):
    res_list = tami_client.load_raw_manifest([('service.name', 'inline')])
    print(res_list)
    svc = [r for r in res_list if r['kind'] == 'Service'][0]
    self.assertEqual(svc['metadata']['name'], 'inline')

  def test_write_manifest(self):
    tami_client.write_manifest([g_rule("Pod:*")])
    with open(tami_client.tmp_file_mame) as file:
      logical = list(yaml.load_all(file.read(), Loader=yaml.FullLoader))
      self.assertEqual(len(logical), 1)

  def test_apply(self):
    pod, svc = find_pod_svc(self.ns)
    self.assertEqual([pod, svc], [None, None])
    tami_client.apply([g_rule("*:*")], [('namespace', self.ns)])
    pod, svc = find_pod_svc(self.ns)
    self.assertIsNotNone(pod)
    self.assertIsNotNone(svc)

  def test_commit_values(self):
    tami_client.commit_values([('foo', 'bar')])
    new_values = tami_client.master_cmap().yget()
    self.assertEqual(new_values, dict(foo='bar'))

  def test_commit_and_load(self):
    wiz_app.ns = self.ns
    tami_client.commit_values([
      ('namespace', self.ns),
      ('service.name', 'updated-service'),
      ('service.port', 81)
    ])
    new_res = tami_client.load_raw_manifest()
    svc = [r for r in new_res if r['kind'] == 'Service'][0]
    self.assertEqual(svc['metadata']['name'], 'updated-service')
    # noinspection PyTypeChecker,PyTypedDict
    self.assertEqual(svc['spec']['ports'][0]['port'], 81)
    self.assertIsNotNone(svc)

  def test_integration(self):
    tami_client.commit_values([
      ('namespace', self.ns),
      ('service.name', 'updated-service'),
      ('service.port', 81)
    ])
    tami_client.write_manifest([])
    tami_client.kubectl_apply()
    svc = KatSvc.find('updated-service', self.ns)
    self.assertIsNotNone(svc)
    self.assertEqual(svc.from_port, 81)


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
  return [KatPod.find('pod', ns), KatSvc.find('service', ns)]

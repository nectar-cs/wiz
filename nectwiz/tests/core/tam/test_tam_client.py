import yaml
from k8kat.utils.testing import ns_factory

from nectwiz.core.tam import tam_client
from nectwiz.model.base.res_match_rule import ResMatchRule
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestTamiClient(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)
    helper.create_base_master_map(self.ns)

  def tearDown(self) -> None:
    super().tearDown()
    ns_factory.relinquish(self.ns)

  # def test_write_manifest(self):
  #   tam_client.save_manifest_as_tmp([ResMatchRule("Pod:*")], [])
  #   with open(tam_client.tmp_file_mame) as file:
  #     logical = list(yaml.load_all(file.read(), Loader=yaml.FullLoader))
  #     self.assertEqual(len(logical), 1)

  def test_fmt_inline_assigns(self):
    str_assignments = [('foo.bar', 'baz'), ('x', 'y')]
    actual = tam_client.fmt_inline_assigns(str_assignments)
    self.assertEqual(actual, "--set foo.bar=baz --set x=y")

  def test_filter_res(self):
    res_list = g_res_list(('k1', 'n1'), ('k1', 'n2'))
    result = tam_client.filter_res(res_list, [ResMatchRule("k1:n1")])
    self.assertEqual(result, [res_list[0]])

  # def test_apply(self):
  #   pod, svc = find_pod_svc(self.ns)
  #   self.assertEqual([pod, svc], [None, None])
  #   tami_client.apply([g_rule("*:*")], [('namespace', self.ns)])
  #   pod, svc = find_pod_svc(self.ns)
  #   self.assertIsNotNone(pod)
  #   self.assertIsNotNone(svc)

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

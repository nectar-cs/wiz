import os

import yaml
from k8kat.utils.testing import ns_factory

from nectwiz.core.tam import tam_client
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.model.base.resource_selector import ResourceSelector
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestTamClient(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)
    helper.create_base_master_map(self.ns)
    if os.path.isfile(tam_client.tmp_file_mame):
      os.remove(tam_client.tmp_file_mame)

  def tearDown(self) -> None:
    super().tearDown()
    ns_factory.relinquish(self.ns)

  def test_kubectl_apply(self):
    outcomes = TamClient.kubectl_apply([
      good_res(self.ns, '1'),
      bad_res(self.ns, '1')
    ])
    self.assertEqual(2, len(outcomes))
    o1, o2 = outcomes
    self.assertEqual('', o1['api_group'])
    self.assertEqual('', o2['api_group'])

    self.assertEqual('configmap', o1['kind'])
    self.assertEqual('configmaps', o2['kind'])

    self.assertEqual('good-1', o1['name'])
    self.assertEqual('bad-1', o2['name'])

    self.assertEqual('created', o1['verb'])
    self.assertIsNone(o2['verb'])

    self.assertIsNone(o1['error'])
    self.assertIsNotNone(o2['error'])

  def test_short_lived_resfile(self):
    self.assertFalse(os.path.isfile(tam_client.tmp_file_mame))
    with tam_client.short_lived_resfile(dict(foo='bar')):
      with open(tam_client.tmp_file_mame) as file:
        loaded = yaml.load(file.read())
        self.assertEqual(dict(foo='bar'), loaded)

  def test_fmt_inline_assigns(self):
    str_assignments = [('foo.bar', 'baz'), ('x', 'y')]
    actual = tam_client.fmt_inline_assigns(str_assignments)
    self.assertEqual(actual, "--set foo.bar=baz --set x=y")

  def test_filter_res(self):
    res_list = g_res_list(('k1', 'n1'), ('k1', 'n2'))
    selector = ResourceSelector.inflate("k1:n1")
    result = TamClient.filter_res(res_list, [selector])
    self.assertEqual(result, [res_list[0]])

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


good_res = lambda ns, ind: dict(
  apiVersion='v1',
  kind='ConfigMap',
  metadata=dict(namespace=ns, name=f'good-{ind}'),
  data={}
)

bad_res = lambda ns, ind: dict(
  apiVersion='v1',
  kind='ConfigMap',
  metadata=dict(namespace=ns, name=f'bad-{ind}'),
  data='a-wrong-datatype'
)

from k8kat.utils.testing import ns_factory

from nectwiz.core import config_man
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class Base:
  class TestTamSuper(ClusterTest):

    def client_instance(self) -> TamClient:
      raise RuntimeError

    def setUp(self) -> None:
      super().setUp()
      self.ns, = ns_factory.request(1)
      helper.mock_globals(self.ns)
      helper.create_base_master_map(self.ns)

    def tearDown(self) -> None:
      super().tearDown()
      ns_factory.relinquish(self.ns)

    def test_load_manifest_defaults(self):
      values = self.client_instance().load_manifest_defaults()
      self.assertEqual(exp_default_values, values)

    def test_load_tpd_manifest(self):
      config_man.commit_keyed_tam_assigns(self.mock_tam_vars())
      inlines = [('service.name', 'inline')]
      result = self.client_instance().load_tpd_manifest(inlines)

      kinds = sorted([r['kind'] for r in result])
      svc = [r for r in result if r['kind'] == 'Service'][0]
      pod = [r for r in result if r['kind'] == 'Pod'][0]

      self.assertEqual(len(result), 2)
      self.assertEqual(kinds, sorted(['Pod', 'Service']))
      self.assertEqual(svc['metadata']['name'], 'inline')
      self.assertEqual(pod['metadata']['name'], 'updated-pod')

    def mock_tam_vars(self):
      return [
        ('namespace', self.ns),
        ('pod.name', 'updated-pod'),
        ('service.port', 81)
      ]


exp_default_values = {
  'namespace': 'default',
  'service': {
    'name': 'service',
    'port': 80
  },
  'pod': {
    'name': 'pod',
    'image': 'nginx'
  }
}

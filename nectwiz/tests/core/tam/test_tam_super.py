import time

from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
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
      time.sleep(3)
      values = self.client_instance().load_default_values()
      self.assertEqual(exp_default_values, values)

    def test_load_tpd_manifest(self):
      time.sleep(3)
      config_man.patch_manifest_vars(manifest_vars)
      result = self.client_instance().template_manifest(flat_inlines)

      kinds = sorted([r['kind'] for r in result])
      svc = [r for r in result if r['kind'] == 'Service'][0]
      pod = [r for r in result if r['kind'] == 'Pod'][0]

      self.assertEqual(len(result), 2)
      self.assertEqual(sorted(['Pod', 'Service']), kinds)
      self.assertEqual('inline', svc['metadata']['name'])
      self.assertEqual('updated-pod', pod['metadata']['name'])


manifest_vars = {
  'pod': {
    'name': 'updated-pod',
  },
  'service': {
    'port': 81
  }
}


flat_inlines = {
  'service.name': 'inline'
}


exp_default_values = {
  'service': {
    'name': 'service',
    'port': 80
  },
  'pod': {
    'name': 'pod',
    'image': 'nginx'
  }
}

from k8_kat.utils.testing import ns_factory

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

    def test_load_templated_man_simple(self):
      res_list = self.client_instance().load_tpd_manifest()
      kinds = sorted([r['kind'] for r in res_list])
      self.assertEqual(len(res_list), 2)
      self.assertEqual(kinds, sorted(['Pod', 'Service']))

    def test_load_templated_man_with_inlines(self):
      inlines = [('service.name', 'inline')]
      res_list = self.client_instance().load_tpd_manifest(inlines)
      print(res_list)
      svc = [r for r in res_list if r['kind'] == 'Service'][0]
      self.assertEqual(svc['metadata']['name'], 'inline')

    def mock_tam_commit(self):
      return {
        'namespace': self.ns,
        'service.name': 'updated-service',
        'service.port': 81
      }

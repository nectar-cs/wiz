import yaml
from k8_kat.utils.testing import ns_factory

from wiz.core import tami_prep
from wiz.tests.t_helpers.cluster_test import ClusterTest
from wiz.tests.t_helpers.helper import create_base_master_map, ci_tami_name


class TestTecPrep(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestTecPrep, cls).setUpClass()
    cls.ns, = ns_factory.request(1)

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()
    pass

  def test_consume(self):
    create_base_master_map(self.ns)
    output = tami_prep.consume(self.ns, ci_tami_name(), [])
    self.assertIsNotNone(output)
    res_dicts = list(yaml.load_all(output, yaml.FullLoader))
    self.assertEqual(2, len(res_dicts))

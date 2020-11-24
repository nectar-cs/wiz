import yaml
from k8kat.utils.testing import ns_factory

from nectwiz.core.tam import tami_prep
from nectwiz.tests.t_helpers.cluster_test import ClusterTest
from nectwiz.tests.t_helpers.helper import create_base_master_map, ci_tami_name


class TestTamiPrep(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestTamiPrep, cls).setUpClass()
    cls.ns, = ns_factory.request(1)

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()
    pass

  def test_consume_no_values(self):
    create_base_master_map(self.ns)
    output = tami_prep.consume(
      ns=self.ns,
      image=f"{ci_tami_name()}:1.0.0",
      arglist=['template', 'foo', '.']
    )
    self.assertIsNotNone(output)
    res_dicts = list(yaml.load_all(output, yaml.FullLoader))
    self.assertEqual(2, len(res_dicts))

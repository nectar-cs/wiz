from k8_kat.utils.testing import ns_factory

from nectwiz.core import variables_man
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestVariablesMan(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)
    helper.create_base_master_map(self.ns)

  def tearDown(self) -> None:
    super().tearDown()
    ns_factory.relinquish(self.ns)

def test_commit_values(self):
    variables_man.commit_values([('foo', 'bar')])
    new_values = variables_man.master_cmap().yget()
    self.assertEqual(new_values, dict(foo='bar'))

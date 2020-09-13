from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
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

  def test_commit_tam_assigns(self):
    assignments = dict(foo=dict(bar='baz'))
    config_man.commit_mfst_vars(assignments)
    self.assertEqual(assignments, config_man.read_mfst_vars())

    config_man.commit_mfst_vars(dict(bar='baz'))
    expectation = dict(bar='baz', foo=dict(bar='baz'))
    self.assertEqual(expectation, config_man.read_mfst_vars())

    config_man.commit_mfst_vars(dict(foo=dict(baz='bar')))
    expectation = dict(bar='baz', foo=dict(bar='baz', baz='bar'))
    self.assertEqual(expectation, config_man.read_mfst_vars())

  def test_commit_keyed_tam_assigns(self):
    expectation = dict(foo=dict(bar='baz'))
    config_man.commit_keyed_mfst_vars([('foo.bar', 'baz')])
    self.assertEqual(expectation, config_man.read_mfst_vars())

    config_man.commit_keyed_mfst_vars([('bar', 'baz')])
    expectation = dict(bar='baz', foo=dict(bar='baz'))
    self.assertEqual(expectation, config_man.read_mfst_vars())

    config_man.commit_keyed_mfst_vars([('foo.baz', 'bar')])
    expectation = dict(bar='baz', foo=dict(bar='baz', baz='bar'))
    self.assertEqual(expectation, config_man.read_mfst_vars())

import subprocess

from tests.test_helpers.cluster_test import ClusterTest
from wiz.core import wiz_globals as wg_module
from wiz.core.wiz_globals import wiz_globals


class TestWizGlobals(ClusterTest):


  def setUp(self) -> None:
    super().setUp()
    wg_module.clear_cache()

  def test_read_ns_and_app(self):
    result = wg_module.read_ns_and_app()
    self.assertEqual(result, [None, None])

  def test_persist_ns_and_app(self):
    wg_module.persist_ns_and_app('foo', dict(foo='bar'))
    ns, app = wg_module.read_ns_and_app()
    self.assertEqual(ns, 'foo')
    self.assertEqual(app, dict(foo='bar'))

  def test_init(self):
    wg_module.persist_ns_and_app('foo', dict(foo='bar'))
    self.assertEqual(wiz_globals.ns, 'foo')
    self.assertEqual(wiz_globals.app, dict(foo='bar'))

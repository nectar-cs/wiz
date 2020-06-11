from wiz.core import wiz_globals as wg_module
from wiz.core.wiz_globals import wiz_app
from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestWizGlobals(ClusterTest):


  def setUp(self) -> None:
    super().setUp()
    wg_module.clear_cache()
    wg_module.wiz_app.ns_overwrite = None
    wg_module.wiz_app.app_overwrite = None

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
    self.assertEqual(wiz_app.ns, 'foo')
    self.assertEqual(wiz_app.app(), dict(foo='bar'))

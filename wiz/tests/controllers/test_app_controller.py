import json

from k8_kat.tests.res.common import test_kat_quota
from k8_kat.utils.testing import ns_factory
from wiz.core import wiz_globals
from wiz.core.wiz_globals import wiz_app
from wiz.server import app
from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestAppController(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    wiz_globals.clear_cache()
    wiz_app.app_overwrite = None
    wiz_app.ns_overwrite, = ns_factory.request(1)

  def test_limits_and_usage_with_adapter(self):
    test_kat_quota.create('app-quota', wiz_app.ns)
    response = app.test_client().get('/api/app/resource-stats')
    data = json.loads(response.data).get('data')
    self.assertIsNotNone(data)

  def test_tedi_prep(self):
    wiz_app.ns_overwrite = None
    wiz_globals.clear_cache()
    ns, = ns_factory.request(1)

    payload = dict(app=dict(foo='bar'), ns=ns)
    response = app.test_client().post('/api/app/prepare', json=payload)
    status = json.loads(response.data).get('status')

    self.assertEqual('success', status)
    self.assertEqual(dict(foo='bar'), wiz_app.app())
    self.assertEqual(ns, wiz_app.ns)

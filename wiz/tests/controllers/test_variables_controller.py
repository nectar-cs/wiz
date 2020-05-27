import json

from wiz.core.wiz_globals import wiz_app
from wiz.server import app
from wiz.tests.models.helpers import g_conf
from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestVariablesController(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    wiz_app.clear()

  def test_index(self):
    wiz_app.add_configs([
      g_conf(i='ChartVariable', k='cv1'),
      g_conf(i='ChartVariable', k='cv2')
    ])

    response = app.test_client().get('/api/chart-variables')
    body = json.loads(response.data).get('data')

    self.assertEqual(2, len(body))

  def test_show(self):
    wiz_app.add_configs([g_conf(i='ChartVariable', k='cv1')])
    response = app.test_client().get('/api/chart-variables/cv1')
    body = json.loads(response.data).get('data')
    self.assertEqual('cv1', body['id'])
    self.assertEqual(True, body['is_safe_to_set'])
    self.assertEqual([], body['operations'])
    self.assertIn('field', body.keys())

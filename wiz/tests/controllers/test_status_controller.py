import json

from wiz.server import app
from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestStatusController(ClusterTest):

  def test_ping(self):
    response = app.test_client().get('/api/ping')
    body = json.loads(response.data)
    self.assertEqual(body, dict(ping='pong'))

  def test_status(self):
    response = app.test_client().get('/api/status')
    ret_data = json.loads(response.data)
    self.assertIsNotNone(ret_data)

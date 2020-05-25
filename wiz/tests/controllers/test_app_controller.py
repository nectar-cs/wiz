import json

from wiz.server import app
from wiz.tests.models.helpers import g_con_conf
from wiz.tests.t_helpers.cluster_test import ClusterTest
from wiz.core.wiz_globals import wiz_globals as wg


class TestAppController(ClusterTest):

  def test_operations_index_empty(self):
    response = app.test_client().get('/api/app/operations')
    body = json.loads(response.data)
    self.assertEqual(body, dict(data=[]))

  def test_operations_index_with_data(self):
    configs = [g_con_conf(k='foo', t='Foo', d='Bar', s=['s1', 's2'])]
    wg.set_configs(operations=configs, install_stages=configs)

    response1 = app.test_client().get('/api/app/operations')
    body1 = json.loads(response1.data).get('data')

    response2 = app.test_client().get('/api/app/install_stages')
    body2 = json.loads(response2.data).get('data')

    expected = dict(
      id='foo',
      title='Foo',
      description='Bar',
      first_step_id='s1'
    )

    self.assertEqual([expected], body1)
    self.assertEqual([expected], body2)

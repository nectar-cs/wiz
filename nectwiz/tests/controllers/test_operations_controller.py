import json

from nectwiz.model.base.wiz_model import models_man
from nectwiz.server import app
from nectwiz.tests.models.helpers import g_conf
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestOperationsController(ClusterTest):

  def setUp(self) -> None:
    models_man.clear()

  def test_operations_index(self):
    config = g_conf(k='foo', t='Foo', i='Operation')
    models_man.add_descriptors([config])

    response = app.test_client().get('/api/operations')
    body = json.loads(response.data).get('data')

    self.assertEqual(1, len(body))
    self.assertEqual('foo', body[0].get('id'))
    self.assertEqual('Foo', body[0].get('title'))

  # def test_steps_show(self):
  #   wg.add_configs(basic_operation())
  #
  #   response = app.test_client().get('/api/operations/o1/stages/g1/steps/s1')
  #   body = json.loads(response.data)['data']
  #   self.assertEqual(body['id'], 's1')
  #   self.assertEqual(len(body['fields']), 1)
  #   self.assertEqual(body['fields'][0]['id'], 'f1')

  def test_fields_validate(self):
    models_man.add_descriptors(basic_operation())

    endpoint = '/api/operations/o1/stages/g1/steps/s1/fields/f1/validate'
    response = app.test_client().post(endpoint, json=dict(value='bar'))
    body = json.loads(response.data)['data']
    self.assertEqual(body, dict(status='valid'))

  def test_step_next_simple(self):
    endpoint = '/api/operations/o1/stages/g1/steps/s1/next'
    models_man.add_descriptors([
      g_conf(k='o1', stages=['g1'], i='Operation'),
      g_conf(k='g1', steps=['s1', 's2'], i='Stage'),
      g_conf(k='s1', fields=['f1'], i='Step', next='bar'),
    ])

    response = app.test_client().post(endpoint, json=dict(values={}))
    body = json.loads(response.data)
    self.assertEqual('bar', body.get('step_id'))


def basic_operation():
  return [
    g_conf(k='o1', stages=['g1'], i='Operation'),
    g_conf(k='g1', steps=['s1', 's2'], i='Stage'),
    g_conf(k='s1', fields=['f1'], i='Step'),
    g_conf(k='f1', i='Field')
  ]

import json

from wiz.core.wiz_globals import wiz_globals as wg
from wiz.server import app
from wiz.tests.models.helpers import g_con_conf, g_conf
from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestOperationsController(ClusterTest):

  def setUp(self) -> None:
    wg.clear()

  def test_steps_show_when_exists(self):
    wg.add_configs(
      operations=[g_con_conf(k='c1', s=['s1', 's2'])],
      steps=[g_conf(k='s1', t='Foo', fields=['f1'])],
      fields=[
        dict(
          key='f1',
          title='Bar',
          type='choice',
          info='Inf',
          options=[
            dict(key='x', value='y')
          ])
      ]
    )

    response = app.test_client().get('/api/operations/c1/steps/s1')
    body = json.loads(response.data)['data']
    self.assertEqual(body['id'], 's1')
    self.assertEqual(body['title'], 'Foo')
    self.assertEqual(len(body['fields']), 1)
    self.assertEqual(body['fields'][0]['id'], 'f1')

  def test_fields_validate_when_valid(self):
    wg.add_configs(
      operations=[g_con_conf(k='c1', s=['s1'])],
      steps=[g_conf(k='s1', t='Foo', fields=['f1'])],
      fields=[g_field(k='f1', c='foo')]
    )

    endpoint = '/api/operations/c1/steps/s1/fields/f1/validate'
    response = app.test_client().post(endpoint, json=dict(value='bar'))
    body = json.loads(response.data)['data']
    self.assertEqual(body, dict(status='valid'))

  def test_fields_validate_when_not_valid(self):
      wg.add_configs(
        operations=[g_con_conf(k='c1', s=['s1'])],
        steps=[g_conf(k='s1', t='Foo', fields=['f1'])],
        fields=[g_field(k='f1', c='foo', t='warning', m='bar')]
      )

      endpoint = '/api/operations/c1/steps/s1/fields/f1/validate'
      body = dict(value='foo')
      response = app.test_client().post(endpoint, json=body)
      body = json.loads(response.data)['data']
      self.assertEqual(body, dict(status='warning', message='bar'))

  def test_step_next_simple(self):
    wg.add_configs(
      operations=[g_con_conf(k='c1', s=['s1'])],
      steps=[g_conf(k='s1', next='foo-baz')]
    )

    endpoint = '/api/operations/c1/steps/s1/next'
    response = app.test_client().post(endpoint, json=dict(values={}))
    body = json.loads(response.data)['step_id']
    self.assertEqual(body, 'foo-baz')


def g_field(k='f', c='Check', m='Message', t='warning'):
  return dict(
    key=k,
    validations=[
      dict(
        type='equality',
        check_against=c,
        message=m,
        tone=t
      )
    ]
  )

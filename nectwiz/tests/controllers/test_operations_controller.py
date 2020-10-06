import json
from typing import Dict, Any

from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.operation.operation import Operation
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.predicate.format_predicate import FormatPredicate
from nectwiz.model.variable.variable_value_decorator import VariableValueDecorator
from nectwiz.server import app
from nectwiz.tests.models.helpers import g_conf
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestOperationsController(ClusterTest):

  def setUp(self) -> None:
    models_man.clear(restore_defaults=True)
    models_man.add_descriptors([basic_operation_config])
    models_man.add_classes([SimpleDecorator])
    OperationState.clear_list()

    endpoint = f'{operation_path}/generate-ost'
    response = app.test_client().post(endpoint)
    self.ost = json.loads(response.data)['data']

  def test_operations_index(self):
    config = g_conf(k='foo', t='Foo', i='Operation')
    models_man.add_descriptors([config])

    response = app.test_client().get('/api/operations')
    self.assertEqual(200, response.status_code)

  def test_step_refresh(self):
    endpoint = f'{steps_path}/step-1/refresh'

    payload = dict(values={'field-1.1': 'off'})
    response = self.http_post(endpoint, json=payload)
    body = json.loads(response.data)['data']
    step_part, assigns_part = body.get('step'), body.get('manifest_assignments')
    f1 = step_part['fields'][0]
    self.assertEqual(1, len(step_part['fields']))
    self.assertEqual("it's decorated-off", f1.get('decorated_value'))
    self.assertEqual('off', assigns_part['field-1.1'])

    payload = dict(values={'field-1.1': 'on'})
    response = self.http_post(endpoint, json=payload)
    body = json.loads(response.data)['data']
    step_part, assigns_part = body.get('step'), body.get('manifest_assignments')
    f1 = step_part['fields'][0]
    self.assertEqual(2, len(step_part['fields']))
    self.assertEqual("it's decorated-on", f1.get('decorated_value'))
    self.assertEqual('on', assigns_part['field-1.1'])

  def test_fields_validate(self):
    endpoint = f'{steps_path}/step-1/fields/field-1.1/validate'

    response = self.http_post(endpoint, json=dict(value='bar'))
    body = json.loads(response.data)['data']
    self.assertEqual('error', body['status'])

    response = self.http_post(endpoint, json=dict(value='bar@bar.com'))
    body = json.loads(response.data)['data']
    self.assertEqual('valid', body['status'])

  def http_post(self, *args, **kwargs):
    headers = {'Ostid': self.ost}
    return app.test_client().post(*args, **kwargs, headers=headers)


operation_path = '/api/operations/unittest'
stage_path = f'{operation_path}/stages/stage-1'
steps_path = f'{stage_path}/steps'


class SimpleDecorator(VariableValueDecorator):
  def compute(self, value: Any, operation_state: OperationState) -> Dict:
    return {'foo': f"decorated-{value}"}


basic_operation_config = dict(
  kind=Operation.__name__,
  id='unittest',
  stages=[
    dict(
      id='stage-1',
      steps=[
        dict(
          id='step-1',
          fields=[
            dict(
              id='field-1.1',
              validation=[
                dict(
                  kind=FormatPredicate.__name__,
                  check_against='email'
                )
              ],
              value_decorator=dict(
                kind=SimpleDecorator.__name__,
                template="it's {foo}"
              )
            ),
            dict(
              id='field-1.2',
              show_condition=dict(
                challenge='{field-1.1}',
                check_against='on'
              )
            )
          ]
        ),
        dict(
          id='step-2'
        )
      ]
    )
  ]
)

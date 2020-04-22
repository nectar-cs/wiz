import base64
import json
import unittest

from tests.models.helpers import g_conf, g_con_conf
from wiz.core.wiz_globals import wiz_globals as wg
from wiz.server import app


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

def state_head(original_payload):
  message = json.dumps(original_payload)
  message_bytes = message.encode('ascii')
  base64_bytes = base64.b64encode(message_bytes)
  base64_message = base64_bytes.decode('ascii')
  return {'step_state': base64_message}


class TestConcern(unittest.TestCase):

  def setUp(self) -> None:
    wg.clear()


  def test_concerns_index_empty(self):
    response = app.test_client().get('/api/concerns')
    body = json.loads(response.data)
    self.assertEqual(body, dict(data=[]))


  def test_concerns_index_with_data(self):
    wg.set_configs(concerns=[g_con_conf(k='foo', t='Foo', d='Bar', s=['s1', 's2'])])
    response = app.test_client().get('/api/concerns')
    body = json.loads(response.data)
    self.assertEqual(body, dict(
      data=[
        dict(
          id='foo',
          title='Foo',
          description='Bar',
          first_step_id='s1'
        )]))


  def test_steps_show_when_exists(self):
    wg.set_configs(
      concerns=[g_con_conf(k='c1', s=['s1', 's2'])],
      steps=[g_conf(k='s1', t='Foo')]
    )

    response = app.test_client().get('/api/concerns/c1/steps/s1')
    body = json.loads(response.data)
    self.assertEqual(body, dict(
      data=dict(
        id='s1',
        title='Foo'
      )))


  def test_fields_validate_when_nothing(self):
    wg.set_configs(
      concerns=[g_con_conf(k='c1', s=['s1'])],
      steps=[g_conf(k='s1', t='Foo', fields=['f1'])],
      fields=[g_field(k='f1', c='foo')]
    )

    endpoint = '/api/concerns/c1/steps/s1/fields/f1/validate'
    state = dict(f1='bar')
    response = app.test_client().post(endpoint, headers=state_head(state))
    body = json.loads(response.data)['data']
    self.assertEqual(body, dict(status='valid'))


  def test_state_header(self):
    payload = dict(data='ping')
    headers = state_head(payload)

    with app.test_client() as client:
      response = client.get('/api/concerns-echo-state',headers=headers)
      out = json.loads(response.data)
      self.assertEqual(out, dict(pong=payload))


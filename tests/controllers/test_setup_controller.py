import base64
import json
import unittest

from tests.models.helpers import g_conf, g_con_conf
from wiz.core.wiz_globals import wiz_globals as wg
from wiz.server import app


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

  def test_state_header(self):
    message = json.dumps(dict(data='ping'))

    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    headers = {'step_state': base64_message}

    with app.test_client() as client:
      response = client.get('/api/concerns-ping-state',headers=headers)
      print(response.data)



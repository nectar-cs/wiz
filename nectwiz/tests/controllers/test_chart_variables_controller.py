import json

from k8kat.utils.testing import ns_factory

from nectwiz.core.core.config_man import config_man
from nectwiz.server import app
from nectwiz.tests.models.helpers import g_conf
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestChartVariablesController(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    wiz_app.clear()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)

  # def test_submit(self):
  #   helper.foo_bar_setup(self.ns)
  #   wiz_app.add_configs([g_conf(i='ChartVariable', k='foo')])
  #   self.assertEqual('bar', ChartVariable.inflate('foo').read_crt_value())
  #
  #   endpoint = '/api/chart-variables/foo/submit'
  #   payload = dict(value='baz')
  #   response = app.test_client().post(endpoint, json=payload)
  #
  #   self.assertEqual('success', json.loads(response.data).get('status'))
  #   self.assertEqual('baz', ChartVariable.inflate('foo').read_crt_value())

  def test_validate(self):
    wiz_app.add_configs([dict(
      kind='ChartVariable',
      id='foo',
      field=dict(id='f')
    )])

    endpoint = '/api/chart-variables/foo/validate'
    response = app.test_client().post(endpoint, json=dict(value=''))
    body = json.loads(response.data).get('data')
    self.assertEqual('error', body.get('status'))
    self.assertEqual('Cannot be empty', body.get('message'))

    response2 = app.test_client().post(endpoint, json=dict(value='bar'))
    body2 = json.loads(response2.data).get('data')
    self.assertEqual('valid', body2.get('status'))

  def test_index(self):
    helper.foo_bar_setup(self.ns)
    
    wiz_app.add_configs([
      dict(kind='ChartVariable', id='foo'), 
      dict(kind='ChartVariable', id='bar.foo')
    ])

    response = app.test_client().get('/api/chart-variables')
    cv1, cv2 = body = json.loads(response.data).get('data')
    self.assertEqual(2, len(body))
    self.assertEqual('foo', cv1.get('id'))
    self.assertEqual('bar', cv1.get('value'))
    self.assertEqual('bar.foo', cv2.get('id'))
    self.assertEqual('baz', cv2.get('value'))

  # def test_show_no_field(self):
  #   helper.foo_bar_setup(self.ns)
  #   wiz_app.add_configs([g_conf(i='ChartVariable', k='foo')])
  #
  #   response1 = app.test_client().get('/api/chart-variables/foo')
  #   cv1 = json.loads(response1.data).get('data')
  #
  #   self.assertEqual([], cv1['operations'])
  #   self.assertIsNone(cv1['field'])

  def test_show_with_field(self):
    helper.foo_bar_setup(self.ns)
    field_options = [dict(id='key', value='value')]

    wiz_app.add_configs([dict(
      kind='ChartVariable',
      id='bar.foo',
      field=dict(
        id='f1',
        type='select',
        options=field_options
      )
    )])

    response = app.test_client().get('/api/chart-variables/bar.foo')
    cv = json.loads(response.data).get('data')

    self.assertEqual('select', cv['field'].get('type'))
    self.assertEqual(field_options, cv['field'].get('options'))

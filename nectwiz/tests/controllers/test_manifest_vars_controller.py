import json

from k8kat.utils.testing import ns_factory

from nectwiz.model.base.wiz_model import models_man
from nectwiz.model.input.select_input import SelectInput
from nectwiz.model.variables.manifest_variable import ManifestVariable
from nectwiz.server import app
from nectwiz.tests.t_helpers import helper
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestManifestVariablesController(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    models_man.clear()
    self.ns, = ns_factory.request(1)
    helper.mock_globals(self.ns)

  def test_show(self):
    endpoint = '/api/manifest-variables/foo'
    models_man.add_descriptors([
      dict(
        kind=ManifestVariable.__name__,
        id='foo',
        input=dict(
          kind=SelectInput.__name__,
          options=dict(x='X', y='Y')
        )
      )
    ])

    response = app.test_client().get(endpoint)
    body = json.loads(response.data).get('data')

    exp_opts = [dict(id='x', title='X'), dict(id='y', title='Y')]
    self.assertEqual('foo', body.get('id'))
    self.assertEqual(SelectInput.__name__, body.get('type'))
    self.assertEqual(exp_opts, body.get('options'))

  def test_validate(self):
    endpoint = '/api/manifest-variables/foo/validate'
    models_man.add_descriptors([
      dict(
        kind=ManifestVariable.__name__,
        id='foo',
        validation=[
          dict(
            operator='presence',
            reason='Cannot be empty'
          )
        ]
      )
    ])

    response = app.test_client().post(endpoint, json=dict(value=''))
    body = json.loads(response.data).get('data')
    self.assertEqual('error', body.get('status'))
    self.assertEqual('Cannot be empty', body.get('message'))

    response2 = app.test_client().post(endpoint, json=dict(value='bar'))
    body2 = json.loads(response2.data).get('data')
    self.assertEqual('valid', body2.get('status'))

  def test_index(self):
    helper.foo_bar_setup(self.ns)
    
    models_man.add_descriptors([
      dict(kind=ManifestVariable.__name__, id='foo'),
      dict(kind=ManifestVariable.__name__, id='bar.foo')
    ])

    response = app.test_client().get('/api/manifest-variables')
    cv1, cv2 = body = json.loads(response.data).get('data')
    self.assertEqual(2, len(body))
    self.assertEqual('foo', cv1.get('id'))
    self.assertEqual('bar', cv1.get('value'))
    self.assertEqual('bar.foo', cv2.get('id'))
    self.assertEqual('baz', cv2.get('value'))

import json
import time

from k8_kat.utils.testing import ns_factory

from wiz.core import tedi_prep
from wiz.core.tedi_client import tedi_pod
from wiz.core.wiz_globals import wiz_globals
from wiz.server import app
from wiz.tests.t_helpers import helper
from wiz.tests.t_helpers.cluster_test import ClusterTest
from wiz.tests.t_helpers.helper import create_base_master_map


class TestStatusController(ClusterTest):
  def test_status(self):
    response = app.test_client().get('/api/status')
    ret_data = json.loads(response.data)
    self.assertIsNotNone(ret_data)

  def test_tedi_status_no_tedi(self):
    wiz_globals.ns_overwrite, = ns_factory.request(1)
    self.assertEqual('none', fetch_tedi_status())

  def test_tedi_status_with_tedi(self):
    wiz_globals.ns_overwrite, = ns, = ns_factory.request(1)
    create_base_master_map(ns)
    tedi_prep.create(ns, helper.simple_tedi_setup())
    print(fetch_tedi_status())
    self.assertTrue(fetch_tedi_status() in ['pending', 'positive', 'none'])

  def test_tedi_prep(self):
    wiz_globals.ns_overwrite, = ns, = ns_factory.request(1)
    create_base_master_map(ns)

    payload = dict(app=helper.simple_tedi_setup(), ns=ns,)
    response = app.test_client().post('/api/tedi/prepare', json=payload)
    self.assertEqual('pending', json.loads(response.data).get('status'))


def fetch_tedi_status():
  response = app.test_client().get('/api/tedi/status')
  return json.loads(response.data).get('status')

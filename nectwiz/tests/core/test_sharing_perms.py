import json
from typing import Dict

from kubernetes.client import V1ConfigMap, V1ObjectMeta

from k8_kat.auth.kube_broker import broker

from k8_kat.utils.testing import ns_factory
from nectwiz.core.telem import telem_perms
from nectwiz.core.telem.telem_perms import TelemPerms
from nectwiz.core.wiz_app import wiz_app
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestSharingPerms(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    wiz_app._ns, = ns_factory.request(1)

  def test_user_perms(self):
    self.assertEqual({}, perms_map())
    mk_map(dict(foo='bar'))
    self.assertEqual(dict(foo='bar'), perms_map())

  def test_can_upload_telem(self):
    self.assertFalse(TelemPerms().can_sync_telem())
    mk_map({telem_perms.upload_telem_key: True})
    self.assertTrue(TelemPerms().can_sync_telem())

  def test_can_share_prop(self):
    mk_map({
      'operations.metadata': True,
      'operations.assignments': 'False'
    })
    perms = TelemPerms()
    check = lambda s: perms.can_share_prop(s)
    self.assertTrue(check('operation_outcome.operation_id'))
    self.assertTrue(check('operation_outcome.step_outcomes.started_at'))
    self.assertFalse(check('operation_outcome.step_outcomes.chart_assigns'))
    self.assertFalse(check('not-real'))

def mk_map(contents: Dict):
  return broker.coreV1.create_namespaced_config_map(
    namespace=wiz_app.ns(),
    body=V1ConfigMap(
      metadata=V1ObjectMeta(name='master'),
      data={
        telem_perms.cmap_field: json.dumps(contents)
      }
    )
  )


def perms_map():
  return TelemPerms().user_perms()
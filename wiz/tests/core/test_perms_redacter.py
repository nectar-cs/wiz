import json
from typing import Dict

from kubernetes.client import V1ConfigMap, V1ObjectMeta

from k8_kat.auth.kube_broker import broker
from k8_kat.utils.testing import ns_factory
from wiz.core.telem import sharing_perms
from wiz.core.telem.perms_redactor import redact_op_outcome
from wiz.core.wiz_globals import wiz_app

from wiz.tests.t_helpers.cluster_test import ClusterTest


class TestPermsRedactor(ClusterTest):

  def setUp(self) -> None:
    super().setUp()
    wiz_app.ns, = ns_factory.request(1)

  def test_redact_op_outcome(self):
    mk_map({'operations.metadata': True})

    op_outcome = dict(
      operation_id='foo',
      step_outcomes=[
        dict(
          stage_id='bar',
          chart_assigns='should-get-redacted',
          exit_condition_outcomes=dict(
            condition_id='baz'
          )
        )
      ]
    )

    actual = redact_op_outcome(op_outcome)
    dd = actual['step_outcomes'][0]
    self.assertEqual('foo', actual['operation_id'])
    self.assertEqual('bar', dd['stage_id'])
    self.assertEqual('baz', dd['exit_condition_outcomes']['condition_id'])
    self.assertIsNone(dd['chart_assigns'])


def mk_map(contents: Dict):
  return broker.coreV1.create_namespaced_config_map(
    namespace=wiz_app.ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(name='master'),
      data={
        sharing_perms.cmap_field: json.dumps(contents)
      }
    )
  )

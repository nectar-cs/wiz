import json

import yaml

from k8_kat.auth.kube_broker import broker
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from wiz.core import tedi_client
from wiz.core.telem.ost import OperationState, StepState
from wiz.core.wiz_globals import wiz_app


def ci_tedi_name():
  return "gcr.io/nectar-bazaar/wiz-ci-tedi"


def one_step_op_state(**kwargs):
  return OperationState(step_states=[
    StepState(
      **kwargs,
      commit_outcome=dict(
        chart_assigns=kwargs.get('cass', {}),
        state_assigns=kwargs.get('sass', {})
      )
    ),
  ])


def mock_globals(ns, tedi_image=None):
  tedi_image = tedi_image or ci_tedi_name()
  if ns:
    wiz_app.ns = ns
  if tedi_image:
    wiz_app.tedi_image = tedi_image


def create_base_master_map(ns):
  broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(
        namespace=ns,
        name='master'
      ),
      data=dict(master=yaml.dump({}))
    )
  )


def foo_bar_setup(ns):
  create_base_master_map(ns)
  tedi_client.commit_values([
    ('foo', 'bar'),
    ('bar.foo', 'baz')
  ])

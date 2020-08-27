import json

import yaml

from k8_kat.auth.kube_broker import broker
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from nectwiz.core import config_man
from nectwiz.core.tam import tami_client
from nectwiz.core.telem.ost import OperationState, StepState
from nectwiz.core.wiz_app import wiz_app


def ci_tami_name():
  return "gcr.io/nectar-bazaar/wiz-ci-tami"


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


def mock_globals(ns, tami_image=None):
  tami_image = tami_image or ci_tami_name()
  if ns:
    wiz_app._ns = ns
  if tami_image:
    wiz_app.tam_uri = tami_image


def create_base_master_map(ns):
  broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(
        namespace=ns,
        name='master'
      ),
      data={
        config_man.tam_config_key: json.dumps({}),
        config_man.tam_vars_key: json.dumps({})
      }
    )
  )


def foo_bar_setup(ns):
  create_base_master_map(ns)
  config_man.commit_tam_vars({
    'foo': 'bar',
    'foo.bar': 'baz'
  })

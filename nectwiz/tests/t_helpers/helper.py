import json

from k8kat.auth.kube_broker import broker
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from nectwiz.core.core import config_man
from nectwiz.core.core.wiz_app import wiz_app
from nectwiz.model.operations.operation_state import OperationState
from nectwiz.model.step.step_state import StepState


def ci_tami_name():
  return "gcr.io/nectar-bazaar/wiz-ci-tami"


def one_step_state(step, keep=True) -> StepState:
  opstate = OperationState('123', 'abc')
  return opstate.gen_step_state(step, keep)


def mock_globals(ns):
  if ns:
    wiz_app._ns = ns
  # if tami_image:
  #   wiz_app.tam_uri = tami_image


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
  config_man.commit_keyed_tam_assigns([
    ('foo', 'bar'),
    ('bar.foo', 'baz')
  ])

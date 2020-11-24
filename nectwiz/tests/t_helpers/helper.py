import json

from k8kat.auth.kube_broker import broker
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from nectwiz.core.core.config_man import config_man, tam_config_key, tam_vars_key
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.operation.step_state import StepState


def ci_tami_name():
  return "gcr.io/nectar-bazaar/wiz-ci-tami"


def ci_tams_name():
  return "https://api.codenectar.com/manifest_servers/nectar/wiz-ci-tam"


def ci_tamle_name():
  return "wiz-ci-tam-eval"


def one_step_state(step, keep=True) -> StepState:
  op_state = OperationState('123', 'abc')
  return op_state.gen_step_state(step, keep)


def mock_globals(ns):
  if ns:
    config_man._ns = ns


def create_base_master_map(ns):
  broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(
        namespace=ns,
        name='master'
      ),
      data={
        tam_config_key: json.dumps({}),
        tam_vars_key: json.dumps({})
      }
    )
  )


def foo_bar_setup(ns):
  create_base_master_map(ns)
  config_man.patch_keyed_manifest_vars([
    ('foo', 'bar'),
    ('bar.foo', 'baz')
  ])

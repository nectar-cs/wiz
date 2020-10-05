import time

from k8kat.utils.testing import ns_factory

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import KAOs
from nectwiz.core.tam.tam_client import TamClient
from nectwiz.model.action.apply_manifest_observer import ApplyManifestObserver
from nectwiz.model.operation import status_computer
from nectwiz.model.operation.step_state import StepState
from nectwiz.model.pre_built.common_predicates import ResourcePropertyPredicate
from nectwiz.model.predicate.default_predicates import from_apply_outcome
from nectwiz.tests.t_helpers.cluster_test import ClusterTest


class TestActionObserver(ClusterTest):

  def test_check_kao_failures(self):
    observer = ApplyManifestObserver({}, fail_fast=False)
    ns, = ns_factory.request(1)
    self.assertEqual([], observer.errdicts)
    outcomes = [*good_cmap_kao(ns), *bad_cmap_kao(ns)]
    observer.check_kao_failures(outcomes)
    self.assertEqual(1, len(observer.errdicts))
    errdict = observer.errdicts[0]
    self.assertEqual('apply_manifest', errdict['event_type'])
    self.assertEqual('configmaps', errdict['resource']['kind'])
    self.assertEqual('cm-bad', errdict['resource']['name'])

  def test_on_await_cycle_done_no_errs(self):
    observer = ApplyManifestObserver({}, fail_fast=False)
    ns, = ns_factory.request(1)
    config_man._ns = ns
    outcomes = [*good_cmap_kao(ns), *bad_pod_kao(ns)]
    preds = from_apply_outcome(outcomes)
    flat_preds = utils.flatten(preds.values())
    state = StepState('synthetic', None)
    for i in range(120):
      status_computer.compute(preds, state, {})
      observer.on_await_cycle_done(flat_preds, state)
      if state.has_settled():
        break
      else:
        time.sleep(2)
    self.assertTrue(state.did_fail())
    self.assertEqual(1, len(observer.errdicts))
    errdict = observer.errdicts[0]
    exp_pred_kind = ResourcePropertyPredicate.__name__
    self.assertEqual(exp_pred_kind, errdict['predicate_kind'])
    self.assertEqual('pod', errdict['resource']['kind'])
    self.assertEqual('pod-bad', errdict['resource']['name'])


def good_cmap_kao(ns: str) -> KAOs:
  return TamClient({}).kubectl_apply([
    dict(
      apiVersion='v1',
      kind='ConfigMap',
      metadata=dict(name='cm-good', namespace=ns),
      data={}
    )
  ])

def bad_cmap_kao(ns: str) -> KAOs:
  return TamClient({}).kubectl_apply([
    dict(
      apiVersion='v1',
      kind='ConfigMap',
      metadata=dict(name='cm-bad', namespace=ns),
      data='wrong-format'
    )
  ])

def bad_pod_kao(ns: str) -> KAOs:
  return TamClient({}).kubectl_apply([
    dict(
      apiVersion='v1',
      kind='Pod',
      metadata=dict(name='pod-bad', namespace=ns),
      spec=dict(
        containers=[
          dict(
            name='main',
            image=f"not-an-image-{utils.rand_str(10)}"
          )
        ]
      )
    )
  ])

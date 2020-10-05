import time
from typing import Dict, Optional

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import StepActionKwargs, TamDict
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.action.action import Action
from nectwiz.model.action.apply_manifest_observer import ApplyManifestObserver
from nectwiz.model.operation import status_computer
from nectwiz.model.operation.step_state import StepState
from nectwiz.model.predicate.default_predicates import from_apply_outcome


class ApplyManifestAction(Action):

  def __init__(self, config):
    super().__init__(config)
    self.res_selectors = config.get('apply_filters', [])
    self.tam: Optional[TamDict] = config.get('tam')
    self.observer = ApplyManifestObserver(self.tam or config_man.tam())

  def perform(self, **kwargs: StepActionKwargs) -> Dict:
    inlines = (kwargs.get('inline') or {}).items()
    self.observer.notify_job()
    self.apply_part(inlines)
    self.await_part()
    self.observer.on_succeeded()
    return dict()

  def apply_part(self, inlines):
    client = tam_client(self.tam)
    manifestds = client.load_templated_manifest(inlines)
    self.observer.on_apply_started()
    apply_outcomes = client.kubectl_apply(manifestds)
    self.observer.on_apply_finished(apply_outcomes)
    time.sleep(2)

  def await_part(self):
    predicate_tree = from_apply_outcome(self.observer.get_kaos())
    predicates = utils.flatten(predicate_tree.values())
    state = StepState('synthetic', None)
    context = dict(resolvers=config_man.resolvers())
    for i in range(120):
      status_computer.compute(predicate_tree, state, context)
      self.observer.on_await_cycle_done(predicates, state)
      if state.has_settled():
        break
      else:
        time.sleep(2)
    print("DONE ONE DONE")
    print(state.status)
    self.observer.on_settled(state.status)
    return state.did_succeed()

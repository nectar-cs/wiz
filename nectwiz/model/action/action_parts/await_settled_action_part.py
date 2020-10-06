import time
from typing import List

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import ProgressItem, KAO, PredEval
from nectwiz.model.action.base.action_observer import Observer
from nectwiz.model.operation import status_computer
from nectwiz.model.operation.step_state import StepState
from nectwiz.model.predicate.resource_property_predicate import ResourcePropertyPredicate

key_await_settled = 'await_settled'

class AwaitSettledActionPart:
  @staticmethod
  def progress_items():
    return [
      ProgressItem(
        id=key_await_settled,
        status='idle',
        title='Await Resources Settled',
        info='Wait until all changed resources are in a settled state',
        sub_items=[]
      )
    ]

  @classmethod
  def perform(cls, observer: Observer, kaos: List[KAO]):
    observer.set_item_status(key_await_settled, 'running')
    predicate_tree = ResourcePropertyPredicate.from_apply_outcome(kaos)
    predicates = utils.flatten(predicate_tree.values())
    state = StepState('synthetic', None)
    context = dict(resolvers=config_man.resolvers())
    did_time_out = True
    for i in range(120):
      status_computer.compute(predicate_tree, state, context)
      cls.on_await_attempted(observer, state, predicates)
      cls.scan_settle_failures(observer, state, predicates)
      if state.has_settled():
        did_time_out = False
        break
      else:
        time.sleep(2)
    cls.scan_timeout_failure(observer, did_time_out)
    observer.set_item_status(key_await_settled, state.status)
    return state.did_succeed()

  @classmethod
  def on_await_attempted(cls, observer: Observer, state, predicates):
    exit_statuses: List[PredEval] = state.exit_statuses['positive']
    sub_items = []

    for status in exit_statuses:
      finder = lambda pred: pred.id() == status['predicate_id']
      originator = next(filter(finder, predicates), None)
      sub_items.append(dict(
        id=status['predicate_id'],
        title=originator and originator.title,
        info=originator and originator.info,
        status='positive' if status['met'] else 'running'
      ))

    observer.set_prop(key_await_settled, 'sub_items', sub_items)

  @classmethod
  def scan_timeout_failure(cls, observer, timed_out: bool):
    if timed_out:
      observer.process_error(
        fatal=True,
        event_type=key_await_settled
      )

  @classmethod
  def scan_settle_failures(cls, observer: Observer, state: StepState, predicates):
    if state.did_fail():
      finder = lambda es: es.get('met')
      culprit = next(filter(finder, state.exit_statuses['negative']), None)
      if culprit:
        finder = lambda pred: pred.id() == culprit['predicate_id']
        culprit_pred = next(filter(finder, predicates), None)
        if culprit_pred and hasattr(culprit_pred, 'selector'):
          original_res_sel = culprit_pred.selector()
          observer.process_error(
            event_type=key_await_settled,
            predicate_id=culprit_pred.id(),
            predicate_kind=culprit_pred.kind(),
            resource=dict(
              name=original_res_sel.name,
              kind=original_res_sel.k8s_kind
            )
          )

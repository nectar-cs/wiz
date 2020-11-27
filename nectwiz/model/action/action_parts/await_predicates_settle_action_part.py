import time
from typing import List

from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.base.observer import Observer
from nectwiz.model.operation.predicate_statuses_computer import PredicateStatusesComputer
from nectwiz.model.predicate.predicate import Predicate

key_await_settled = 'await_settled'

class AwaitPredicatesSettleActionPart:
  @staticmethod
  def progress_items():
    return [
      ProgressItem(
        id=key_await_settled,
        status='idle',
        title='Wait for Changed Resource to Settle',
        info='Wait until all changed resources are in a settled state',
        sub_items=[]
      )
    ]

  @classmethod
  def perform(cls, observer: Observer, predicates: List[Predicate]):
    observer.set_item_running(key_await_settled)
    computer = PredicateStatusesComputer(predicates)
    did_time_out = True
    for i in range(120):
      computer.perform_iteration()

      cls.update_observer(observer=observer, computer=computer)
      cls.scan_settle_failures(observer=observer, computer=computer)

      if computer.did_finish():
        did_time_out = False
        break
      else:
        time.sleep(2)

    cls.scan_timeout_failure(observer, did_time_out)
    observer.set_item_status(key_await_settled, 'positive')

  @classmethod
  def update_observer(cls, **kwargs):
    observer: Observer = kwargs['observer']
    computer: PredicateStatusesComputer = kwargs['computer']

    sub_items = []

    for predicate in computer.optimist_predicates:
      evaluation = computer.find_eval(predicate.id())
      sub_items.append(dict(
        id=predicate.id(),
        title=predicate.title,
        info=predicate.info,
        status='positive' if evaluation['met'] else 'running'
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
  def scan_settle_failures(cls, **kwargs):
    observer: Observer = kwargs['observer']
    computer: PredicateStatusesComputer = kwargs['computer']
    if computer.did_fail():
      predicate = computer.culprit_predicate()
      observer.process_error(
        fatal=True,
        tone='error',
        reason='One or more resources failed to settle',
        type='res_settle_failed',
        resource=predicate.culprit_res_signature(),
        extras=predicate.error_extras()
      )

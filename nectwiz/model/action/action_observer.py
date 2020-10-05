import json
from typing import Optional, List

from rq.job import Job, get_current_job

from nectwiz.core.core import utils
from nectwiz.core.core.types import ProgressItem, PredEval, KAOs, ErrDict
from nectwiz.model.error.controller_error import MyErr
from nectwiz.model.operation.step_state import StepState


class ActionObserver:
  def __init__(self, fail_fast=True):
    self.progress = ProgressItem()
    self.progress['sub_items'] = []
    self.blame_item_id = None
    self.errdicts = []
    self.fail_fast = fail_fast

  def notify_job(self, errdict=None):
    job: Job = get_current_job()
    if job:
      job.meta['progress'] = json.dumps(self.progress)
      if errdict:
        job.meta['error'] = json.dumps(errdict)
      job.save_meta()

  def item(self, _id: str) -> Optional[ProgressItem]:
    finder = lambda item: item.get('id') == _id
    return next(filter(finder, self.progress['sub_items']), None)

  def set_item_status(self, _id, status):
    item = self.item(_id)
    if item:
      item['status'] = status
    self.notify_job()

  def set_item_running(self, _id: str):
    self.set_item_status(_id, 'running')

  def set_item_outcome(self, _id: str, outcome: bool):
    self.set_item_status(_id, 'positive' if outcome else 'negative')

  def subitem(self, _id, sub_id) -> Optional[ProgressItem]:
    finder = lambda item: item.get('id') == sub_id
    outer_item = self.item(_id)
    return next(filter(finder, outer_item['sub_items']), None)

  def add_subitem(self, outer_id, subitem):
    self.item(outer_id)['sub_items'].append(subitem)

  def on_await_cycle_done(self, predicates, state: StepState):
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

    self.item('await_settled')['sub_items'] = sub_items
    self.check_res_wait_failures(state, predicates)
    self.notify_job()

  def check_kao_failures(self, outcomes: KAOs):
    self.blame_item_id = 'apply'
    fail_finder = lambda kao: kao.get('error') is not None
    kao_culprit = next(filter(fail_finder, outcomes), None)
    if kao_culprit is not None:
      self.process_error(
        event_type='apply_manifest',
        resource=dict(
          name=kao_culprit.get('name'),
          kind=kao_culprit.get('kind'),
        ),
        error=kao_culprit.get('error')
      )

  def check_res_wait_failures(self, state: StepState, predicates):
    if state.did_fail():
      finder = lambda es: es.get('met') == True
      culprit = next(filter(finder, state.exit_statuses['negative']), None)
      if culprit:
        finder = lambda pred: pred.id() == culprit['predicate_id']
        culprit_pred = next(filter(finder, predicates), None)
        if culprit_pred and hasattr(culprit_pred, 'selector'):
          original_res_sel = culprit_pred.selector()
          self.process_error(
            predicate_id=culprit_pred.id(),
            predicate_kind=culprit_pred.kind(),
            resource=dict(
              name=original_res_sel.name,
              kind=original_res_sel.k8s_kind
            )
          )

  def on_succeeded(self):
    self.progress['status'] = 'positive'
    self.notify_job()

  def on_failed(self, errdict: ErrDict = None):
    self.progress['status'] = 'negative'
    self.notify_job(errdict)

  def on_ended(self, success: bool):
    if success:
      self.on_succeeded()
    else:
      self.on_failed()

  def process_error(self, **errdict):
    errdict['uuid'] = utils.rand_str(20)
    if self.blame_item_id and self.item(self.blame_item_id):
      self.item(self.blame_item_id)['error_id'] = errdict['uuid']
      self.item(self.blame_item_id)['status'] = 'negative'
    if self.fail_fast:
      raise MyErr(errdict)
    else:
      self.errdicts.append(errdict)
      self.notify_job()


class ReluctantObserver(ActionObserver):
  def on_succeeded(self):
    pass

  def on_failed(self, ):
    pass

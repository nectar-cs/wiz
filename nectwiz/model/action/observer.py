import json
from typing import Optional, Union, List

from rq.job import Job, get_current_job

from nectwiz.core.core.types import ProgressItem, PredEval


class Observer:
  def __init__(self):
    self.progress = ProgressItem()
    self.progress['sub_items'] = []

  def notify_job(self):
    job: Job = get_current_job()
    if job:
      job.meta['progress'] = json.dumps(self.progress)
      job.save_meta()

  def item(self, _id) -> Optional[ProgressItem]:
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

  def on_exit_statuses_computed(self, predicates, statuses):
    flat_stats: List[Union[PredEval, ProgressItem]] = statuses['positive']
    for status in flat_stats:
      finder = lambda pred: pred.id() == status['predicate_id']
      originator = next(filter(finder, predicates), None)
      status['id'] = status['predicate_id']
      status['title'] = originator and originator.title
      status['info'] = originator and originator.info
      status['status'] = 'positive' if status['met'] else 'running'
    self.item('await_settled')['sub_items'] = flat_stats
    self.notify_job()

  def on_succeeded(self):
    self.progress['status'] = 'positive'
    self.notify_job()

  def on_failed(self):
    self.progress['status'] = 'negative'
    self.notify_job()


class ReluctantObserver(Observer):
  def on_succeeded(self):
    pass

  def on_failed(self):
    pass

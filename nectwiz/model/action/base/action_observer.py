import json
from typing import Optional, Any

from rq.job import Job, get_current_job

from nectwiz.core.core import utils
from nectwiz.core.core.types import ProgressItem, ErrDict
from nectwiz.model.error.controller_error import ActionHalt


class Observer:
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

  def set_prop(self, item_id: str, prop_name: str, new_value: Any):
    item = self.item(item_id)
    if item:
      # noinspection PyTypedDict
      item[prop_name] = new_value
      self.notify_job()
    else:
      print(f"[nectwiz::observer] danger no item {item_id}")

  def set_item_status(self, _id, status):
    self.set_prop(_id, 'status', status)

  def set_item_running(self, _id: str):
    self.set_item_status(_id, 'running')

  def set_item_outcome(self, _id: str, outcome: bool):
    self.set_item_status(_id, 'positive' if outcome else 'negative')

  def subitem(self, item_id: str, sub_id: str) -> Optional[ProgressItem]:
    outer_item = self.item(item_id)
    if outer_item:
      finder = lambda sub_item: sub_item.get('id') == sub_id
      return next(filter(finder, outer_item['sub_items']), None)
    else:
      print(f"[nectwiz::observer] danger no item {item_id}")

  def set_subitem_status(self, item_id:  str, sub_item_id: str, status: str):
    subitem = self.subitem(item_id, sub_item_id)
    if subitem:
      self.subitem(item_id, sub_item_id)['status'] = status
      self.notify_job()
    else:
      print(f"[nectwiz::observer] danger no subitem {item_id}/{sub_item_id}")

  def add_subitem(self, outer_id, subitem):
    self.item(outer_id)['sub_items'].append(subitem)

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
    self.errdicts.append(errdict)
    if self.blame_item_id and self.item(self.blame_item_id):
      self.set_prop(self.blame_item_id, 'error_id', errdict['uuid'])
      self.set_item_status(self.blame_item_id, 'negative')
    if self.fail_fast:
      raise ActionHalt(errdict)
    else:
      self.notify_job()


class ReluctantObserver(Observer):
  def on_succeeded(self):
    pass


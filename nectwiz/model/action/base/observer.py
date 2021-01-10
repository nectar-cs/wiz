import json
from typing import Optional, Any, List, Dict

from inflection import underscore
from rq.job import Job, get_current_job

from nectwiz.core.core import utils
from nectwiz.core.core.types import ProgressItem, ErrDict
from nectwiz.model.error.controller_error import ActionHalt
from nectwiz.model.error.errors_man import errors_man


class Observer:
  def __init__(self):
    self.blame_item_id: Optional[str] = None
    self.errdicts: List[ErrDict] = []
    self.progress = ProgressItem(
      id=underscore(self.__class__.__name__),
      logs=[],
      sub_items=[]
    )

  def notify_job(self):
    job: Job = get_current_job()
    if job:
      errors_man.add_errors(self.errdicts)
      job.meta['progress'] = json.dumps(self.progress)
      job.save_meta()

  def log(self, logs: List[str]):
    if not self.progress.get('logs'):
      self.progress['logs'] = []
    self.progress['logs'] += logs
    self.notify_job()

  def set_items(self, items: List[ProgressItem]):
    self.progress['sub_items'] = items

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

  # noinspection PyTypedDict
  def merge_prop(self, item_id: str, prop_name: str, patch: Dict):
    item = self.item(item_id)
    if item:
      current_value = item.get(prop_name, {}) or {}
      if type(current_value) == dict:
        item[prop_name] = dict(**current_value, **patch)
        self.notify_job()
      else:
        print(f"[nectwiz::observer] danger unmergeable {current_value}")
    else:
      print(f"[nectwiz::observer] danger no item {item_id}")

  def set_item_status(self, _id, status):
    self.set_prop(_id, 'status', status)

  def set_item_running(self, item_id: str):
    self.blame_item_id = item_id
    self.set_item_status(item_id, 'running')

  def set_item_outcome(self, _id: str, outcome: bool):
    self.set_item_status(_id, 'positive' if outcome else 'negative')

  def set_item_succeeded(self, _id: str):
    self.set_item_outcome(_id, True)

  def set_item_failed(self, _id: str):
    self.set_item_status(_id, False)

  def subitem(self, item_id: str, sub_id: str) -> Optional[ProgressItem]:
    outer_item = self.item(item_id)
    if outer_item:
      finder = lambda sub_item: sub_item.get('id') == sub_id
      return next(filter(finder, outer_item['sub_items']), None)
    else:
      print(f"[nectwiz::observer] danger no item {item_id}")

  def set_subitem_status(self, item_id:  str, sub_item_id: str, status: str):
    self.set_subitem_prop(item_id, sub_item_id, 'status', status)

  def set_crt_subitem_status(self, sub_item_id: str, status: str):
    self.set_subitem_prop(self.blame_item_id, sub_item_id, 'status', status)

  def set_subitem_prop(self, item_id:  str, sub_item_id: str, prop, value: str):
    subitem = self.subitem(item_id, sub_item_id)
    if subitem:
      self.subitem(item_id, sub_item_id)[prop] = value
      self.notify_job()
    else:
      print(f"[nectwiz::observer] danger no subitem {item_id}/{sub_item_id}")

  def add_subitem(self, outer_id, subitem):
    self.item(outer_id)['sub_items'].append(subitem)
    self.notify_job()

  def on_succeeded(self):
    self.progress['status'] = 'positive'
    self.notify_job()

  def on_failed(self, errdict: ErrDict = None):
    self.progress['status'] = 'negative'
    if errdict:
      self.process_error(**errdict)

  def on_ended(self, success: bool):
    if success:
      self.on_succeeded()
    else:
      self.on_failed()

  def process_error(self, **errdict):
    from nectwiz.model.error.error_handler import ErrorHandler
    errdict['uuid'] = utils.rand_str(20)
    tone, reason = errdict.pop('tone', None), errdict.pop('reason', None)
    self.errdicts.append(errdict)
    if self.blame_item_id and self.item(self.blame_item_id):
      diagnosable = ErrorHandler.is_err_diagnosable(errdict)
      self.set_item_status(self.blame_item_id, 'negative')
      self.cancel_blamed_subitems()
      self.merge_prop(self.blame_item_id, 'error', dict(
        id=errdict['uuid'] if diagnosable else None,
        tone=tone,
        reason=reason
      ))
    else:
      print(f"[nectwiz::observer] critical no blame id for {errdict}")
    if errdict.get('fatal'):
      raise ActionHalt(errdict)
    else:
      self.notify_job()

  def cancel_blamed_subitems(self):
    item = self.item(self.blame_item_id)
    subitems = item.get('sub_items', [])
    for subitem in subitems:
      if subitem.get('status') == 'running':
        subitem['status'] = 'negative'


class simple_action_eval:
  def __init__(self, observer: Observer, action_part_key: str):
    self.observer: Observer = observer
    self.action_part_key: str = action_part_key

  def __enter__(self):
    self.observer.set_item_running(self.action_part_key)

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.observer.set_item_succeeded(self.action_part_key)

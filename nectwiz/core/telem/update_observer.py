import json
from typing import List, Tuple, Optional

from rq import get_current_job
from rq.job import Job

from nectwiz.core.core import utils
from nectwiz.core.core.types import ProgressItem
from nectwiz.model.action.observer import Observer


class UpdateObserver(Observer):
  def __init__(self, _type):
    super().__init__()
    self.progress = ProgressItem(
      id=None,
      status='running',
      title=f"Application {_type}",
      info="Updates the variables manifest and waits for a settled state",
      sub_items=[
        ProgressItem(
          id='before_hooks',
          status='idle',
          title='Pre-update Hooks',
          info='Run vendor-provided hooks, halt on fatal error',
          sub_items=[]
        ),
        dict(
          id='perform',
          status='idle',
          title='Perform Update',
          info='Apply the new application manifest',
          logs=[],
          outcomes=[],
          mfst_vars={},
          sub_items=[
            dict(
              id='perform_commit',
              status='idle',
              title='Write new manifest defaults',
            ),
            dict(
              id='perform_apply',
              status='idle',
              title='Apply new manifest',
            )
          ]
        ),
        ProgressItem(
          id='await_settled',
          status='idle',
          title='Await Resources Settled',
          info='Wait until all changed resources are in a settled state',
          sub_items=[]
        ),
        ProgressItem(
          id='after_hooks',
          status='idle',
          title='Post-update Hooks',
          info='Run vendor-provided hooks, halt on fatal error',
          sub_items=[]
        )
      ]
    )

  def on_hook_started(self):
    self.item('perform')['status'] = 'running'
    self.notify_job()

  def on_hook_done(self, which: str, name, status):
    bucket = self.item(f'{which}_hooks')
    hook_finder = lambda hook_prog: hook_prog['title'] == name
    hook = next(filter(hook_finder, bucket['sub_items']), None)
    hook['status'] = status
    self.notify_job()

  def on_hook_set_started(self, which, hook_names):
    bucket = self.item(f'{which}_hooks')
    bucket['sub_items'] = list(map(shallow_hook, hook_names))
    self.notify_job()

  def on_hook_set_done(self, which):
    self.item(f'{which}_hooks')['status'] = 'positive'
    self.notify_job()

  def on_perform_started(self):
    self.item('perform')['status'] = 'running'
    self.subitem('perform', 'perform_commit')['status'] = 'running'
    self.notify_job()

  def on_mfst_vars_committed(self, mfst_vars: List[Tuple[str, str]]):
    # noinspection PyTypeChecker
    self.item('perform')['mfst_vars'] = mfst_vars
    self.subitem('perform', 'perform_commit')['status'] = 'positive'
    self.subitem('perform', 'perform_apply')['status'] = 'running'
    self.notify_job()

  # noinspection PyTypeChecker
  def on_perform_finished(self, status, log_chunk):
    logs = utils.clean_log_lines(log_chunk)
    self.subitem('perform', 'perform_apply')['status'] = 'positive'
    self.item('perform')['logs'] = logs
    self.item('perform')['outcomes'] = utils.logs2outkomes(logs)
    self.item('perform')['status'] = status
    self.notify_job()

  def get_ktl_apply_logs(self) -> List[str]:
    return self.item('perform')['logs'] or []

  def on_settle_wait_started(self):
    self.item('await_settled')['status'] = 'running'
    self.notify_job()

  def on_settled(self, status: str):
    self.item('await_settled')['status'] = status
    self.notify_job()

def shallow_hook(name) -> ProgressItem:
  return ProgressItem(
    id=name,
    title=name,
    status='idle',
    info=None,
    sub_items=[]
  )

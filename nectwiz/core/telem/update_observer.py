import functools
import json
from typing import TypedDict, List

from rq import get_current_job
from rq.job import Job


class UpdateObserver:
  def __init__(self):
    self.progress: UpdateProgress = UpdateProgress(
      before_hooks_progress=HookSetProgress(status='idle', hook_statuses=[]),
      perform_progress=PerformProgress(status='idle', logs=[]),
      after_hooks_progress=HookSetProgress(status='idle', hook_statuses=[]),
      sync_progress='idle'
    )

  def on_fatal_error(self):
    self.progress['status'] = 'negative'

  def on_succeeded(self):
    self.progress['status'] = 'positive'


  def on_hook_set_done(self, which):
    pass

  def on_hook_set_started(self, which, hook_names):
    bucket = getattr(self, f"{which}_hooks_progress")
    bucket['hook_statuses'] = list(map(shallow_hook, hook_names))

  def on_hook_done(self, which: str, name: str, status, message: str):
    bucket = getattr(self, f"{which}_hooks_progress")

    self.notify_job()

  def on_perform_started(self):
    self.progress['perform_progress']['status'] = 'running'
    self.notify_job()

  def notify_job(self):
    job: Job = get_current_job()
    job.meta['progress'] = json.dumps(self.progress)
    job.save_meta()



class HookProgress(TypedDict):
  name: str
  status: str
  message: str


class HookSetProgress(TypedDict):
  status: str
  hook_statuses: List[HookProgress]


class PerformProgress(TypedDict):
  status: str
  logs: List[str]


class UpdateProgress(TypedDict, total=False):
  status: str
  before_hooks_progress: HookSetProgress
  perform_progress: PerformProgress
  after_hooks_progress: HookSetProgress
  sync_progress: str

def shallow_hook(name) -> HookProgress:
  return HookProgress(
    name=name,
    status='idle',
    message=''
  )
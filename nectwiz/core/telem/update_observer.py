import json
from typing import List, Tuple, Optional

from rq import get_current_job
from rq.job import Job

from nectwiz.core.core import utils
from nectwiz.core.core.types import ProgressItem


class UpdateObserver:
  def __init__(self, _type):
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
          title='Pre-update Hooks',
          info='Run vendor-provided hooks, halt on fatal error',
          logs=[],
          mfst_vars={},
          sub_items=[]
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

  def item(self, _id) -> Optional[ProgressItem]:
    finder = lambda item: item.get('id') == _id
    return next(filter(finder, self.progress['sub_items']), None)

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
    self.notify_job()

  def on_mfst_vars_committed(self, mfst_vars: List[Tuple[str, str]]):
    # noinspection PyTypeChecker
    self.item('perform')['mfst_vars'] = mfst_vars
    self.notify_job()

  def on_perform_finished(self, status, log_chunk):
    self.item('perform')['status'] = status
    # noinspection PyTypeChecker
    self.item('perform')['logs'] = utils.clean_log_lines(log_chunk)
    self.notify_job()

  def get_ktl_apply_logs(self) -> List[str]:
    return self.item('perform')['logs'] or []

  def on_exit_statuses_computed(self, predicates, statuses):
    flat_stats = statuses['positive'] + statuses['negative']
    for status in flat_stats:
      finder = lambda pred: pred.id() == status['predicate_id']
      originator = next(filter(finder, predicates), None)
      status['id'] = status['predicate_id']
      status['title'] = originator and originator.title
      status['info'] = originator and originator.info

    self.item('await_settled')['status'] = 'running'
    self.item('await_settled')['sub_items'] = statuses
    self.notify_job()

  def on_settled(self, status: str):
    self.item('await_settled')['status'] = status
    self.notify_job()

  def on_fatal_error(self):
    self.progress['status'] = 'negative'

  def on_succeeded(self):
    self.progress['status'] = 'positive'

  def notify_job(self):
    job: Job = get_current_job()
    if job:
      job.meta['progress'] = json.dumps(self.progress)
      job.save_meta()


def shallow_hook(name) -> ProgressItem:
  return ProgressItem(
    id=name,
    title=name,
    status='idle',
    info=None,
    sub_items=[]
  )

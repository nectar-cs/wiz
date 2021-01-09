from datetime import datetime
from typing import Dict, Optional

from nectwiz.core.core import job_client
from nectwiz.core.core.types import ExitStatuses, ActionOutcome

IDLE = 'idle'
RUNNING = 'running'
SETTLED_POS = 'positive'
SETTLED_NEG = 'negative'


class StepState:
  def __init__(self, step_sig: str, parent_op):
    self.step_sig: str = step_sig
    self.parent_op = parent_op
    self.status: str = IDLE
    self.started_at = datetime.now()
    self.chart_assigns: Dict = {}
    self.state_assigns: Dict = {}
    self.pref_assigns: Dict = {}
    self.action_outcome: Optional[ActionOutcome] = None
    self.action_telem = None
    self.exit_statuses: ExitStatuses = default_exit_statuses()
    self.committed_at = None
    self.terminated_at = None
    self.job_id = None

  def is_running(self):
    return self.status == RUNNING

  def has_settled(self):
    return self.status in [SETTLED_POS, SETTLED_NEG]

  def did_succeed(self):
    return self.status == SETTLED_POS

  def did_fail(self):
    return self.status == SETTLED_NEG

  def notify_action_started(self, job_id):
    self.status = 'running'
    self.job_id = job_id

  def notify_vars_assigned(self, bundle: Dict):
    self.chart_assigns = bundle.get('chart')
    self.state_assigns = bundle.get('state')
    self.pref_assigns = bundle.get('prefs')
    self.pref_assigns = bundle.get('prefs')

  def notify_terminated(self, success: bool, telem):
    self.status = SETTLED_POS if success else SETTLED_NEG
    self.action_telem = telem

  def notify_succeeded(self):
    self.status = SETTLED_POS

  def notify_failed(self):
    self.status = SETTLED_NEG

  def all_assigns(self):
    """
    Merges chart assigns and state assigns extracted from the commit outcome.
    :return:
    """
    return dict(
      **self.chart_assigns,
      **self.state_assigns,
      **self.pref_assigns
    )

  def inform_status_from_worker(self) -> Dict:
    action_job = job_client.find_job(self.job_id)
    if action_job:
      progress = job_client.job_progress(self.job_id)
      if action_job.is_finished or action_job.is_failed:
        if action_job.is_finished:
          telem = job_client.job_telem(self.job_id)
          self.notify_terminated(action_job.result, telem)
        else:
          self.notify_failed()
        return dict(status=self.status, progress=progress)
      else:
        return dict(status='running', progress=progress)
    else:
      print(f"[nectwiz::step] danger job {self.job_id} lost!")
      return dict(status='negative', progress={})


def default_exit_statuses() -> ExitStatuses:
  return ExitStatuses(positive=[], negative=[])

from datetime import datetime
from typing import Dict, List, Optional

from nectwiz.core.core.types import PredEval, ExitStatuses, ActionOutcome

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


def default_exit_statuses() -> ExitStatuses:
  return ExitStatuses(positive=[], negative=[])

from datetime import datetime
from typing import Dict, List, Optional

from nectwiz.core.core.types import PredEval, ExitStatuses, ActionOutcome

IDLE = 'idle'
RUNNING = 'running'
SETTLING = 'settling'
SETTLED_POS = 'settled'
SETTLED_NEG = 'settled'


class StepState:
  def __init__(self, step_sig: str, parent_op):
    self.step_sig: str = step_sig
    self.parent_op = parent_op
    self.status: str = IDLE
    self.started_at = datetime.now()
    self.chart_assigns: Dict = {}
    self.state_assigns: Dict = {}
    self.action_outcome: Optional[ActionOutcome] = None
    self.exit_statuses: ExitStatuses = default_exit_statuses()
    self.committed_at = None
    self.terminated_at = None
    self.job_id = None

  def was_running(self):
    return self.status == RUNNING

  def has_settled(self):
    return self.status in [SETTLED_POS, SETTLED_NEG]

  def action_was(self, cls_name) -> bool:
    if self.action_outcome:
      return self.action_outcome['charge'] == cls_name
    else:
      return False

  def is_awaiting_settlement(self):
    return self.status == SETTLING

  def notify_action_started(self, job_id):
    self.status = 'running'
    self.job_id = job_id

  def notify_vars_assigned(self, chart_assigns: Dict, state_assigns: Dict):
    self.chart_assigns = chart_assigns
    self.state_assigns = state_assigns

  def notify_succeeded(self):
    self.status = SETTLED_POS

  def notify_failed(self):
    self.status = SETTLED_NEG

  def notify_is_settling(self):
    self.status = SETTLING

  def notify_exit_status_computed(self, charge, pred_eval: PredEval):
    # noinspection PyTypedDict
    existing: List[PredEval] = self.exit_statuses[charge]
    matcher = lambda es: es['key'] == pred_eval['key']
    entry = next(filter(matcher, existing), None)
    if entry:
      entry['met'] = pred_eval['met']
      entry['reason'] = pred_eval['reason']
    else:
      existing.append(pred_eval)

  def all_exit_statuses(self) -> List[PredEval]:
    return self.exit_statuses['positive'] + self.exit_statuses['negative']

  def all_assigns(self):
    """
    Merges chart assigns and state assigns extracted from the commit outcome.
    :return:
    """
    return dict(**self.chart_assigns, **self.state_assigns)


def default_exit_statuses() -> ExitStatuses:
  return ExitStatuses(positive=[], negative=[])

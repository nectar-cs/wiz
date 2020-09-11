from datetime import datetime
from typing import Dict, List, Optional

from nectwiz.core.core.types import PredEval, ExitStatuses, ActionOutcome

IDLE = 'idle'
RUNNING = 'running'
SETTLING = 'settling'
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
      return self.action_outcome['cls_name'] == cls_name
    else:
      return False

  def did_succeed(self):
    return self.status == SETTLED_POS

  def did_fail(self):
    return self.status == SETTLED_NEG

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

  def notify_is_settling(self, action_outcome: ActionOutcome):
    self.action_outcome = action_outcome
    self.status = SETTLING

  def notify_exit_status_computed(self, charge, new_eval: PredEval):
    # noinspection PyTypedDict
    existing: List[PredEval] = self.exit_statuses[charge]
    key = 'predicate_id'
    matcher = lambda old_eval: old_eval[key] == new_eval[key]
    entry = next(filter(matcher, existing), None)
    if entry:
      entry['met'] = new_eval['met']
      entry['name'] = new_eval.get('name')
      entry['reason'] = new_eval.get('reason')
    else:
      existing.append(new_eval)

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

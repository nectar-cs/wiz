from datetime import datetime
from typing import Dict, List

from nectwiz.core.core.types import PredEval, ExitStatuses

POS = 'positive'
NEG = 'negative'
SETTLING = 'settling'


class StepState:
  def __init__(self, step_sig: str, parent_op):
    self.step_sig: str = step_sig
    self.parent_op = parent_op
    self.status: str = 'pending'
    self.started_at = datetime.now()
    self.chart_assigns: Dict = {}
    self.state_assigns: Dict = {}
    self.exit_statuses: ExitStatuses = default_exit_statuses()
    self.committed_at = None
    self.terminated_at = None
    self.job_id = None
    self.job_logs = []

  def was_running(self):
    return self.status == 'running'

  def was_verifying(self):
    return self.status == 'exit'

  def notify_action_started(self, job_id):
    self.status = 'running'
    self.job_id = job_id

  def notify_succeeded(self):
    self.status = POS

  def notify_failed(self):
    self.status = NEG

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

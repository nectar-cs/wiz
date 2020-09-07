from datetime import datetime
from typing import Dict, List

from nectwiz.core.core.types import ExitStatus, ExitStatuses


class StepState:
  def __init__(self, step_sig: str, parent_op):
    self.step_sig: str = step_sig
    self.parent_op = parent_op
    self.status: str = 'pending'
    self.started_at = datetime.now()
    self.chart_assigns: Dict = {}
    self.state_assigns: Dict = {}
    self.exit_statuses: ExitStatuses = {}
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
    self.status = 'positive'

  def notify_is_verifying(self):
    self.status = 'verifying'

  @property
  def all_assigns(self):
    """
    Merges chart assigns and state assigns extracted from the commit outcome.
    :return:
    """
    return dict(**self.chart_assigns, **self.state_assigns)

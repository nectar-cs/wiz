from copy import deepcopy
from datetime import datetime
from typing import List, Optional, Dict

from k8_kat.utils.main.utils import deep_merge
from wiz.core.types import CommitOutcome


class StepState:
  def __init__(self, **kwargs):
    self.stage_id = kwargs.get('stage_id')
    self.step_id = kwargs.get('step_id')
    self.started_at = kwargs.get('started_at')
    self.commit_outcome = None
    self.commit_reason = None
    self.committed_at = None
    self.chart_assigns: Optional[Dict] = kwargs.get('chart_assigns', {})
    self.state_assigns: Optional[Dict] = kwargs.get('state_assigns', {})
    self.terminated_at = None
    self.outcome = None
    self.job_id = None
    self.exist_code = None
    self.logs = None

  def patch_committed(self, com_outcome: CommitOutcome):
    self.committed_at = datetime.now()
    self.commit_outcome = com_outcome.get('status')
    self.commit_reason = com_outcome.get('reason')
    self.chart_assigns = deepcopy(com_outcome.get('chart_assigns'))
    self.state_assigns = deepcopy(com_outcome.get('state_assigns'))
    self.job_id = com_outcome.get('job_id')

  def patch_terminated(self, outcome, logs=None):
    self.outcome = outcome
    self.logs = logs

  def belongs_to_step(self, step_id, stage_id):
    return self.step_id == step_id and \
           self.stage_id == stage_id

  def serialize(self):
    return dict(
      step_id=self.step_id,
      stage_id=self.step_id,
    )


class OperationState:

  def __init__(self, **kwargs):
    self.osr_id = kwargs.get('id')
    self.step_states: List[StepState] = kwargs.get('step_states', [])

  @classmethod
  def find_or_create(cls, osr_id):
    matcher = (oo for oo in operation_states if oo.osr_id == osr_id)
    existing = next(matcher, None)
    if not existing:
      existing = OperationState(id=osr_id)
      operation_states.append(existing)
    return existing

  def record_step_started(self, step_id, stage_id):
    self.step_states.append(StepState(
      step_id=step_id,
      stage_key=stage_id,
      started_at=datetime.now()
    ))

  def record_step_committed(self, stage_id, step_id, outcome: CommitOutcome):
    existing = self.find_step_record(stage_id, step_id)
    existing.patch_committed(outcome)

  def record_step_terminated(self, stage_id, step_id, outcome, job_outcome=None):
    existing = self.find_step_record(stage_id, step_id)
    existing.patch_terminated(outcome, job_outcome)

  def find_step_record(self, stage_id, step_id):
    predicate = lambda so: so.belongs_to_step(stage_id, step_id)
    matcher = (so for so in self.step_states if predicate(so))
    return next(matcher, None)

  def bank(self):
    merged = {}
    for step_record in self.step_states:
      merged = deep_merge(merged, step_record.state_assigns)
    return merged


operation_states: List[OperationState] = []

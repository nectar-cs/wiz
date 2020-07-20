from copy import deepcopy
from datetime import datetime
from functools import reduce
from typing import List, Dict

from k8_kat.utils.main.utils import deep_merge
from wiz.core.types import CommitOutcome, StepRunningStatus


class StepState:
  def __init__(self, **kwargs):
    self.stage_id = kwargs.get('stage_id')
    self.step_id = kwargs.get('step_id')
    self.started_at = kwargs.get('started_at', datetime.now())
    self.commit_outcome: CommitOutcome = kwargs.get('commit_outcome', {})
    self.running_status: StepRunningStatus = {}
    self.committed_at = None
    self.terminated_at = None
    self.job_id = None
    self.job_logs = []

  @property
  def chart_assigns(self):
    return self.commit_outcome.get('chart_assigns', {})

  @property
  def state_assigns(self):
    return self.commit_outcome.get('state_assigns', {})

  @property
  def all_assigns(self):
    return dict(**self.chart_assigns, **self.state_assigns)

  def patch_committed(self, commit_outcome: CommitOutcome):
    self.committed_at = datetime.now()
    self.commit_outcome = deepcopy(commit_outcome)
    self.job_id = commit_outcome.get('job_id')

  def patch_pending(self, status: StepRunningStatus):
    self.running_status = status

  def patch_terminated(self, status: StepRunningStatus):
    self.running_status = status
    self.terminated_at = datetime.now()

  def belongs_to_step(self, stage_id, step_id):
    return self.step_id == step_id and self.stage_id == stage_id

  def serialize(self):
    return dict(
      step_id=self.step_id,
      stage_id=self.step_id,
    )


class OperationState:
  def __init__(self, **kwargs):
    self.osr_id = kwargs.get('id')
    self.operation_id = kwargs.get('operation_id')
    self.step_states: List[StepState] = kwargs.get('step_states', [])

  @classmethod
  def find_or_create(cls, ost_id: str, operation_id: str):
    instance = cls.find(ost_id)
    if not instance:
      instance = OperationState(id=ost_id, operation_id=operation_id)
      operation_states.append(instance)
    return instance

  @classmethod
  def find(cls, osr_id):
    matcher = (oo for oo in operation_states if oo.osr_id == osr_id)
    return next(matcher, None)

  @classmethod
  def delete_if_exists(cls, osr_id: str):
    tuples = enumerate(operation_states)
    index = next((i for i, ops in tuples if ops.osr_id == osr_id), None)
    return operation_states.pop(index) if index else None

  def is_tracked(self):
    return self.osr_id is not None

  def record_step_started(self, stage_id, step_id):
    self.step_states.append(StepState(
      step_id=step_id,
      stage_id=stage_id,
      started_at=datetime.now()
    ))

  def record_step_committed(self, stage_id, step_id, commit_outcome: CommitOutcome):
    step_state = self.find_step_record(stage_id, step_id)
    if step_state:
      step_state.patch_committed(commit_outcome)

  def record_step_terminated(self, stage_id, step_id, status: StepRunningStatus):
    step_state = self.find_step_record(stage_id, step_id)
    if step_state:
      step_state.patch_terminated(status)

  def record_step_pending(self, stage_id, step_id, status: StepRunningStatus):
    step_state = self.find_step_record(stage_id, step_id)
    if step_state:
      step_state.patch_pending(status)

  def find_step_record(self, stage_id, step_id):
    predicate = lambda so: so.belongs_to_step(stage_id, step_id)
    matcher = (so for so in self.step_states if predicate(so))
    return next(matcher, None)

  def state_assigns(self) -> Dict:
    merge = lambda w, e: deep_merge(w, deepcopy(e.state_assigns))
    return reduce(merge, self.step_states, {})

  def chart_assigns(self) -> Dict:
    merge = lambda w, e: deep_merge(w, deepcopy(e.chart_assigns))
    return reduce(merge, self.step_states, {})

  def all_assigns(self) -> Dict:
    return {**self.state_assigns(), **self.chart_assigns()}


operation_states: List[OperationState] = []

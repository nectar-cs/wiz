from copy import deepcopy
from datetime import datetime
from functools import reduce
from typing import List, Dict, Optional

from k8kat.utils.main.utils import deep_merge
from nectwiz.core.types import CommitOutcome, StepRunningStatus


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
    """
    Getter for chart assigns from the Step's commit outcome.
    :return: chart assigns dict.
    """
    return self.commit_outcome.get('chart_assigns', {})

  @property
  def state_assigns(self):
    """
    Getter for state assigns from the Step's commit outcome.
    :return: state assigns dict.
    """
    return self.commit_outcome.get('state_assigns', {})

  @property
  def all_assigns(self):
    """
    Merges chart assigns and state assigns extracted from the commit outcome.
    :return:
    """
    return dict(**self.chart_assigns, **self.state_assigns)

  def patch_committed(self, commit_outcome: CommitOutcome):
    """
    Patches the current StepState with the details of the commit outcome. Eg
    happens when the user submits a form with the given state in the Front End.
    :param commit_outcome: details of last commit outcome.
    """
    self.committed_at = datetime.now()
    self.commit_outcome = deepcopy(commit_outcome)
    self.job_id = commit_outcome.get('job_id')

  def patch_pending(self, status: StepRunningStatus):
    """
    Patches the status of the current StepState as pending. Occurs while not all
    exit checks have passed.
    :param status: dict with status details used to patch the state.
    """
    self.running_status = status

  def patch_terminated(self, status: StepRunningStatus):
    """
    Patches the current StepState with the terminated status and termination time.
    :param status: dict with status details used to patch the state.
    """
    self.running_status = status
    self.terminated_at = datetime.now()

  def belongs_to_step(self, stage_id:str, step_id:str) -> bool:
    """
    Checks if the current StepOutcome belongs to a given Step.
    :param stage_id: stage id to check against.
    :param step_id: step id to check against.
    :return: True if both match, False otherwise.
    """
    return self.step_id == step_id and self.stage_id == stage_id

  def serialize(self):
    """
    Serializes the StepState object into a simple dict.
    :return: dict with step id and stage id.
    """
    return dict(
      step_id=self.step_id,
      stage_id=self.stage_id
    )


class OperationState:
  def __init__(self, **kwargs):
    self.ost_id = kwargs.get('id') #ost = operation state
    self.operation_id = kwargs.get('operation_id')
    self.step_states: List[StepState] = kwargs.get('step_states', [])
    self.status = 'pending'

  @classmethod
  def find(cls, ost_id: Optional[str]) -> 'OperationState':
    """
    Finds the OperationState with the marching osr id.
    :param ost_id: id to match by.
    :return: OperationState or None
    """
    matcher = (oo for oo in operation_states if oo.ost_id == ost_id)
    return next(matcher, None)

  @classmethod
  def create(cls, operation_id: str, osd_id: str):
    operation_states.append(OperationState(
      id=osd_id,
      operation_id=operation_id
    ))

  @classmethod
  def mark_status_if_exists(cls, ost_id, status: str) -> bool:
    op_state = cls.find(ost_id)
    if op_state:
      op_state.status = status
      return True
    return False

  @classmethod
  def delete_if_exists(cls, ost_id: Optional[str]) -> Optional['OperationState']:
    """
    Deletes the OperationState if one with the given osr id exists.
    :param ost_id: id used to locate the OperationState.
    :return: deleted instance of the OperationState if found, else None.
    """
    tuples = enumerate(operation_states)
    index = next((i for i, ops in tuples if ops.ost_id == ost_id), None)
    return operation_states.pop(index) if index else None

  @classmethod
  def prune(cls):
    while cls.find(None):
      cls.delete_if_exists(None)

  def is_tracked(self):
    """
    Checks if a given OperationState has an osr id associated with it.
    :return: True if it does, False otherwise.
    """
    return self.ost_id is not None


  def record_step_started(self, stage_id:str, step_id:str):
    """
    Append a new StepState to the current OperationState.
    :param stage_id: stage id to be recorded for the StepState.
    :param step_id: step id to be recorded for the StepState.
    """
    self.step_states.append(StepState(
      step_id=step_id,
      stage_id=stage_id,
      started_at=datetime.now()
    ))

  def record_step_committed(self, stage_id:str, step_id:str, commit_outcome: CommitOutcome):
    """
    Records that a given step has been committed.
    :param stage_id: stage id to find the right step.
    :param step_id: step id to find the right step.
    :param commit_outcome: commit outcome with the details of the commit.
    """
    step_state = self.find_step_record(stage_id, step_id)
    if step_state:
      step_state.patch_committed(commit_outcome)

  def record_step_terminated(self, stage_id, step_id, status: StepRunningStatus):
    """
    Records that a given step has been terminated.
    :param stage_id: stage id to find the right step.
    :param step_id: step id to find the right step.
    :param status: dict with status details used to patch the state.
    """
    step_state = self.find_step_record(stage_id, step_id)
    if step_state:
      step_state.patch_terminated(status)

  def record_step_pending(self, stage_id, step_id, status: StepRunningStatus):
    """
    Records that a given step is still pending.
    :param stage_id: stage id to find the right step.
    :param step_id: step id to find the right step.
    :param status: dict with status details used to patch the state.
    """
    step_state = self.find_step_record(stage_id, step_id)
    if step_state:
      step_state.patch_pending(status)

  def find_step_record(self, stage_id, step_id) -> StepState:
    """
    Finds the StepOutcome with a matching stage_id and step_id.
    :param stage_id: stage id to match against.
    :param step_id: step id to match against.
    :return: matching StepOutcome or None.
    """
    predicate = lambda so: so.belongs_to_step(stage_id, step_id)
    matcher = (so for so in self.step_states if predicate(so))
    return next(matcher, None)

  def state_assigns(self) -> Dict:
    """
    Deep merges state assigns from a list of StepStates
    :return: all state assigns in one dict.
    """
    merge = lambda w, e: deep_merge(w, deepcopy(e.state_assigns)) #whole, #element
    return reduce(merge, self.step_states, {})

  def chart_assigns(self) -> Dict:
    """
    Deep merges chart assigns from a list of StepStates.
    :return: all chart assigns in one dict.
    """
    merge = lambda w, e: deep_merge(w, deepcopy(e.chart_assigns))
    return reduce(merge, self.step_states, {})

  def all_assigns(self) -> Dict:
    """
    Merges together state assigns and chart assigns into a single dict.
    :return: dict containing state assigns and chart assigns.
    """
    return {**self.state_assigns(), **self.chart_assigns()}


operation_states: List[OperationState] = []

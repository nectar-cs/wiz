from copy import deepcopy
from datetime import datetime
from functools import reduce
from typing import List, Dict, Optional

from k8kat.utils.main.utils import deep_merge

from nectwiz.core.core import utils
from nectwiz.core.core.types import CommitOutcome
from nectwiz.model.step.step_state import StepState


class OperationState:
  def __init__(self, uuid: str, operation_id: str):
    self.uuid: str = uuid
    self.op_id: str = operation_id
    self.step_states: List[StepState] = []
    self.status = 'running'

  def find_step_state(self, step) -> StepState:
    matcher = lambda ss: ss.sig == step.sig()
    return next(filter(matcher, self.step_states), None)

  def gen_step_state(self, step) -> StepState:
    if not self.find_step_state(step):
      new_ss = StepState(step.sig(), self)
      self.step_states.append(new_ss)
      return new_ss
    else:
      raise RuntimeError("Step with same signature exists!")

  @classmethod
  def find(cls, ost_id: Optional[str]) -> 'OperationState':
    """
    Finds the OperationState with the marching osr id.
    :param ost_id: id to match by.
    :return: OperationState or None
    """
    matcher = lambda op_state: op_state.uuid == ost_id
    return next(filter(matcher, operation_states), None)

  @classmethod
  def gen(cls, operation_id: str) -> str:
    uuid = utils.rand_str(string_len=10)
    operation_states.append(OperationState(uuid, operation_id))
    return uuid

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
    index = next((i for i, ops in tuples if ops.uuid == ost_id), None)
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


  def find_step_state(self, step_uid):
    f = lambda ss: ss.get('step_uid') == step_uid
    return next(filter(f, self.step_states))


operation_states: List[OperationState] = []

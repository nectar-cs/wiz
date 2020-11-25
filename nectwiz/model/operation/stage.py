from typing import List

from nectwiz.model.base.wiz_model import WizModel, key_or_dict_to_key
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.operation.step import Step


class Stage(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.description = config.get('description')

  def first_step_key(self) -> str:
    """
    Returns the key of the first associated Step, if present.
    :return: Step key or None.
    """
    step_descriptors = self.config.get('steps', [])
    first = step_descriptors[0] if len(step_descriptors) else None
    return key_or_dict_to_key(first) if first else None

  def next_step_id(self, crt_step: Step, op_state: OperationState) -> str:
    """
    Returns the id of the next step, or "done" if no next step exists.
    :param crt_step:
    :param op_state: if-then-else values, if necessary.
    :return: id of next step or "done".
    """
    if crt_step.has_explicit_next():
      return crt_step.next_step_id(op_state)
    else:
      stage_steps = self.steps()
      index = step_index(stage_steps, crt_step.id())
      is_not_last = index < len(stage_steps) - 1
      return stage_steps[index + 1].id() if is_not_last else 'done'

  def steps(self) -> List[Step]:
    """
    Loads the Steps associated with the Stage.
    :return: List of Step instances.
    """
    return self.inflate_children('steps', Step)

  def step(self, _id: str) -> Step:
    """
    Finds the Step by key and inflates (instantiates) into a Step instance.
    :param _id: identifier for desired Step.
    :return: Step instance.
    """
    return self.inflate_child_in_list('steps', Step, _id)


def step_index(steps: List[Step], step_id: str) -> int:
  """
  Returns the index of the desired Step.
  :param steps: list of all Steps associated with a Stage.
  :param step_id: id to identify the desired Step.
  :return: index of the desired Step.
  """
  finder = (i for i, step in enumerate(steps) if step.id() == step_id)
  return next(finder)

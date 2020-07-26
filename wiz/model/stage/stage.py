from typing import Dict, List

from wiz.model.base.wiz_model import WizModel, key_or_dict_to_key
from wiz.model.step.step import Step


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
    first = step_descriptors[0] if len(step_descriptors) else 0
    return key_or_dict_to_key(first) if first else None

  def next_step_id(self, crt_step: Step, values: Dict[str, str]) -> str:
    """
    Returns the id of the next step, or "done" if no next step exists.
    :param crt_step:
    :param values: if-then-else values, if necessary.
    :return: id of next step or "done".
    """
    if crt_step.has_explicit_next():
      return crt_step.next_step_id(values)
    else:
      stage_steps = self.steps()
      index = step_index(stage_steps, crt_step.key)
      is_not_last = index < len(stage_steps) - 1
      return stage_steps[index + 1].key if is_not_last else 'done'

  def steps(self) -> List[Step]:
    """
    Loads the Steps associated with the Stage.
    :return: List of Step instances.
    """
    return self.load_children('steps', Step)

  def step(self, key:str) -> Step:
    """
    Finds the Step by key and inflates (instantiates) into a Step instance.
    :param key: identifier for desired Step.
    :return: Step instance.
    """
    return self.load_list_child('steps', Step, key)


def step_index(steps: List[Step], step_id: str) -> int:
  """
  Returns the index of the desired Step.
  :param steps: list of all Steps associated with a Stage.
  :param step_id: id to identify the desired Step.
  :return: index of the desired Step.
  """
  finder = (i for i, step in enumerate(steps) if step.key == step_id)
  return next(finder)

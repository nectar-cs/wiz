from typing import Dict, List

from wiz.model.base.wiz_model import WizModel, key_or_dict_to_key
from wiz.model.step.step import Step


class Stage(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.description = config.get('description')

  def first_step_key(self) -> str:
    step_descriptors = self.config.get('steps', [])
    first = step_descriptors[0] if len(step_descriptors) else 0
    return key_or_dict_to_key(first) if first else None

  def next_step_id(self, crt_step: Step, values: Dict[str, str]) -> str:
    if crt_step.has_explicit_next():
      return crt_step.next_step_id(values)
    else:
      stage_steps = self.steps()
      index = step_index(stage_steps, crt_step.key)
      is_not_last = index < len(stage_steps) - 1
      return stage_steps[index + 1].key if is_not_last else 'done'

  def steps(self):
    return self.load_children('steps', Step)

  def step(self, key):
    return self.load_child('steps', Step, key)


def step_index(steps: List[Step], step_id: str):
  finder = (i for i, step in enumerate(steps) if step.key == step_id)
  return next(finder)

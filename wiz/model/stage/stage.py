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

  def steps(self):
    return self.load_children('steps', Step)

  def step(self, key):
    return self.load_child('steps', Step, key)

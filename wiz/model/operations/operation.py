from wiz.model.step.step import Step
from wiz.model.base.wiz_model import WizModel, key_or_dict_to_key


class Operation(WizModel):

  def __init__(self, config):
    super().__init__(config)

  def first_stage_key(self) -> str:
    stage_descriptors = self.config.get('stages', [])
    first = stage_descriptors[0] if len(stage_descriptors) else 0
    return key_or_dict_to_key(first) if first else None

  def stages(self):
    return self.load_children('steps', Step)

  def stage(self, key):
    return self.load_child('steps', Step, key)

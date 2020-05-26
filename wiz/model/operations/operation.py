from wiz.model.stage.stage import Stage
from wiz.model.base.wiz_model import WizModel, key_or_dict_to_key


class Operation(WizModel):

  def first_stage_key(self) -> str:
    stage_descriptors = self.config.get('stages', [])
    first = stage_descriptors[0] if len(stage_descriptors) else 0
    return key_or_dict_to_key(first) if first else None

  def stages(self):
    return self.load_children('stages', Stage)

  def stage(self, key):
    return self.load_child('stages', Stage, key)

  def res_access(self):
    return self.config.get('res_access', [])

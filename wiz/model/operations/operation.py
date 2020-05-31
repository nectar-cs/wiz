from typing import List

from wiz.model.prerequisite.prerequisite import Prerequisite
from wiz.model.stage.stage import Stage
from wiz.model.base.wiz_model import WizModel, key_or_dict_to_key


class Operation(WizModel):

  def first_stage_key(self) -> str:
    stage_descriptors = self.config.get('stages', [])
    first = stage_descriptors[0] if len(stage_descriptors) else 0
    return key_or_dict_to_key(first) if first else None

  @property
  def is_system(self) -> bool:
    return self.key in ['install', 'uninstall']

  @property
  def synopsis(self) -> List[str]:
    return self.config.get('synopsis', [])

  @property
  def long_desc(self) -> str:
    return self.config.get('description', '')

  @property
  def risks(self) -> List[str]:
    return self.config.get('risks', [])

  def stages(self) -> List[Stage]:
    return self.load_children('stages', Stage)

  def stage(self, key) -> Stage:
    return self.load_child('stages', Stage, key)

  def prerequisites(self) -> List[Prerequisite]:
    return self.load_children('prerequisites', Prerequisite)

  def prerequisite(self, key) -> Prerequisite:
    return self.load_child('prerequisites', Prerequisite, key)

  def res_access(self):
    return self.config.get('res_access', [])


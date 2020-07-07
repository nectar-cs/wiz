from typing import List, Optional

from wiz.core.osr import OperationState
from wiz.model.prerequisite.prerequisite import Prerequisite
from wiz.model.stage.stage import Stage
from wiz.model.base.wiz_model import WizModel, key_or_dict_to_key


class Operation(WizModel):

  def first_stage_key(self) -> str:
    stage_descriptors = self.config.get('stages', [])
    first = stage_descriptors[0] if len(stage_descriptors) else 0
    return key_or_dict_to_key(first) if first else None

  def is_state_owner(self, op_state: OperationState) -> bool:
    return op_state.operation_id == self.key

  @classmethod
  def find_state_owner(cls, op_states: List[OperationState]):
    return next(filter(cls.is_state_owner, op_states))

  @property
  def is_system(self) -> bool:
    return self.key in ['installation', 'uninstall']

  @property
  def synopsis(self) -> List[str]:
    return self.config.get('synopsis', [])

  @property
  def long_desc(self) -> str:
    return self.config.get('description', '')

  @property
  def risks(self) -> List[str]:
    return self.config.get('risks', [])

  @property
  def affects_data(self):
    return self.config.get('affects_data', False)

  @property
  def affects_uptime(self):
    return self.config.get('affects_uptime', False)

  def stages(self) -> List[Stage]:
    return self.load_children('stages', Stage)

  def stage(self, key) -> Stage:
    return self.load_list_child('stages', Stage, key)

  def prerequisites(self) -> List[Prerequisite]:
    return self.load_children('prerequisites', Prerequisite)

  def prerequisite(self, key) -> Prerequisite:
    return self.load_list_child('prerequisites', Prerequisite, key)

  def res_access(self):
    return self.config.get('res_access', [])


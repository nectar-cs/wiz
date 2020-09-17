from typing import List, Optional, TypeVar

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import Input
from nectwiz.model.manifest_variable.manifest_variable import ManifestVariable

TARGET_CHART = 'chart'
TARGET_INLIN = 'inline'
TARGET_STATE = 'state'
TARGET_TYPES = [TARGET_CHART, TARGET_INLIN, TARGET_STATE]

T = TypeVar('T', bound='Field')

class Field(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.expl_option_descriptors = config.get('options')
    self.target = config.get('target', TARGET_CHART)
    self._manifest_variable = None

  def manifest_variable(self) -> Optional[ManifestVariable]:
    _id = self.config.get('chartVariableId')
    return ManifestVariable.inflate(_id) if _id else None

  def input_spec(self) -> Optional[Input]:
    return self.variable_spec().input_spec()

  def variable_spec(self) -> ManifestVariable:
    if not self._manifest_variable:
      self._manifest_variable = self.manifest_variable()
      if not self._manifest_variable:
        self._manifest_variable = ManifestVariable(self.config)
    return self._manifest_variable

  def input_type(self) -> Optional[str]:
    return self.input_spec().type()

  def options(self) -> List[dict]:
    return self.input_spec().options()

  def is_manifest_bound(self) -> bool:
    return self.is_chart_var() or self.is_inline_chart_var()

  def is_inline_chart_var(self) -> bool:
    return self.target == TARGET_INLIN

  def is_chart_var(self) -> bool:
    return self.target == TARGET_CHART

  def is_state_var(self) -> bool:
    return self.target == TARGET_STATE

  def needs_decorating(self) -> bool:
    return self.input_type == 'slider'

  def current_or_default(self) -> Optional[str]:
    current = config_man.mfst_vars(False).get(self.id())
    return current or self.default_value()

  def default_value(self) -> Optional[str]:
    return self.manifest_variable().default_value()

  def validate(self, value) -> List[Optional[str]]:
    for validator in self.validators():
      tone, message = validator.validate(value)
      if tone and message:
        return [tone, message]
    return [None, None]

  def sanitize_value(self, value):
    return value

  def decorate_value(self, value: str) -> Optional[any]:
    return None

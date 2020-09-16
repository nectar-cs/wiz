from typing import List, Optional, TypeVar

from nectwiz.core.core.utils import deep_get
from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.res_match_rule import ResMatchRule
from nectwiz.model.base.validator import Validator
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
    self.man_var_desc = config.get('chartVariable')
    self.expl_input_type = config.get('type', 'text-input')
    self.expl_option_descriptors = config.get('options')
    self.target = config.get('target', TARGET_CHART)
    self.expl_options_source = config.get('options_source', None)
    self.expl_default = config.get('default')
    self._manifest_variable = None
    self.expl_validation_descriptors = config.get('validations', [
      dict(type='presence')
    ])

  def manifest_variable(self) -> Optional[ManifestVariable]:
    if not self._manifest_variable:
      _id = self.config.get('chartVariableId') or self.config.get('id')
      if _id:
        self._manifest_variable = ManifestVariable.inflate(_id)
    return self._manifest_variable

  def input_spec(self) -> Optional[Input]:
    if self.config.get('input'):
      return Input.inflate(self.config.get('input'))
    elif self.manifest_variable():
      return self.manifest_variable().input_spec()
    else:
      return None

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
    if self.expl_default:
      return self.expl_default
    else:
      return self.manifest_variable().default_value
      tam_defaults = config_man.tam_defaults() or {}
      native_default = deep_get(tam_defaults, self.id().split("."))
      if native_default:
        return native_default
      elif self.input_type == 'select':
        options = self.options()
        return options[0].get('id') if len(options) > 0 else None
      else:
        return None

  def validators(self) -> List[Validator]:
    validation_configs = self.validation_descriptors
    return [Validator.inflate(c) for c in validation_configs]

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

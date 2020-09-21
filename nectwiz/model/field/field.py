from typing import List, Optional, TypeVar, Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import Input
from nectwiz.model.variables.generic_variable import GenericVariable

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
    self._delegate_variable = None

  def load_delegate_variable(self) -> Optional[GenericVariable]:
    _id = self.config.get('variable_id')
    return GenericVariable.inflate(_id) if _id else None

  def input_spec(self) -> Optional[Input]:
    return self.variable_spec().input_spec()

  def validate(self, value, context):
    return self.variable_spec().validate(value, context)

  def variable_spec(self) -> GenericVariable:
    if not self._delegate_variable:
      self._delegate_variable = self.load_delegate_variable()
      if not self._delegate_variable:
        self._delegate_variable = GenericVariable(self.config)
    return self._delegate_variable

  def input_type(self) -> Optional[str]:
    return self.input_spec().type()

  def options(self) -> List[Dict]:
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
    return self.load_delegate_variable().default_value()

  def compute_visibility(self) -> bool:
    predicate_kod = self.config.get('show_condition')
    if predicate_kod:
      predicate = Predicate.inflate(predicate_kod)
      return predicate.evaluate()
    else:
      return True

  def sanitize_value(self, value):
    return value

  def decorate_value(self, value: str) -> Optional[any]:
    return None

  @classmethod
  def inflate_with_key(cls, _id: str) -> T:
    is_kind = len(_id) > 0 and _id[0].isupper()
    if not is_kind:
      if not cls.id_exists(_id):
        return cls.inflate_with_config(dict(
          kind='Field',
          id=_id,
          variable_id=_id
        ))
    else:
      return super().inflate_with_key(_id)

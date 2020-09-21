from typing import List, Optional, TypeVar, Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import GenericInput
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.variables.generic_variable import GenericVariable

TARGET_CHART = 'chart'
TARGET_INLIN = 'inline'
TARGET_STATE = 'state'
TARGET_TYPES = [TARGET_CHART, TARGET_INLIN, TARGET_STATE]

T = TypeVar('T', bound='Field')

class Field(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self._delegate_variable = self.resolve_variable_spec()
    self.title = self._delegate_variable.title
    self.info = self._delegate_variable.info
    self.expl_option_descriptors = config.get('options')
    self.target = config.get('target', TARGET_CHART)

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

  def input_spec(self) -> Optional[GenericInput]:
    return self.resolve_variable_spec().input_spec()

  def validate(self, value: str, context: Dict):
    return self.resolve_variable_spec().validate(value, context)

  def resolve_variable_spec(self) -> GenericVariable:
    variable_id = self.config.get('variable_id')
    if variable_id:
      return GenericVariable.inflate(variable_id)
    else:
      return GenericVariable(self.config)

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

  def requires_decoration(self) -> bool:
    return self.input_spec().requires_decoration()

  def current_or_default(self) -> Optional[str]:
    current = config_man.mfst_vars(False).get(self.id())
    return current or self.default_value()

  def default_value(self) -> Optional[str]:
    return self.load_delegate_variable().default_value()

  def compute_visibility(self, context) -> bool:
    predicate_kod = self.config.get('show_condition')
    if predicate_kod:
      predicate: Predicate = Predicate.inflate(predicate_kod)
      return predicate.evaluate(context)
    else:
      return True

  def sanitize_value(self, value):
    return value

  def decorate_value(self, value: str) -> Optional[any]:
    return None

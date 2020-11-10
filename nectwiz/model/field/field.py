from typing import List, Optional, TypeVar, Dict

from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import GenericInput
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.variable.generic_variable import GenericVariable

TARGET_CHART = 'chart'
TARGET_INLIN = 'inline'
TARGET_STATE = 'state'
TARGET_PREFS = 'prefs'
TARGET_TYPES = [TARGET_CHART, TARGET_INLIN, TARGET_STATE, TARGET_PREFS]

T = TypeVar('T', bound='Field')

class Field(WizModel):

  def __init__(self, config: Dict):
    super().__init__(config)
    self._delegate_variable = self.resolve_variable_spec()
    self.title = self._delegate_variable.title
    self.info = self._delegate_variable.info
    self.expl_option_descriptors = config.get('options')
    self.target = config.get('target', TARGET_CHART)
    if not self._id:
      self._id = self._delegate_variable.id()

  def input_spec(self) -> Optional[GenericInput]:
    return self._delegate_variable.input_spec()

  def validate(self, value: str, context: Dict):
    return self._delegate_variable.validate(value, context)

  def resolve_variable_spec(self) -> GenericVariable:
    variable_kod = self.config.get('variable')
    if variable_kod:
      return GenericVariable.inflate(variable_kod)
    else:
      return GenericVariable(self.config)

  def delegate_variable(self):
    return self._delegate_variable

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

  def current_or_default(self) -> Optional[str]:
    current = config_man.manifest_vars().get(self.id())
    return current or self.default_value()

  def default_value(self) -> Optional[str]:
    return self._delegate_variable.default_value()

  def compute_visibility(self, context: Dict) -> bool:
    predicate_kod = self.config.get('show_condition')
    if predicate_kod:
      predicate: Predicate = Predicate.inflate(predicate_kod)
      return predicate.evaluate(context)
    else:
      return True

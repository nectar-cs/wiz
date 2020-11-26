from typing import List, Optional, TypeVar, Dict

from werkzeug.utils import cached_property

from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import PredEval
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.variable.generic_variable import GenericVariable

T = TypeVar('T', bound='Field')

class Field(WizModel):

  TARGET_KEY = 'target'
  VARIABLE_KEY = 'variable'
  SHOW_CONDITION_KEY = 'show_condition'

  TARGET_CHART = 'chart'
  TARGET_INLIN = 'inline'
  TARGET_STATE = 'state'
  TARGET_PREFS = 'prefs'

  TARGET_TYPES = [TARGET_CHART, TARGET_INLIN, TARGET_STATE, TARGET_PREFS]
  DEFAULT_TARGET = TARGET_CHART

  @cached_property
  def variable(self) -> GenericVariable:
    """
    Inflate child variable using 'variable' KoD or own configuration
    if 'variable' not defined.
    @return: GenericVariable instance
    """
    return self.inflate_child(
      GenericVariable,
      prop=self.VARIABLE_KEY,
      safely=True
    ) or GenericVariable({'id': self.id()})

  @cached_property
  def show_condition_predicate(self) -> Predicate:
    return self.inflate_child(
      Predicate,
      prop=self.SHOW_CONDITION_KEY,
      safely=True
    )

  @cached_property
  def title(self) -> str:
    return self.get_prop(self.TITLE_KEY) or self.variable.title

  @cached_property
  def info(self) -> str:
    return self.get_prop(self.INFO_KEY) or self.variable.info

  @cached_property
  def target(self):
    return self.get_prop(self.TARGET_KEY, self.DEFAULT_TARGET)

  def validate(self, value: str) -> PredEval:
    """
    Delegates validate() to child GenericVariable.
    @param value: value to use as challenge in child Predicate
    @return: PredEval result
    """
    return self.variable.validate(value)

  def default_value(self) -> Optional[str]:
    return self.variable.default_value()

  def compute_visibility(self) -> bool:
    if self.show_condition_predicate:
      return self.show_condition_predicate.evaluate()
    return True

  def current_or_default(self) -> Optional[str]:
    current = config_man.manifest_vars().get(self.id())
    return current or self.default_value()

  def serialize_options(self) -> List[Dict]:
    return self.variable.input_model.serialize_options()

  def is_manifest_bound(self) -> bool:
    return self.is_chart_var() or self.is_inline_chart_var()

  def is_inline_chart_var(self) -> bool:
    return self.target == self.TARGET_INLIN

  def is_chart_var(self) -> bool:
    return self.target == self.TARGET_CHART

  def is_state_var(self) -> bool:
    return self.target == self.TARGET_STATE


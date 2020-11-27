from typing import List, TypeVar, Dict

from werkzeug.utils import cached_property

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
    Inflate child variable using 'variable' KoD. If not present,
    construct synthetic GenericVariable using own config.
    @return: GenericVariable instance
    """
    return self.inflate_child(
      GenericVariable,
      prop=self.VARIABLE_KEY,
      safely=True
    ) or self.inflate_child(
      GenericVariable,
      kod=self.variable_bound_config_subset()
    )

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

  def variable_bound_config_subset(self):
    pool = self.config.items()
    relevant = GenericVariable.COPYABLE_KEYS
    return {k: v for k, v in pool if k in relevant}

  def compute_visibility(self) -> bool:
    print(f"My Turn {self.id()}")
    if self.show_condition_predicate:
      return self.show_condition_predicate.evaluate()
    return True

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

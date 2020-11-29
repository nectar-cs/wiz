from typing import Any, Dict

from werkzeug.utils import cached_property

from nectwiz.core.core import subs
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.operation.operation_state import OperationState
from nectwiz.model.predicate.common_predicates import TruePredicate
from nectwiz.model.predicate.predicate import Predicate


class VariableValueDecorator(WizModel):

  KEY_TEMPLATE = 'template'
  SHOW_COND_KEY = 'show_condition'

  @cached_property
  def output_template(self) -> str:
    return self.get_prop(self.KEY_TEMPLATE, '')

  @cached_property
  def show_condition(self):
    return self.inflate_child(
      Predicate,
      prop=self.SHOW_COND_KEY,
      safely=True
    ) or self.gen_default_show_condition()

  def gen_default_show_condition(self) -> Predicate:
    return self.inflate_child(Predicate, kod=TruePredicate.__name__)

  def compute_visibility(self) -> bool:
    return self.show_condition.evaluate()

  def decorate(self, value: Any, operation_state: OperationState) -> Any:
    subs2 = self.compute(value, operation_state) or {}
    print(f"CONT {subs2}")
    return subs.interp(self.output_template, subs2)

  def compute(self, value: Any, operation_state: OperationState) -> Dict:
    return {}

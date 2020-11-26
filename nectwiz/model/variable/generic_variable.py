from functools import lru_cache
from typing import List, TypeVar, Optional, Any

from werkzeug.utils import cached_property

from nectwiz.core.core.types import PredEval
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import GenericInput
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.variable.variable_value_decorator import VariableValueDecorator

T = TypeVar('T', bound='ManifestVariable')

validations_key = 'validation'

class GenericVariable(WizModel):

  DEFAULT_VALUE_KEY = 'default'
  DECORATOR_KEY = 'decorator'
  INPUT_MODEL_KEY = 'input'
  VALIDATION_PREDS_KEY = 'validation'

  @cached_property
  def default_value(self) -> Optional[Any]:
    return self.get_prop(self.DEFAULT_VALUE_KEY)

  @cached_property
  def input_model(self) -> GenericInput:
    return self.inflate_child(
      GenericInput,
      prop=self.INPUT_MODEL_KEY
    )

  @cached_property
  def value_decorator(self) -> VariableValueDecorator:
    return self.inflate_child(
      VariableValueDecorator,
      prop=self.DECORATOR_KEY
    )

  @lru_cache(maxsize=5)
  def value_injected_validators(self, value) -> List[Predicate]:
    value = self.sanitize_for_validation(value)
    patch = dict(challenge=value, context=dict(value=value))

    return self.inflate_children(
      Predicate,
      prop=self.VALIDATION_PREDS_KEY,
      patches=patch
    )

  def validate(self, value: Any) -> PredEval:
    for predicate in self.value_injected_validators(value):
      if not predicate.evaluate():
        return PredEval(
          predicate_id=predicate.id(),
          met=False,
          reason=predicate.reason,
          tone=predicate.tone
        )
    return PredEval(
      met=True,
      tone='',
      reason=''
    )

  def sanitize_for_validation(self, value: Any) -> Any:
    return self.input_model.sanitize_for_validation(value)

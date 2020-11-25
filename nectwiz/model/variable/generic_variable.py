from functools import lru_cache
from typing import List, TypeVar, Optional, Any

from nectwiz.core.core.types import PredEval
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import GenericInput
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.variable.variable_value_decorator import VariableValueDecorator

T = TypeVar('T', bound='ManifestVariable')

validations_key = 'validation'

class GenericVariable(WizModel):
  def __init__(self, config):
    super().__init__(config)
    self.explicit_default: str = config.get('default')
    self.decorator_kod: str = config.get('value_decorator')
    self.validation_predicate_kods: List[str] = config.get('validation')

  @lru_cache(maxsize=1)
  def input_spec(self) -> GenericInput:
    kod = self.config.get('input', GenericInput.__name__)
    return GenericInput.inflate(kod)

  @lru_cache(maxsize=1)
  def validators(self) -> List[Predicate]:
    return self.inflate_children('validation', Predicate)

  def default_value(self) -> str:
    return self.explicit_default

  @lru_cache(maxsize=1)
  def value_decorator(self) -> Optional[VariableValueDecorator]:
    if self.decorator_kod:
      return VariableValueDecorator.inflate(self.decorator_kod)

  def validate(self, value: any) -> PredEval:
    value = self.sanitize_for_validation(value)
    patch = dict(challenge=value, context=dict(value=value))
    for predicate_kod in self.validation_predicate_kods:
      predicate = self.inflate_child(Predicate, predicate_kod, patch)
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
    return self.input_spec().sanitize_for_validation(value)

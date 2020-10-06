from typing import List, TypeVar, Dict, Optional

from nectwiz.core.core.types import PredEval, KoD
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import GenericInput
from nectwiz.model.predicate.predicate import Predicate
from nectwiz.model.variable.variable_value_decorator import VariableValueDecorator

T = TypeVar('T', bound='ManifestVariable')

class GenericVariable(WizModel):
  def __init__(self, config):
    super().__init__(config)
    self.explicit_default: str = config.get('default')
    self.decorator_desc: str = config.get('value_decorator')

  def input_spec(self) -> GenericInput:
    kod = self.config.get('input', GenericInput.__name__)
    return GenericInput.inflate(kod)

  def validators(self) -> List[Predicate]:
    return self.load_children('validation', Predicate)

  def default_value(self) -> str:
    return self.explicit_default

  def value_decorator(self) -> Optional[VariableValueDecorator]:
    if self.decorator_desc:
      return VariableValueDecorator.inflate(self.decorator_desc)

  def validate(self, value: any, context: Dict) -> PredEval:
    context = dict(**context, value=value)
    for predicate in self.validators():
      if not predicate.evaluate(context):
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

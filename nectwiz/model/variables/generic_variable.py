from typing import List, TypeVar, Dict

from nectwiz.core.core.types import PredEval
from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import GenericInput
from nectwiz.model.predicate.predicate import Predicate

T = TypeVar('T', bound='ManifestVariable')

class GenericVariable(WizModel):
  def __init__(self, config):
    super().__init__(config)
    self.data_type: str = config.get('type', 'string')
    self.explicit_default: str = config.get('default')

  def input_spec(self) -> GenericInput:
    return GenericInput.inflate(self.config.get('input'))

  def validators(self) -> List[Predicate]:
    return self.load_children('validation', Predicate)

  def default_value(self) -> str:
    return self.explicit_default

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
    return PredEval(met=True)

from typing import Optional, List, TypeVar

from nectwiz.model.base.wiz_model import WizModel
from nectwiz.model.input.input import Input
from nectwiz.model.predicate.predicate import Predicate

T = TypeVar('T', bound='ManifestVariable')

class GenericVariable(WizModel):
  def __init__(self, config):
    super().__init__(config)
    self.data_type: str = config.get('type', 'string')
    self.explicit_default: str = config.get('default')

  def input_spec(self) -> Input:
    return Input.inflate(self.config.get('input'))

  def validators(self) -> List[Predicate]:
    return self.load_children('validations', Predicate)

  def default_value(self) -> str:
    return self.explicit_default

  def validate(self, value, context) -> List[Optional[str]]:
    context = dict(value=value, **context)
    for predicate in self.validators():
      if not predicate.evaluate(context):
        return [predicate.tone, predicate.reason]
    return [None, None]

from wiz.core.wiz_globals import wiz_globals
from wiz.model.field.validator import Validator
from wiz.model.wiz_model import WizModel


class Field(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.options = config.get('options')

  def validators(self):
    return [Validator.inflate(c) for c in self.config['on']]

  def validate(self, value):
    for validator in self.validators():
      tone, message = validator.validate(value)
      if tone and message:
        return [tone, message]
    return None

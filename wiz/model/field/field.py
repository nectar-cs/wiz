from wiz.model.field.validator import Validator
from wiz.model.base.wiz_model import WizModel


class Field(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.options = config.get('options')

  def validators(self):
    validation_configs = self.config.get('validations', [])
    return [Validator.inflate(c) for c in validation_configs]

  def validate(self, value):
    for validator in self.validators():
      tone, message = validator.validate(value)
      if tone and message:
        return [tone, message]
    return [None, None]

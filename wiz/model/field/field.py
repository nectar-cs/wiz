from wiz.core.wiz_globals import wiz_globals
from wiz.model.field.validator import Validator

class Field:

  def __init__(self, config):
    self.config = config
    self.options = config['options']

  def validators(self):
    return [Validator.inflate(c) for c in self.config['on']]

  def validate(self, value):
    for validator in self.validators():
      tone, message = validator.validate(value)
      if tone and message:
        return [tone, message]
    return None

  @classmethod
  def inflate(cls, config):
    custom_subclass = wiz_globals.step_class(config['key'])
    host_class = custom_subclass or cls
    return host_class(config)

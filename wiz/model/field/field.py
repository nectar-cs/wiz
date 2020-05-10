from wiz.model.field.validator import Validator
from wiz.model.base.wiz_model import WizModel


class Field(WizModel):

  def __init__(self, config):
    super().__init__(config)

  @property
  def type(self):
    return self.config['type']

  @property
  def options(self):
    return self.config.get('options')

  @property
  def info(self):
    return self.config.get('info')

  def default_value(self):
    return self.config.get('default')

  @property
  def watch_res_kinds(self):
    declared = self.config.get('res_watch', [])
    return list(set(declared + ['ConfigMap']))

  @property
  def is_inline(self):
    return self.config.get('inline', False)

  def validators(self):
    validation_configs = self.config.get('validations', [])
    return [Validator.inflate(c) for c in validation_configs]

  def validate(self, value):
    for validator in self.validators():
      tone, message = validator.validate(value)
      if tone and message:
        return [tone, message]
    return [None, None]

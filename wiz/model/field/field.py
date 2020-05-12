from typing import List, Optional

from wiz.model.field.validator import Validator
from wiz.model.base.wiz_model import WizModel


class Field(WizModel):

  def __init__(self, config):
    super().__init__(config)

  @property
  def type(self):
    return self.config.get('type', 'text-input')

  @property
  def validation_descriptors(self):
    return self.config.get('validations', [
      dict(type='presence')
    ])

  @property
  def options(self):
    return self.config.get('options')

  @property
  def info(self):
    return self.config.get('info')

  @property
  def watch_res_kinds(self):
    declared = self.config.get('res_watch', [])
    return list(set(declared + ['ConfigMap']))

  @property
  def is_inline(self):
    return self.config.get('inline', False)

  def default_value(self):
    return self.config.get('default')

  def validators(self):
    validation_configs = self.validation_descriptors
    return [Validator.inflate(c) for c in validation_configs]

  def validate(self, value) -> List[Optional[str]]:
    for validator in self.validators():
      tone, message = validator.validate(value)
      if tone and message:
        return [tone, message]
    return [None, None]

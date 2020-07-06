from functools import reduce
from typing import List, Optional

from wiz.model.base.res_match_rule import ResMatchRule
from wiz.model.base.validator import Validator
from wiz.model.base.wiz_model import WizModel

TARGET_CHART = 'chart'
TARGET_INLINE = 'inline'
TARGET_STATE = 'state'

class Field(WizModel):

  @property
  def type(self):
    return self.config.get('type', 'text-input')

  @property
  def validation_descriptors(self):
    return self.config.get('validations', [
      dict(type='presence')
    ])

  @property
  def option_descriptors(self):
    return self.config.get('options')

  @property
  def target(self):
    return self.config.get('target', 'chart')

  @property
  def options_source(self):
    return self.config.get('options_source', None)

  def options(self):
    if self.options_source:
      _type = self.options_source.get('type')
      if _type == 'select-k8s-res':
        rule_descriptors = self.options_source.get('res_match_rules', [])
        rules = [ResMatchRule(rd) for rd in rule_descriptors]
        res_list = reduce(lambda whole, rule: whole + rule.query(), rules, [])
        return [{'key': r.name, 'value': r.name} for r in res_list]
      else:
        raise RuntimeError(f"Can't process source {type}")
    else:
      return self.option_descriptors

  def is_manifest_bound(self):
    return self.is_chart_var or self.is_inline_chart_var

  @property
  def is_inline_chart_var(self):
    return self.target == 'inline'

  @property
  def is_chart_var(self):
    return self.target == 'chart'

  @property
  def is_state_var(self):
    return self.target == 'state'

  def needs_decorating(self):
    return self.config.get('type') == 'slider'

  def default_value(self):
    explicit_default = self.config.get('default')
    if not explicit_default and self.type == 'select':
      options = self.options()
      return options[0]['key'] if len(options) > 0 else None
    else:
      return explicit_default

  def validators(self):
    validation_configs = self.validation_descriptors
    return [Validator.inflate(c) for c in validation_configs]

  def validate(self, value) -> List[Optional[str]]:
    for validator in self.validators():
      tone, message = validator.validate(value)
      if tone and message:
        return [tone, message]
    return [None, None]

  def sanitize_value(self, value):
    return value

  def decorate_value(self, value: str) -> Optional[any]:
    return None

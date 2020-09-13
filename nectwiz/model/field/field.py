from typing import List, Optional

from nectwiz.core.core.utils import deep_get
from nectwiz.core.core.config_man import config_man
from nectwiz.model.base.res_match_rule import ResMatchRule
from nectwiz.model.base.validator import Validator
from nectwiz.model.base.wiz_model import WizModel


TARGET_CHART = 'chart'
TARGET_INLIN = 'inline'
TARGET_STATE = 'state'
TARGET_TYPES = [TARGET_CHART, TARGET_INLIN, TARGET_STATE]


class Field(WizModel):

  def __init__(self, config):
    super().__init__(config)
    self.input_type = config.get('type', 'text-input')
    self.option_descriptors = config.get('options')
    self.target = config.get('target', TARGET_CHART)
    self.options_source = config.get('options_source', None)
    self.expl_default = config.get('default')
    self.validation_descriptors = config.get('validations', [
      dict(type='presence')
    ])

  def options(self) -> List[dict]:
    if self.options_source:
      _type = self.options_source.get('type')
      if _type == 'select-k8s-res':
        rule_descriptors = self.options_source.get('res_match_rules', [])
        rules = [ResMatchRule(rd) for rd in rule_descriptors]
        res_list = set(sum([rule.query() for rule in rules], []))
        return [{'id': r.name, 'value': r.name} for r in res_list]
      else:
        raise RuntimeError(f"Can't process source {type}")
    else:
      return self.option_descriptors

  def is_manifest_bound(self) -> bool:
    return self.is_chart_var() or self.is_inline_chart_var()

  def is_inline_chart_var(self) -> bool:
    return self.target == TARGET_INLIN

  def is_chart_var(self) -> bool:
    return self.target == TARGET_CHART

  def is_state_var(self) -> bool:
    return self.target == TARGET_STATE

  def needs_decorating(self) -> bool:
    return self.input_type == 'slider'

  def current_or_default(self) -> Optional[str]:
    current = config_man.mfst_vars(False).get(self.id())
    return current or self.default_value()

  def default_value(self) -> Optional[str]:
    if self.expl_default:
      return self.expl_default
    else:
      tam_defaults = config_man.tam_defaults() or {}
      native_default = deep_get(tam_defaults, self.id().split("."))
      if native_default:
        return native_default
      elif self.input_type == 'select':
        options = self.options()
        return options[0].get('id') if len(options) > 0 else None
      else:
        return None

  def validators(self) -> List[Validator]:
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

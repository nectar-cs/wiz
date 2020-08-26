from functools import reduce
from typing import List, Optional

from nectwiz.model.base.res_match_rule import ResMatchRule
from nectwiz.model.base.validator import Validator
from nectwiz.model.base.wiz_model import WizModel

TARGET_CHART = 'chart'
TARGET_INLINE = 'inline'
TARGET_STATE = 'state'
TARGET_TYPES = [TARGET_CHART, TARGET_INLINE, TARGET_STATE]

class Field(WizModel):

  @property
  def type(self) -> str:
    """
    Getter for Field type. Defaults to "text-input" if unspecified.
    :return: Field type.
    """
    return self.config.get('type', 'text-input')

  @property
  def validation_descriptors(self) -> List[dict]:
    """
    Getter for Validation descriptors associated with a Field.
    :return: list of Validation descriptors.
    """
    return self.config.get('validations', [
      dict(type='presence')
    ])

  @property
  def option_descriptors(self) -> List[str]:
    """
    Getter for Option descriptors.
    :return: list of Option descriptors.
    """
    return self.config.get('options')

  @property
  def target(self) -> str:
    """
    Getter for the Field's target property. Defaults to chart if unspecified.
    :return: Field's target property.
    """
    return self.config.get('target', TARGET_CHART)

  @property
  def options_source(self) -> str:
    """
    Getter for the Field's options source.
    :return: Field's option source if available, else None.
    """
    return self.config.get('options_source', None)

  def options(self) -> List[dict]:
    """
    If the Field has an option source, prepares the options list which consists
    of k8s resources.
    :return: list of k8s resources as dicts.
    """
    if self.options_source:
      _type = self.options_source.get('type')
      if _type == 'select-k8s-res':
        rule_descriptors = self.options_source.get('res_match_rules', [])
        rules = [ResMatchRule(rd) for rd in rule_descriptors]
        res_list = set(sum([rule.query() for rule in rules], []))
        return [{'key': r.name, 'value': r.name} for r in res_list]
      else:
        raise RuntimeError(f"Can't process source {type}")
    else:
      return self.option_descriptors

  def is_manifest_bound(self) -> bool:
    """
    Checks if the variable should be recorded in the manifest.
    :return: True if it should, False otherwise.
    """
    return self.is_chart_var or self.is_inline_chart_var

  def is_inline_chart_var(self) -> bool:
    """
    Checks if the Field is an inline variable.
    :return: True if it is, False otherwise.
    """
    return self.target == TARGET_INLINE

  def is_chart_var(self) -> bool:
    """
    Checks if the Field is a chart variable.
    :return: True if it is, False otherwise.
    """
    return self.target == TARGET_CHART

  def is_state_var(self) -> bool:
    """
    Checks if the Field is a state variable.
    :return: True if it is, False otherwise.
    """
    return self.target == TARGET_STATE

  def needs_decorating(self) -> bool:
    """
    Checks if the Field is of type "slider" and thus needs decorating.
    :return: True if does, False otherwise.
    """
    return self.config.get('type') == 'slider'

  def default_value(self) -> str:
    """
    Prepares the default value for a field. Uses the explicitly defined one if
    that exists, otherwise simply uses the first option.
    :return: string with default value.
    """
    explicit_default = self.config.get('default')
    if not explicit_default and self.type == 'select':
      options = self.options()
      return options[0]['key'] if len(options) > 0 else None
    else:
      return explicit_default

  def validators(self) -> List[Validator]:
    """
    Returns a list of inflated Validators associated with a Field.
    :return: list of Validators.
    """
    validation_configs = self.validation_descriptors
    return [Validator.inflate(c) for c in validation_configs]

  def validate(self, value) -> List[Optional[str]]:
    """
    Validates the value in the Field against each Validator in the associated
    Validator list.
    :param value: value to be checked.
    :return: list with [tone, message] if at least one Validator returns
    non-empty, else [None, None].
    """
    for validator in self.validators():
      tone, message = validator.validate(value)
      if tone and message:
        return [tone, message]
    return [None, None]

  def sanitize_value(self, value):
    return value

  def decorate_value(self, value: str) -> Optional[any]:
    return None

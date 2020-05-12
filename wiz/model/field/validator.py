import re
from typing import Dict


class Validator:
  def __init__(self, config: Dict[str, any]):
    self.config = config

  @property
  def check(self):
    return str(self.config.get('check_against', '')).lower()

  @property
  def message(self):
    return str(self.config.get('message'))

  @property
  def tone(self):
    return self.config.get('tone', 'error').lower()

  def perform(self, value) -> bool:
    raise NotImplementedError

  def validate(self, value):
    if self.perform(value):
      return [self.tone, self.message]
    else:
      return [None, None]

  @classmethod
  def inflate(cls, config) -> 'Validator':
    _type = config['type']
    if _type == 'equality':
      return EqValidator(config)
    elif _type == 'inequality':
      return NeqValidator(config)
    elif _type == 'presence':
      return PresenceValidator(config)
    elif _type == 'format':
      return FormatValidator(config)
    else:
      raise RuntimeError(f"Don't know validation type {_type}")


class EqValidator(Validator):
  def perform(self, value):
    return self.check == str(value).lower()


class NeqValidator(EqValidator):
  def perform(self, value):
    return not super().perform(value)


class PresenceValidator(Validator):
  @property
  def message(self):
    return self.config.get('message', 'Cannot be empty')

  @property
  def check(self):
    given = str(self.config.get('check_against', 'True')).lower()
    return given == 'true'

  def perform(self, value):
    if self.check:
      return not bool(value)
    else:
      return bool(value)


class FormatValidator(Validator):
  @property
  def message(self):
    default = f'Must be {self.inflection()} {self.check}'
    return self.config.get('message', default)

  def inflection(self):
    return 'an' if self.check in ['integer', 'email'] else 'a'

  def perform(self, value):
    if self.check == 'integer':
      return not value.isdigit()
    elif self.check == 'boolean':
      return value not in ['true', 'false']
    elif self.check == 'email':
      return not re.search(r"^\S+@\S+\.\S+$", value)
    else:
      raise RuntimeError(f"NO ADAPTER FOR {self.check}")
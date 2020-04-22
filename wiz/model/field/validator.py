from typing import Dict


class Validator:
  def __init__(self, config: Dict[str, any]):
    self.check = str(config['check_against']).lower()
    self.message = config.get('message')
    self.tone = config.get('tone', 'error').lower()

    if self.tone not in ['warning', 'error']:
      raise RuntimeError(f'Tone must be warning or error, got {self.tone}')

  def perform(self, value):
    raise NotImplementedError

  def validate(self, value):
    if self.perform(value):
      return [self.tone, self.message]
    else:
      return [None, None]

  @classmethod
  def inflate(cls, config):
    _type = config['type']
    if _type == 'equality':
      return EqValidator(config)
    elif _type == 'inequality':
      return NeqValidator(config)
    else:
      raise RuntimeError(f"Don't know validation type {_type}")

class EqValidator(Validator):
  def perform(self, value):
    return self.check == str(value).lower()

class NeqValidator(EqValidator):
  def perform(self, value):
    return not super().perform(value)

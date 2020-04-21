from typing import Dict

from wiz.model.step_state import StepState


def validate_custom_classes(classes):
  for concern_class in classes:
    if not concern_class.key():
      raise RuntimeError('Concern key must provide a key()')

  keys = [c.key() for c in classes]
  duplicates = set([x for x in keys if keys.count(x) > 1])
  if duplicates:
    raise RuntimeError(f'Duplicate keys found: {duplicates}')


def find_class(candidates, key: str):
  matches = [c for c in candidates if c.key == key]
  return matches[0] if len(matches) else None


def find_config(candidates, key):
  matches = [config for config in candidates if config['key'] == key]
  return matches[0] if len(matches) == 1 else None


class WizGlobals:

  def __init__(self, ):
    self.concern_configs = []
    self.step_configs = []
    self.field_configs = []
    self.concern_classes = []
    self.step_classes = []
    self.field_classes = []
    self.step_state = StepState({})

  def set_configs(self, **kwargs):
    self.concern_configs = kwargs.get('concerns')
    self.step_configs = kwargs.get('steps')
    self.field_configs = kwargs.get('fields')

  def set_subclasses(self, **kwargs):
    self.concern_classes = kwargs.get('concerns')
    self.step_classes = kwargs.get('steps')
    self.field_classes = kwargs.get('fields')

  def concern_config(self, key):
    return find_config(self.concern_configs, key)

  def step_config(self, key):
    return find_config(self.step_configs, key)

  def field_config(self, key):
    return find_config(self.field_configs, key)

  def concern_class(self, key: str):
    return find_class(self.concern_classes, key)

  def step_class(self, key: str):
    return find_class(self.step_classes, key)


wiz_globals = WizGlobals()
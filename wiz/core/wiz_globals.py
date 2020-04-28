from typing import Dict


def validate_custom_classes(classes):
  for concern_class in classes:
    if not concern_class.key():
      raise RuntimeError('Concern key must provide a key()')

  keys = [c.key() for c in classes]
  duplicates = set([x for x in keys if keys.count(x) > 1])
  if duplicates:
    raise RuntimeError(f'Duplicate keys found: {duplicates}')


def category_default() -> Dict[str, any]:
  return dict(concerns=[], steps=[], fields=[])


class WizGlobals:

  def __init__(self):
    self.ns = None
    self.configs = category_default()
    self.subclasses = category_default()

  def set_configs(self, **kwargs):
    self.configs = {**category_default(), **kwargs}

  def set_subclasses(self, **kwargs):
    self.subclasses = {**category_default(), **kwargs}

  def find_config(self, category, key: str):
    candidates = self.configs[category]
    matches = [config for config in candidates if config['key'] == key]
    return matches[0] if len(matches) else None

  def find_subclass(self, category, key: str):
    candidates = self.subclasses[category]
    matches = [config for config in candidates if config.key() == key]
    return matches[0] if len(matches) else None

  def clear(self):
    self.configs = category_default()
    self.subclasses = category_default()


wiz_globals = WizGlobals()

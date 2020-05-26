from typing import Type, Optional, Dict

import inflection

from wiz.core.wiz_globals import wiz_app


class WizModel:

  def __init__(self, config):
    self.config = config
    self.key = config['key']

  @property
  def title(self):
    return self.config.get('title')

  @property
  def info(self):
    return self.config.get('info')

  def load_children(self, config_key, child_class):
    descriptor_list = self.config.get(config_key, [])
    transform = lambda obj: key_or_dict_to_child(obj, child_class)
    return [transform(obj) for obj in descriptor_list]

  def load_child(self, config_key, child_class, child_key):
    descriptor_list = self.config.get(config_key, [])
    predicate = lambda obj: key_or_dict_matches(obj, child_key)
    matches = [obj for obj in descriptor_list if predicate(obj)]
    match = matches[0] if len(matches) > 0 else None
    return key_or_dict_to_child(match, child_class) if match else None

  @classmethod
  def inflate_with_config(cls, config: Dict) -> Optional['WizModel']:
    subclass = wiz_app.find_subclass(cls.type_key(), config['key'])
    host_class = subclass or cls
    return host_class(config)

  @classmethod
  def inflate_with_key(cls, key: str) -> Optional['WizModel']:
    config = wiz_app.find_config(cls.type_key(), key)
    return cls.inflate_with_config(config)

  @classmethod
  def inflate_all(cls):
    configs = wiz_app.configs_of_kind(cls.type_key())
    return [cls.inflate_with_config(config) for config in configs]

  @classmethod
  def inflate(cls, key_or_dict) -> Optional['WizModel']:
    if isinstance(key_or_dict, str):
      return cls.inflate_with_key(key_or_dict)
    elif isinstance(key_or_dict, Dict):
      return cls.inflate_with_config(key_or_dict)
    raise RuntimeError(f"Bad input {key_or_dict}")

  @classmethod
  def type_key(cls):
    return f"{inflection.underscore(cls.__name__)}"


def key_or_dict_to_key(key_or_dict) -> str:
  if isinstance(key_or_dict, str):
    return key_or_dict

  elif isinstance(key_or_dict, dict):
    return key_or_dict['key']

  raise RuntimeError(f"Can't handle {key_or_dict}")


def key_or_dict_matches(key_or_dict, target_key: str) -> bool:
  return key_or_dict_to_key(key_or_dict) == target_key

def key_or_dict_to_child(key_or_dict, child_cls: Type[WizModel]) -> 'WizModel':
  return child_cls.inflate(key_or_dict)

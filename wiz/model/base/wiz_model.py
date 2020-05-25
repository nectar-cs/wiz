from typing import Type

from wiz.core.wiz_globals import wiz_globals


class WizModel:

  def __init__(self, config):
    self.config = config
    self.key = config['key']
    self.title = config.get('title')

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
  def inflate(cls, key, config=None):
    if not config:
      config = wiz_globals.find_config(cls.type_key(), key)

    subclass = wiz_globals.find_subclass(cls.type_key(), key)
    host_class = subclass or cls
    return host_class(config)

  @classmethod
  def inflate_all(cls):
    keys = [c['key'] for c in wiz_globals.configs[cls.type_key()]]
    return [cls.inflate(key) for key in keys]

  @classmethod
  def type_key(cls):
    return f'{cls.__name__.lower()}s'


def key_or_dict_matches(key_or_dict, target_key: str) -> bool:
  if isinstance(key_or_dict, str):
    return key_or_dict == target_key

  elif isinstance(key_or_dict, dict):
    return key_or_dict.get('key') == target_key

  raise RuntimeError(f"Can't handle {key_or_dict}")


def key_or_dict_to_child(key_or_dict, child_cls: Type[WizModel]) -> 'WizModel':
  if isinstance(key_or_dict, str):
    return child_cls.inflate(
      key=key_or_dict
    )

  elif isinstance(key_or_dict, dict):
    return child_cls.inflate(
      key=key_or_dict.get('key'),
      config=key_or_dict
    )

  raise RuntimeError(f"Can't handle {key_or_dict}")

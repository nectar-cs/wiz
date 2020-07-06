from typing import Type, Optional, Dict, Union

from wiz.core.wiz_globals import wiz_app


class WizModel:

  def __init__(self, config: Dict):
    self.config: Dict = config
    self.key: str = config['key']
    self.parent = None

  @property
  def title(self):
    return self.config.get('title')

  @property
  def info(self):
    return self.config.get('info')

  def load_children(self, config_key, child_class):
    descriptor_list = self.config.get(config_key, [])
    if not isinstance(descriptor_list, list):
      descriptor_list = [descriptor_list]
    transform = lambda obj: key_or_dict_to_child(obj, child_class, self)
    return [transform(obj) for obj in descriptor_list]

  def load_list_child(self, config_key, child_class, child_key):
    descriptor_list = self.config.get(config_key, [])
    predicate = lambda obj: key_or_dict_matches(obj, child_key)
    match = next((obj for obj in descriptor_list if predicate(obj)), None)
    return self.load_child(child_class, match) if match else None

  def load_child(self, child_class, key_or_dict: Union[str, Dict]):
    return key_or_dict_to_child(key_or_dict, child_class, self)

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
  def inflate(cls, key_or_dict: Union[str, Dict]) -> Optional['WizModel']:
    if isinstance(key_or_dict, str):
      return cls.inflate_with_key(key_or_dict)
    elif isinstance(key_or_dict, Dict):
      return cls.inflate_with_config(key_or_dict)
    raise RuntimeError(f"Bad input {key_or_dict}")

  @classmethod
  def type_key(cls):
    return f"{cls.__name__}"


def key_or_dict_to_key(key_or_dict) -> str:
  if isinstance(key_or_dict, str):
    return key_or_dict

  elif isinstance(key_or_dict, dict):
    return key_or_dict['key']

  raise RuntimeError(f"Can't handle {key_or_dict}")


def key_or_dict_matches(key_or_dict, target_key: str) -> bool:
  return key_or_dict_to_key(key_or_dict) == target_key


def key_or_dict_to_child(key_or_dict, child_cls: Type[WizModel], parent=None) -> 'WizModel':
  inflated = child_cls.inflate(key_or_dict)
  inflated.parent = parent
  return inflated

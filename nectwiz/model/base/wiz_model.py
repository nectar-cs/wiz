from typing import Type, Optional, Dict, Union, List, TypeVar

from nectwiz.core.core.wiz_app import wiz_app


T = TypeVar('T', bound='WizModel')


class WizModel:

  def __init__(self, config: Dict):
    self.config: Dict = config
    self.key: str = config.get('id')
    self.parent = None

  def id(self):
    return self.key

  @property
  def title(self):
    return self.config.get('title')

  @property
  def info(self):
    return self.config.get('info')

  def load_children(self, config_key:str , child_class:Type[T]) -> List[T]:
    descriptor_list = self.config.get(config_key, [])
    return self.load_related(descriptor_list, child_class)

  def load_related(self, descriptor_list: List, child_class: Type[T]) -> List[T]:
    is_list = isinstance(descriptor_list, list)
    descriptor_list = descriptor_list if is_list else [descriptor_list]
    to_child = lambda obj: key_or_dict_to_child(obj, child_class, self)
    return list(map(to_child, descriptor_list))

  def load_list_child(self, config_key:str, child_class: Type[T], child_key:str) -> T:
    descriptor_list = self.config.get(config_key, [])
    predicate = lambda obj: key_or_dict_matches(obj, child_key)
    match = next((obj for obj in descriptor_list if predicate(obj)), None)
    return self.load_child(child_class, match) if match else None

  def load_child(self, child_cls: Type[T], key_or_dict: Union[str, dict]) -> T:
    return key_or_dict_to_child(key_or_dict, child_cls, self)

  @classmethod
  def inflate_all(cls) -> List[Type[T]]:
    cls_pool = cls.lteq_classes(wiz_app.subclasses)
    configs = configs_for_kinds(wiz_app.configs, cls_pool)
    return [cls.inflate_with_config(config) for config in configs]

  @classmethod
  def inflate_with_key(cls, _id: str) -> Type[T]:
    config = find_config_by_id(_id, wiz_app.configs)
    return cls.inflate_with_config(config)

  @classmethod
  def inflate(cls: T, key_or_dict: Union[str, Dict]) -> Optional[Type[T]]:
    if isinstance(key_or_dict, str):
      return cls.inflate_with_key(key_or_dict)
    elif isinstance(key_or_dict, Dict):
      return cls.inflate_with_config(key_or_dict)
    raise RuntimeError(f"Bad input {key_or_dict}")

  @classmethod
  def lteq_classes(cls, classes: List[Type]) -> List[Type[T]]:
    return [klass for klass in [*classes, cls] if issubclass(klass, cls)]

  @classmethod
  def inflate_with_config(cls, config: Dict) -> T:
    host_class = cls
    subclasses = cls.lteq_classes(wiz_app.subclasses)

    inherit_id, expl_kind = config.get('inherit'), config.get('kind')

    if expl_kind and not expl_kind == cls.__name__:
      host_class = find_class_by_name(expl_kind, subclasses)

    if inherit_id:
      other = cls.inflate_with_key(inherit_id)
      host_class = other.__class__
      config = {**other.config, **config}

    return host_class(config)

  @classmethod
  def expected_id(cls):
    return None

  @classmethod
  def covers_key(cls, key: str) -> bool:
    return cls.expected_id() == key


def key_or_dict_to_key(key_or_dict: Union[str, dict]) -> str:
  if isinstance(key_or_dict, str):
    return key_or_dict

  elif isinstance(key_or_dict, dict):
    return key_or_dict['key']

  raise RuntimeError(f"Can't handle {key_or_dict}")


def key_or_dict_matches(key_or_dict: Union[str, dict], target_key: str) -> bool:
  return key_or_dict_to_key(key_or_dict) == target_key


def key_or_dict_to_child(key_or_dict: Union[str, dict], child_cls: Type[T],
                         parent: T = None) -> T:
  inflated = child_cls.inflate(key_or_dict)
  inflated.parent = parent
  return inflated


def find_class_by_name(name: str, classes) -> Type:
  matcher = lambda klass: klass.__name__ == name
  return next(filter(matcher, classes), None)


def find_config_by_id(_id: str, configs: List[Dict]) -> Dict:
  matcher = lambda c: c.get('id') == _id
  return next(filter(matcher, configs), None)


def configs_for_kinds(configs: List[Dict], cls_pool) -> List[Dict]:
  kinds_pool = [cls.__name__ for cls in cls_pool]
  return [c for c in configs if c.get('kind') in kinds_pool]

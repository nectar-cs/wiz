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
    """
    Getter for the title property.
    :return: title property.
    """
    return self.config.get('title')

  @property
  def info(self):
    """
    Getter for the info property.
    :return: info property.
    """
    return self.config.get('info')

  def load_children(self, config_key:str , child_class:Type[T]) -> List[T]:
    """
    Loads a list of descriptors matching config_key, then inflates
    (instantiates) each one into an instance of the child class.
    :param config_key: child type to be listed.
    :param child_class: target class to be instantiated, eg Operation or Stage.
    :return: list of child_class objects.
    """
    descriptor_list = self.config.get(config_key, [])
    return self.load_related(descriptor_list, child_class)

  def load_related(self, descriptor_list: List, child_class: Type[T]) -> List[T]:
    """
    Inflates (instantiates) each object of the descriptor_list into an instance
    of the passed child_class.
    :param descriptor_list: list of objects to be instantiated.
    :param child_class: target class to be instantiated, eg Operation or Stage.
    :return: list of child_class objects.
    """
    is_list = isinstance(descriptor_list, list)
    descriptor_list = descriptor_list if is_list else [descriptor_list]
    to_child = lambda obj: key_or_dict_to_child(obj, child_class, self)
    return list(map(to_child, descriptor_list))

  def load_list_child(self, config_key:str, child_class: Type[T], child_key:str) -> T:
    """
    Finds child by child key, then inflates (instantiates) into an instance of
    the child class.
    :param config_key: key to find the appropriate descriptor list, eg "steps" or "fields".
    :param child_class: target class to be instantiated, eg Operation or Stage.
    :param child_key: key to find the child by.
    :return: instance of the child class.
    """
    descriptor_list = self.config.get(config_key, [])
    predicate = lambda obj: key_or_dict_matches(obj, child_key)
    match = next((obj for obj in descriptor_list if predicate(obj)), None)
    return self.load_child(child_class, match) if match else None

  def load_child(self, child_cls: Type[T], key_or_dict: Union[str, dict]) -> T:
    """
    Inflates (instantiates) the passed key or config into an instance of the
    child class.
    :param key_or_dict: dict to be inflated, or the key to find it first.
    :param child_cls: target class to be instantiated, eg Operation or Stage.
    :return: instance of the child class.
    """
    return key_or_dict_to_child(key_or_dict, child_cls, self)

  @classmethod
  def inflate_all(cls) -> List[Type[T]]:
    """
    Inflates (instantiates) all configs with kind matching the caller class's name.
    :return: List of instances of the caller class.
    """
    configs = wiz_app.configs_of_kind(cls.type_key())
    return [cls.inflate_with_config(config) for config in configs]

  @classmethod
  def inflate_with_key(cls, key: str) -> Type[T]:
    """
    Inflates (instantiates) the config that matches the passed key into an instance
    of the caller class, eg Operation or Stage.
    :param key: locator for the desired config, eg hub.backend.secrets.key_base.
    :return: instance of the caller class.
    """
    config = wiz_app.find_config(cls.type_key(), key)
    return cls.inflate_with_config(config)

  @classmethod
  def inflate(cls: T, key_or_dict: Union[str, Dict]) -> Optional[Type[T]]:
    """
    Inflates (instantiates) the passed key or config into an instance of the
    caller class, eg Operation or Stage.
    :param key_or_dict: config itself or locator for the desired config.
    :return: instance of the caller class.
    """
    if isinstance(key_or_dict, str):
      return cls.inflate_with_key(key_or_dict)
    elif isinstance(key_or_dict, Dict):
      return cls.inflate_with_config(key_or_dict)
    raise RuntimeError(f"Bad input {key_or_dict}")

  @classmethod
  def inflate_with_config(cls, config: Dict) -> T:
    """
    Inflates (instantiates) the passed config into an instance of the caller
    class, eg Operation or Stage. Takes into account any
    vendor-defined subclasses.
    :param config: vendor-provided app configuration, parsed from YAML to a dict.
    :return: instance of the caller class.
    """
    host_class = cls

    subclasses =
    explicit_kind = config.get('kind')
    lteq_classes()


    key, benefactor_key = config.get('key'), config.get('inherit')

    if key:
      closer_host_class = wiz_app.find_subclass(type_key, key)
      host_class = closer_host_class or host_class

    if benefactor_key:
      other_config = wiz_app.find_config(type_key, benefactor_key)
      config = {**other_config, **config}

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


def lteq_classes(upper_cls: Type[T], classes: List[Type]) -> List[Type[T]]:
  return [klass for klass in classes if issubclass(klass, upper_cls)]


def class_by_name(name: str, classes) -> Type:
  matcher = lambda klass: klass.__name__ == name
  return next(filter(matcher, classes), None)


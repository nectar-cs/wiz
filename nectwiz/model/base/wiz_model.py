import os
from typing import Type, Optional, Dict, Union, List, TypeVar

from nectwiz.core.core import utils
from nectwiz.core.core.types import Kod

T = TypeVar('T', bound='WizModel')

class ModelsMan:
  def __init__(self):
    self._descriptors: List[Dict] = []
    self._classes: List[Type[T]] = []

  def add_descriptors(self, descriptors: List[Dict]):
    self._descriptors = self._descriptors + descriptors

  def add_classes(self, model_classes: List[Type[T]]):
    self._classes = self._classes + model_classes

  def add_defaults(self):
    self.add_descriptors(default_descriptors())
    self.add_classes(default_model_classes())

  def clear(self, restore_defaults=True):
    self._descriptors = []
    self._classes = []
    if restore_defaults:
      self.add_defaults()

  def descriptors(self) -> List[Dict]:
    return self._descriptors

  def classes(self) -> List[Type[T]]:
    return self._classes


models_man = ModelsMan()


class WizModel:

  def __init__(self, config: Dict):
    self.config: Dict = config
    self._id: str = config.get('id')
    self.parent = None

  def id(self):
    return self._id

  @property
  def title(self):
    return self.config.get('title')

  @property
  def info(self):
    return self.config.get('info')

  def kind(self):
    return self.__class__.__name__

  def load_children(self, config_key: str, child_class: Type[T]) -> List[T]:
    descriptor_list = self.config.get(config_key, [])
    return self.load_related(descriptor_list, child_class)

  def load_related(self, kods: List, child_class: Type[T]) -> List[T]:
    is_list = isinstance(kods, list)
    kods = kods if is_list else [kods]
    to_child = lambda obj: key_or_dict_to_child(obj, child_class, self)
    return list(map(to_child, kods))

  def load_list_child(self, key: str, child_cls: Type[T], child_key: str) -> List[T]:
    descriptor_list = self.config.get(key, [])
    predicate = lambda obj: key_or_dict_matches(obj, child_key)
    match = next((obj for obj in descriptor_list if predicate(obj)), None)
    return self.load_child(child_cls, match) if match else None

  def load_child(self, child_cls: Type[T], key_or_dict: Kod) -> T:
    return key_or_dict_to_child(key_or_dict, child_cls, self)

  @classmethod
  def inflate_all(cls) -> List[T]:
    cls_pool = cls.lteq_classes(models_man.classes())
    configs = configs_for_kinds(models_man.descriptors(), cls_pool)
    return [cls.inflate_with_config(config) for config in configs]

  @classmethod
  def inflate(cls: T, key_or_dict: Kod) -> Optional[T]:
    if isinstance(key_or_dict, str):
      return cls.inflate_with_key(key_or_dict)
    elif isinstance(key_or_dict, Dict):
      return cls.inflate_with_config(key_or_dict)
    raise RuntimeError(f"Bad input {key_or_dict}")

  @classmethod
  def id_exists(cls, _id: str):
    pass

  @classmethod
  def inflate_with_key(cls, _id: str) -> T:
    if _id and _id[0].isupper():
      config = dict(kind=_id)
    else:
      candidate_subclasses = cls.lteq_classes(models_man.classes())
      candidate_kinds = [klass.kind() for klass in candidate_subclasses]
      all_configs = models_man.descriptors()
      config = find_config_by_id(_id, all_configs, candidate_kinds)
    return cls.inflate_with_config(config)

  @classmethod
  def inflate_with_config(cls, config: Dict, def_cls=None) -> T:
    host_class = cls or def_cls
    subclasses = cls.lteq_classes(models_man.classes())

    inherit_id, expl_kind = config.get('inherit'), config.get('kind')

    if expl_kind and not expl_kind == cls.__name__:
      host_class = find_class_by_name(expl_kind, subclasses)

    if inherit_id:
      other = cls.inflate_with_key(inherit_id)
      host_class = other.__class__
      config = {**other.config, **config}

    return host_class(config)

  @classmethod
  def lteq_classes(cls, classes: List[Type]) -> List[Type[T]]:
    return [klass for klass in [*classes, cls] if issubclass(klass, cls)]


def key_or_dict_to_key(key_or_dict: Union[str, dict]) -> str:
  if isinstance(key_or_dict, str):
    return key_or_dict

  elif isinstance(key_or_dict, dict):
    return key_or_dict.get('id')

  raise RuntimeError(f"Can't handle {key_or_dict}")


def key_or_dict_matches(key_or_dict: Kod, target_key: str) -> bool:
  return key_or_dict_to_key(key_or_dict) == target_key


def key_or_dict_to_child(key_or_dict: Kod, child_cls: Type[T],
                         parent: T = None) -> T:
  inflated = child_cls.inflate(key_or_dict)
  inflated.parent = parent
  return inflated


def find_class_by_name(name: str, classes) -> Type:
  matcher = lambda klass: klass.__name__ == name
  return next(filter(matcher, classes), None)


def find_config_by_id(_id: str, configs: List[Dict], kinds: List[str]) -> Dict:
  matcher = lambda c: c.get('id') == _id and c.get('kind') in kinds
  return next(filter(matcher, configs), None)


def configs_for_kinds(configs: List[Dict], cls_pool) -> List[Dict]:
  kinds_pool = [cls.__name__ for cls in cls_pool]
  return [c for c in configs if c.get('kind') in kinds_pool]


def default_descriptors() -> List[Dict]:
  pwd = os.path.join(os.path.dirname(__file__))
  return utils.yamls_in_dir(f"{pwd}/../../model/pre_built")


def default_model_classes() -> List[Type[T]]:
  from nectwiz.model.pre_built.cmd_exec_action import CmdExecAction
  from nectwiz.model.pre_built.step_apply_action import StepApplyResAction
  from nectwiz.model.pre_built.flush_telem_action import FlushTelemAction
  from nectwiz.model.deletion_spec.deletion_spec import DeletionSpec
  return [
    CmdExecAction,
    StepApplyResAction,
    FlushTelemAction,
    DeletionSpec
  ]

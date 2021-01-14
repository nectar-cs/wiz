import os
from os.path import isfile
from typing import Type, Optional, Dict, Union, List, TypeVar, Any

from werkzeug.utils import cached_property

from nectwiz.core.core import utils, subs
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import KoD, ErrDict
from nectwiz.core.core.utils import deep_merge
from nectwiz.model.base.default_models import default_model_classes

T = TypeVar('T', bound='WizModel')


class ModelsMan:
  def __init__(self):
    self._descriptors: List[Dict] = []
    self._classes: List[Type[T]] = []
    self._asset_paths: List[str] = []

  def add_descriptors(self, descriptors: List[Dict]):
    self._descriptors = self._descriptors + descriptors

  def add_classes(self, model_classes: List[Type[T]]):
    self._classes = self._classes + model_classes

  def add_asset_dir_paths(self, paths: List[str]):
    self._asset_paths += paths

  def add_defaults(self):
    self.add_descriptors(default_descriptors())
    self.add_classes(default_model_classes())
    self.add_asset_dir_paths(default_asset_paths())

  def clear(self, restore_defaults=True):
    self._descriptors = []
    self._classes = []
    if restore_defaults:
      self.add_defaults()

  def descriptors(self) -> List[Dict]:
    return self._descriptors

  def classes(self) -> List[Type[T]]:
    return self._classes

  def asset_dir_paths(self) -> List[str]:
    return self._asset_paths


models_man = ModelsMan()


class WizModel:

  ID_KEY = 'id'
  CONTEXT_KEY = 'context'
  TITLE_KEY = 'title'
  INHERIT_KEY = 'inherit'
  KIND_KEY = 'kind'
  INFO_KEY = 'info'
  ASSET_PREFIX = 'file::'
  CONTEXT_RECONSTRUCTOR_KEY = 'context_reconstructor'
  CONTEXT_RECONSTRUCTION_DATA_KEY = 'context_reconstruction_data'

  def __init__(self, config: Dict):
    self.config: Dict = config
    self._id: str = config.get(self.ID_KEY)
    self.context: Dict = config.get(self.CONTEXT_KEY, {})
    self.parent: Optional[T] = None

  def id(self) -> str:
    return self._id

  @cached_property
  def title(self) -> str:
    return self.get_prop(self.TITLE_KEY)

  @cached_property
  def info(self) -> str:
    return self.get_prop(self.INFO_KEY)

  def to_dict(self):
    return dict(
      id=self.id(),
      title=self.title,
      info=self.info
    )

  def update_attrs(self, config: Dict):
    for key, value in config.items():
      setattr(self, key, value)

  def get_prop(self, key: str, backup: Any = None) -> Any:
    """
    Convenience method for resolve_props
    @param key: name of desired value in config dict
    @param backup: value to return if value not in config dict
    @return: fully resolved property value or backup if given
    """
    return self.resolve_prop(key, backup=backup)

  def resolve_prop(self, key: str, **kwargs) -> Any:
    """
    Reads a value from the main config dicts, applies all possible
    resolution transformations to obtain its final value. This includes
    1) IFTT resolution, 2) ValueSupplier resolution, and
    3) string substitutions.
    @param key:
    @param kwargs:
    @return: fully resolved property value or backup if given
    """
    if key in list(self.config.keys()):
      value = self.config[key]
    else:
      lazy_backup = kwargs.pop('lazy_backup', None)
      if lazy_backup is not None:
        value = lazy_backup()
      else:
        value = kwargs.pop('backup', None)
      if kwargs.get('warn'):
        print(f"[nectwiz:{self.__class__.__name__}] undefined prop '{key}'")

    return self.resolve_prop_value(value)

  def resolve_prop_value(self, value: Any):
    if type(value) in [str, dict]:
      patches = dict(context=self.context)
      value = self.try_iftt_intercept(kod=value, patches=patches)
      value = self.try_supplier_intercept(kod=value, patches=patches)
      value = self.interpolate_prop(value)
      return self.try_read_from_asset(value)
    else:
      return value

  def interpolate_prop(self, value: str) -> Any:
    """
    Performs string substitutions on input. Combines substitution context
    from instance's self.context and any additional context passed as
    parameters. Returns unchanged input if property is not a string.
    @param value: value of property to interpolate
    @return: interpolated string if input is string else unchanged input
    """
    if value and type(value) == str:
      return subs.interp(value, self.assemble_eval_context())
    return value

  def assemble_eval_context(self) -> Dict:
    config_man_context = dict(resolvers=config_man.resolvers())
    # reconstructed_context = self.gen_reconstructed_context()
    return deep_merge(
      # reconstructed_context,
      config_man_context,
      self.context or {}
    )

  # def gen_reconstructed_context(self):
  #   if self.context_reconstructor:
  #     data = context_reconstruction_data
  #     self.context_reconstructor.generate(data)

  @classmethod
  def singleton_id(cls):
    raise NotImplemented

  @classmethod
  def inflate_singleton(cls, patches=None) -> T:
    return cls.inflate_with_id(cls.singleton_id(), patches)

  @classmethod
  def kind(cls):
    return cls.__name__

  def serialize(self) -> Dict:
    src_items = list(self.config.items())
    return {k: v for k, v in src_items if not k == self.CONTEXT_KEY}

  def inflate_children(self, child_class: Type[T], **kwargs):
    """
    Bottleneck function for a parent model to inflate a list of children.
    In the normal case, kods_or_provider_kod is a list of WizModels KoDs.
    In the special case, kods_or_provider_kod is ListGetter model
    that produces the actual children.
    case,
    @param child_class: class all children must a subclass of
    @return: resolved list of WizModel children
    """
    kods_or_supplier: Union[List[KoD], KoD] = kwargs.get('kod')
    if kods_or_supplier is None:
      kods_or_supplier = self.config.get(kwargs.get('prop')) or []
    patches: Optional[Dict] = kwargs.get('patches')

    kods_or_supplier = kods_or_supplier or []

    if type(kods_or_supplier) == list:
      children_kods = kods_or_supplier
      to_child = lambda obj: self.kod2child(obj, child_class, patches=patches)
      return list(map(to_child, children_kods))
    else:
      from nectwiz.model.supply.value_supplier import ValueSupplier
      supplier_kod = kods_or_supplier
      supplier = self.kod2child(supplier_kod, ValueSupplier, patches=patches)
      actual_kods = supplier.resolve()
      return self.inflate_children(
        child_class,
        kod=actual_kods,
        patches=patches
      )

  def inflate_list_child(self, child_cls: Type[T], **kwargs) -> Optional[T]:
    list_kod: KoD = kwargs.get('kod', self.config.get(kwargs.get('prop')))
    child_id: str = kwargs.get('id')
    patches: Optional[Dict] = kwargs.get('patches')

    predicate = lambda obj: key_or_dict_matches(obj, child_id)
    child_kod = next((obj for obj in list_kod if predicate(obj)), None)
    if child_kod:
      return self.inflate_child(child_cls, kod=child_kod, patches=patches)
    else:
      return None

  def inflate_child(self, child_cls: Type[T], **kwargs) -> Optional[T]:
    kod: KoD = kwargs.pop('kod', self.config.get(kwargs.pop('prop', None)))
    return self.kod2child(kod, child_cls, **kwargs)

  def kod2child(self, kod: KoD, child_cls: Type[T], **kwargs) -> T:
    patches: Dict = kwargs.pop('patches', None)
    patches = self.assemble_downstream_patches(patches)
    inflated = child_cls.inflate(kod, patches=patches, **kwargs)
    if inflated:
      inflated.parent = self
    return inflated

  def assemble_downstream_patches(self, extra_patches: Dict) -> Dict:
    default_patch = dict(context=self.context or {})
    return deep_merge(default_patch, extra_patches or {})

  @classmethod
  def inflate_all(cls, patches: Dict = None) -> List[T]:
    cls_pool = cls.lteq_classes(models_man.classes())
    configs = configs_for_kinds(models_man.descriptors(), cls_pool)
    return [cls.inflate(config, patches=patches) for config in configs]

  @classmethod
  def inflate(cls: T, kod: KoD, **kwargs) -> Optional[T]:
    patches: Dict = kwargs.get('patches')
    skip_intercept = kwargs.get('skip_intercept')
    if not skip_intercept:
      kod = cls.try_iftt_intercept(kod=kod, patches=patches)
    try:
      if isinstance(kod, str):
        return cls.inflate_with_id(kod, patches)
      elif isinstance(kod, Dict):
        return cls.inflate_with_config(kod, patches=patches)
      raise RuntimeError(f"Bad input {kod}")
    except Exception as err:
      if not kwargs.get('safely'):
        print(f"[nectwiz:{cls.kind()}] inflation error below for {kod}")
        raise err

  @classmethod
  def inflate_with_id(cls, _id: str, patches: Optional[Dict]) -> T:
    if _id and _id[0] and _id[0].isupper():
      config = dict(kind=_id)
    else:
      candidate_subclasses = cls.lteq_classes(models_man.classes())
      candidate_kinds = [klass.kind() for klass in candidate_subclasses]
      all_configs = models_man.descriptors()
      config = find_config_by_id(_id, all_configs, candidate_kinds)
    return cls.inflate_with_config(config, patches=patches)

  @classmethod
  def descendent_or_self(cls) -> T:
    subclasses = cls.lteq_classes(models_man.classes())
    not_self = lambda kls: not kls == cls
    return next(filter(not_self, subclasses), cls)({})

  @classmethod
  def inflate_with_config(cls, config: Dict, **kwargs) -> T:
    patches: Optional[Dict] = kwargs.get('patches')
    def_cls: Optional[Type] = kwargs.get('def_cls')

    host_class = cls or def_cls

    inherit_id = config.get(cls.INHERIT_KEY)
    explicit_kind = config.get(cls.KIND_KEY)

    if explicit_kind and not explicit_kind == host_class.__name__:
      host_class = cls.kind2cls(explicit_kind)

    if inherit_id:
      other = cls.inflate_with_id(inherit_id, patches)
      host_class = other.__class__
      config = {**other.config, **config}

    return host_class({**config, **(patches or {})})

  @classmethod
  def id_exists(cls, _id: str) -> bool:
    return True

  @classmethod
  def try_supplier_intercept(cls, **kwargs) -> Any:
    from nectwiz.model.supply.value_supplier import ValueSupplier
    return cls._try_as_interceptor(
      intercept_cls=ValueSupplier,
      prefix="id::",
      **kwargs
    )

  @classmethod
  def try_iftt_intercept(cls, **kwargs) -> Any:
    from nectwiz.model.predicate.iftt import Iftt
    return cls._try_as_interceptor(
      intercept_cls=Iftt,
      prefix="",
      **kwargs
    )

  @classmethod
  def _try_as_interceptor(cls, **kwargs) -> Any:
    intercept_cls: Type[T] = kwargs.get('intercept_cls')
    prefix: str = kwargs.get('prefix')
    kod: KoD = kwargs.get('kod')
    patches: Optional[Dict] = kwargs.get('patches')

    if cls.is_interceptor_candidate(intercept_cls, prefix, kod):
      trimmed_kod = kod.replace(prefix, "") if isinstance(kod, str) else kod

      interceptor = intercept_cls.inflate(
        trimmed_kod,
        patches=patches,
        skip_intercept=True,
        safely=True
      )
      if interceptor:
        return interceptor.resolve()
    return kod

  @staticmethod
  def truncate_kod_prefix(kod: KoD, prefix: str) -> KoD:
    if type(kod) == str and len(kod) >= len(prefix):
      return kod[len(prefix):len(kod)]
    return kod

  @classmethod
  def is_interceptor_candidate(cls, interceptor: Type[T], prefix, kod: KoD):
    if type(kod) == dict:
      interceptors = interceptor.lteq_classes(models_man.classes())
      if kod.get('kind') in [c.__name__ for c in interceptors]:
        return True
    if type(kod) == str:
      return kod.startswith(prefix)
    return False

  @classmethod
  def lteq_classes(cls, classes: List[Type]) -> List[Type[T]]:
    return [klass for klass in [*classes, cls] if issubclass(klass, cls)]

  @classmethod
  def kind2cls(cls, kind: str):
    subclasses = cls.lteq_classes(models_man.classes())
    return find_class_by_name(kind, subclasses)

  @staticmethod
  def try_read_from_asset(value):
    if value and type(value) == str:
      if value.startswith(WizModel.ASSET_PREFIX):
        return read_from_asset(value)
    return value


def read_from_asset(descriptor: str) -> str:
  _, path = descriptor.split("::")
  for dirpath in models_man.asset_dir_paths():
    full_path = f"{dirpath}/{path}"
    if isfile(full_path):
      with open(full_path) as file:
        return file.read()
  return ''


def key_or_dict_to_key(key_or_dict: Union[str, dict]) -> str:
  if isinstance(key_or_dict, str):
    return key_or_dict
  elif isinstance(key_or_dict, dict):
    return key_or_dict.get('id')
  raise RuntimeError(f"Can't handle {key_or_dict}")


def key_or_dict_matches(key_or_dict: KoD, target_key: str) -> bool:
  return key_or_dict_to_key(key_or_dict) == target_key


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


def default_asset_paths() -> List[str]:
  pwd = os.path.join(os.path.dirname(__file__))
  return [f"{pwd}/../../model/pre_built"]

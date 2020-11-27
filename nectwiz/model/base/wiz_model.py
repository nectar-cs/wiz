import os
from os.path import isfile
from typing import Type, Optional, Dict, Union, List, TypeVar, Any

from k8kat.utils.main.utils import deep_merge
from werkzeug.utils import cached_property

from nectwiz.core.core import utils, subs
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import KoD

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
    backup: Any = kwargs.get('backup')
    context_patch: Optional[Dict] = kwargs.get('context_patch')

    value = self.config.get(key, backup)
    if value is None and kwargs.get('warn'):
      print(f"[nectwiz:{self.__class__.__name__}] undefined prop '{key}'")

    if value and type(value) in [str, dict]:
      patches = dict(context=self.context)
      value = self.try_iftt_intercept(kod=value, patches=patches)
      value = self.try_value_getter_intercept(kod=value, patches=patches)
      value = self.interpolate_prop(value, context_patch)
      return self.try_read_from_asset(value)
    else:
      return value

  def interpolate_prop(self, value: str, extra_ctx: Optional[Dict]) -> Any:
    """
    Performs string substitutions on input. Combines substitution context
    from instance's self.context and any additional context passed as
    parameters. Returns unchanged input if property is not a string.
    @param value: value of property to interpolate
    @param extra_ctx: context-dict to be merged in to perform string subs
    @return: interpolated string if input is string else unchanged input
    """
    if value and type(value) == str:
      return subs.interp(value, self.assemble_eval_context(extra_ctx))
    return value

  def assemble_eval_context(self, extra_context) -> Dict:
    """
    @param extra_context:
    @return:
    """
    config_man_context = dict(resolvers=config_man.resolvers())
    self_ctx_merge = deep_merge(config_man_context, self.context or {})
    extra_ctx_merge = deep_merge(self_ctx_merge, extra_context or {})
    return extra_ctx_merge

  @classmethod
  def singleton_id(cls):
    raise NotImplemented

  @classmethod
  def inflate_singleton(cls, patches=None) -> T:
    return cls.inflate_with_id(cls.singleton_id(), patches)

  @classmethod
  def kind(cls):
    return cls.__name__

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
    kods_or_provider_kod: Union[List[KoD], KoD] = kwargs.get('kod')
    if kods_or_provider_kod is None:
      kods_or_provider_kod = self.config.get(kwargs.get('prop')) or []
    patches: Optional[Dict] = kwargs.get('patches')

    if type(kods_or_provider_kod) == list:
      to_child = lambda obj: self.kod2child(obj, child_class, patches)
      return list(map(to_child, kods_or_provider_kod))
    else:
      from nectwiz.model.supply.value_supplier import ValueSupplier
      provider: ValueSupplier = self.inflate(kods_or_provider_kod)
      actual_kods = provider.resolve()
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
    kod: KoD = kwargs.get('kod', self.config.get(kwargs.get('prop')))
    patches: Optional[Dict] = kwargs.get('patches')
    try:
      return self.kod2child(kod, child_cls, patches)
    except:
      if kwargs.get('safely'):
        return None
      raise

  def kod2child(self, kod: KoD, child_cls: Type[T], patches: Dict = None) -> T:
    patches = self.assemble_downstream_patches(patches)
    inflated = child_cls.inflate(kod, patches)
    inflated.parent = self
    return inflated

  def assemble_downstream_patches(self, extra_patches: Dict) -> Dict:
    default_patch = dict(context=self.context or {})
    return deep_merge(default_patch, extra_patches or {})

  @classmethod
  def inflate_all(cls, patches: Dict = None) -> List[T]:
    cls_pool = cls.lteq_classes(models_man.classes())
    configs = configs_for_kinds(models_man.descriptors(), cls_pool)
    return [cls.inflate(config, patches) for config in configs]

  @classmethod
  def inflate(cls: T, key_or_dict: KoD, patches: Dict = None) -> Optional[T]:
    skip_intercept = (patches or {}).get('__skip_intercept')
    if not skip_intercept:
      key_or_dict = cls.try_iftt_intercept(kod=key_or_dict, patches=patches)

    try:
      if isinstance(key_or_dict, str):
        return cls.inflate_with_id(key_or_dict, patches)
      elif isinstance(key_or_dict, Dict):
        return cls.inflate_with_config(key_or_dict, patches=patches)
      raise RuntimeError(f"Bad input {key_or_dict}")
    except Exception as err:
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
  def inflate_safely(cls, *args):
    # noinspection PyBroadException
    try:
      return cls.inflate(*args)
    except:
      return None

  @classmethod
  def id_exists(cls, _id: str) -> bool:
    return True

  @classmethod
  def try_value_getter_intercept(cls, **kwargs) -> Any:
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
      patches = {**(patches or {}), '__skip_intercept': True}
      interceptor = intercept_cls.inflate_safely(kod, patches)
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


def default_model_classes() -> List[Type[T]]:
  from nectwiz.model.action.actions.cmd_exec_action import CmdExecAction
  from nectwiz.model.action.actions.apply_manifest_action import ApplyManifestAction
  from nectwiz.model.adapters.deletion_spec import DeletionSpec
  from nectwiz.model.variable.manifest_variable import ManifestVariable
  from nectwiz.model.input.input import GenericInput
  from nectwiz.model.input.select_input import SelectInput
  from nectwiz.model.input.slider_input import SliderInput
  from nectwiz.model.adapters.list_resources_adapter import ResourceQueryAdapter
  from nectwiz.model.operation.operation import Operation
  from nectwiz.model.operation.stage import Stage
  from nectwiz.model.operation.step import Step
  from nectwiz.model.operation.field import Field
  from nectwiz.model.variable.generic_variable import GenericVariable
  from nectwiz.model.base.resource_selector import ResourceSelector
  from nectwiz.model.operation.operation_run_simulator import OperationRunSimulator
  from nectwiz.model.action.actions.delete_resources_action import DeleteResourcesAction
  from nectwiz.model.action.actions.multi_action import MultiAction
  from nectwiz.model.action.actions.run_predicates_action import RunPredicatesAction
  from nectwiz.model.input.checkboxes_input import CheckboxesInput
  from nectwiz.model.input.checkboxes_input import CheckboxInput
  from nectwiz.model.variable.variable_value_decorator import VariableValueDecorator
  from nectwiz.model.variable.pod_scaling_decorator import FixedReplicasDecorator
  from nectwiz.model.error.error_handler import ErrorHandler
  from nectwiz.model.error.error_trigger_selector import ErrorTriggerSelector
  from nectwiz.model.error.error_diagnosis import ErrorDiagnosis
  from nectwiz.model.error.diagnosis_actionable import DiagnosisActionable
  from nectwiz.model.predicate.format_predicate import FormatPredicate
  from nectwiz.model.predicate.multi_predicate import MultiPredicate
  from nectwiz.model.predicate.common_predicates import TruePredicate
  from nectwiz.core.telem.updates_man import UpdateAction
  from nectwiz.model.action.actions.backup_config_action import BackupConfigAction
  from nectwiz.model.action.actions.backup_config_action import UpdateLastCheckedAction
  from nectwiz.core.telem.updates_man import WizUpdateAction
  from nectwiz.model.adapters.app_status_computer import AppStatusComputer
  from nectwiz.model.stats.prometheus_single_value_computer import PrometheusScalarComputer

  from nectwiz.model.stats.prometheus_computer import PrometheusComputer
  from nectwiz.model.stats.metrics_computer import MetricsComputer
  from nectwiz.model.stats.prometheus_series_computer import PrometheusSeriesComputer
  from nectwiz.model.stats.basic_resource_metrics_computer import BasicResourceMetricsComputer

  from nectwiz.model.predicate.iftt import Iftt
  from nectwiz.model.predicate.common_predicates import FalsePredicate
  from nectwiz.model.hook.hook import Hook
  from nectwiz.model.supply.value_supplier import ValueSupplier
  from nectwiz.model.supply.http_data_supplier import HttpDataSupplier
  from nectwiz.model.supply.resources_supplier import ResourcesSupplier
  from nectwiz.model.predicate.system_check import SystemCheck
  return [
    Operation,
    Stage,
    Step,
    Field,
    Hook,

    GenericVariable,
    ManifestVariable,
    VariableValueDecorator,
    FixedReplicasDecorator,

    ErrorHandler,
    ErrorTriggerSelector,
    ErrorDiagnosis,
    DiagnosisActionable,

    GenericInput,
    SliderInput,
    SelectInput,
    CheckboxesInput,
    CheckboxInput,

    ResourceSelector,
    FormatPredicate,
    MultiPredicate,
    TruePredicate,
    FalsePredicate,

    Iftt,
    ValueSupplier,
    HttpDataSupplier,
    ResourcesSupplier,

    AppStatusComputer,
    SystemCheck,

    MultiAction,
    CmdExecAction,
    ApplyManifestAction,
    DeleteResourcesAction,
    RunPredicatesAction,
    UpdateAction,
    BackupConfigAction,
    UpdateLastCheckedAction,
    WizUpdateAction,

    ResourceQueryAdapter,
    DeletionSpec,
    PrometheusComputer,
    MetricsComputer,
    PrometheusScalarComputer,
    PrometheusSeriesComputer,
    BasicResourceMetricsComputer,

    OperationRunSimulator
  ]

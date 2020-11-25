import os
from os.path import isfile
from typing import Type, Optional, Dict, Union, List, TypeVar, Any

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

  def __init__(self, config: Dict):
    self.config: Dict = config
    self._id: str = config.get('id')
    self.title: str = config.get('title')
    self.info: str = config.get('info')
    self.context: Dict = config.get('context')
    self.choice_items: List[Dict] = config.get('items', [])
    self.parent = None

  def id(self):
    return self._id

  def to_dict(self):
    return dict(
      id=self.id(),
      title=self.title,
      info=self.info
    )

  def update_attrs(self, config: Dict):
    for key, value in config.items():
      setattr(self, key, value)

  def get_prop(self, key, backup=None):
    value = self.config.get(key, backup)
    if value and type(value) in [str, dict]:
      patches = dict(context=self.context)
      value = self.try_iftt_intercept(value, patches)
      value = self.try_value_getter_intercept(value, patches)
      return self.try_resolve_with_context(value)
    else:
      return value

  def prep_downstream_patches(self) -> Dict:
    return dict(context=self.context)

  def try_resolve_with_context(self, value) -> Any:
    if value and type(value) == str:
      return subs.interp(value, self.assemble_final_context())
    return value

  def assemble_final_context(self) -> Dict:
    _context = self.context or {}
    new_resolvers = _context.pop('resolvers', {})
    return dict(
      **_context,
      resolvers=dict(
        **config_man.resolvers(),
        **new_resolvers
      )
    )

  @classmethod
  def singleton_id(cls):
    raise NotImplemented

  @classmethod
  def inflate_singleton(cls, patches=None) -> T:
    return cls.inflate_with_key(cls.singleton_id(), patches)

  @classmethod
  def kind(cls):
    return cls.__name__

  def inflate_children(self,
                       config_key: str,
                       child_class: Type[T],
                       patches: Dict = None) -> List[T]:
    descriptor_list = self.config.get(config_key, [])
    return self.load_related(descriptor_list, child_class, patches)

  def load_related(self,
                   kod_or_kods: List,
                   child_class: Type[T],
                   patches: Dict = None) -> List[T]:
    is_list = isinstance(kod_or_kods, list)
    kod_or_kods = kod_or_kods if is_list else [kod_or_kods]
    to_child = lambda obj: self._kod2child(obj, child_class, patches)
    return list(map(to_child, kod_or_kods))

  def load_list_child(self,
                      key: str,
                      child_cls: Type[T],
                      child_key: str,
                      patches: Dict = None) -> T:
    descriptor_list = self.config.get(key, [])
    predicate = lambda obj: key_or_dict_matches(obj, child_key)
    match = next((obj for obj in descriptor_list if predicate(obj)), None)
    return self.inflate_child(child_cls, match, patches) if match else None

  def inflate_child(self,
                    child_cls: Type[T],
                    kod: KoD,
                    patches: Dict = None) -> T:
    return self._kod2child(kod, child_cls, patches)

  def _kod2child(self,
                 kod: KoD,
                 child_cls: Type[T],
                 patches: Dict = None) -> T:
    patches = {**self.prep_downstream_patches(), **(patches or {})}
    inflated = child_cls.inflate(kod, patches)
    inflated.parent = self
    return inflated

  @classmethod
  def inflate_all(cls, patches: Dict = None) -> List[T]:
    cls_pool = cls.lteq_classes(models_man.classes())
    configs = configs_for_kinds(models_man.descriptors(), cls_pool)
    return [cls.inflate(config, patches) for config in configs]

  @classmethod
  def inflate(cls: T, key_or_dict: KoD, patches: Dict = None) -> Optional[T]:
    key_or_dict = cls.try_as_iftt(key_or_dict)
    try:
      if isinstance(key_or_dict, str):
        return cls.inflate_with_key(key_or_dict, patches)
      elif isinstance(key_or_dict, Dict):
        return cls.inflate_with_config(key_or_dict, patches, None)
      raise RuntimeError(f"Bad input {key_or_dict}")
    except Exception as err:
      raise err

  @classmethod
  def inflate_with_key(cls, _id: str, patches: Optional[Dict]) -> T:
    if _id and _id[0] and _id[0].isupper():
      config = dict(kind=_id)
    else:
      candidate_subclasses = cls.lteq_classes(models_man.classes())
      candidate_kinds = [klass.kind() for klass in candidate_subclasses]
      all_configs = models_man.descriptors()
      config = find_config_by_id(_id, all_configs, candidate_kinds)
    return cls.inflate_with_config(config, patches, None)

  @classmethod
  def descendent_or_self(cls) -> T:
    subclasses = cls.lteq_classes(models_man.classes())
    not_self = lambda kls: not kls == cls
    return next(filter(not_self, subclasses), cls)({})

  @classmethod
  def inflate_with_config(cls,
                          config: Optional[Dict],
                          patches: Optional[Dict],
                          def_cls: Optional[Type]) -> T:
    host_class = cls or def_cls

    inherit_id, expl_kind = config.get('inherit'), config.get('kind')

    if expl_kind and not expl_kind == host_class.__name__:
      host_class = cls.kind2cls(expl_kind)

    if inherit_id:
      other = cls.inflate_with_key(inherit_id, patches)
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
  def try_value_getter_intercept(cls, kod, patches) -> Any:
    from nectwiz.model.value_getter.value_getter import ValueGetter
    return cls.try_as_interceptor(ValueGetter, kod, patches)

  @classmethod
  def try_iftt_intercept(cls, kod, patches) -> Any:
    from nectwiz.model.predicate.iftt import Iftt
    return cls.try_as_interceptor(Iftt, kod, patches)

  @classmethod
  def try_as_interceptor(cls, intercept_cls: Type[T], kod: KoD, patches) -> Any:
    if cls.is_kod_interceptor_candidate(intercept_cls, kod):
      interceptor = intercept_cls.inflate_safely(kod, patches)
      if interceptor:
        return interceptor.resolve_item()
    return kod

  @classmethod
  def is_kod_interceptor_candidate(cls, interceptor: Type[T], kod: KoD):
    if type(kod) == dict:
      if kod.get('kind') == interceptor.__name__:
        return True
    if type(kod) == str:
      return True
    return False

  @classmethod
  def lteq_classes(cls, classes: List[Type]) -> List[Type[T]]:
    return [klass for klass in [*classes, cls] if issubclass(klass, cls)]

  @classmethod
  def kind2cls(cls, kind: str):
    subclasses = cls.lteq_classes(models_man.classes())
    return find_class_by_name(kind, subclasses)

  @staticmethod
  def asset_attr(value):
    if value and type(value) == str and value.startswith("file::"):
      return read_from_asset(value)
    else:
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
  from nectwiz.model.action.actions.flush_telem_action import FlushTelemAction
  from nectwiz.model.adapters.deletion_spec import DeletionSpec
  from nectwiz.model.variable.manifest_variable import ManifestVariable
  from nectwiz.model.input.input import GenericInput
  from nectwiz.model.input.select_input import SelectInput
  from nectwiz.model.input.slider_input import SliderInput
  from nectwiz.model.adapters.list_resources_adapter import ResourceQueryAdapter
  from nectwiz.model.operation.operation import Operation
  from nectwiz.model.operation.stage import Stage
  from nectwiz.model.operation.step import Step
  from nectwiz.model.field.field import Field
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
  from nectwiz.model.predicate.resource_property_predicate import ResourcePropertyPredicate
  from nectwiz.model.predicate.resource_count_predicate import ResourceCountPredicate
  from nectwiz.model.predicate.manifest_variable_predicate import ManifestVariablePredicate
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
  from nectwiz.model.predicate.prefs_variable_predicate import PrefsVariablePredicate

  from nectwiz.model.predicate.iftt import Iftt
  from nectwiz.model.predicate.common_predicates import FalsePredicate
  from nectwiz.model.hook.hook import Hook
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
    ResourcePropertyPredicate,
    ResourceCountPredicate,
    ManifestVariablePredicate,
    TruePredicate,
    FalsePredicate,
    PrefsVariablePredicate,
    Iftt,

    MultiAction,
    CmdExecAction,
    ApplyManifestAction,
    FlushTelemAction,
    DeleteResourcesAction,
    AppStatusComputer,
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

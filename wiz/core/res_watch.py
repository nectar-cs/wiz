from typing import Callable, Optional, List, Dict, Type

from k8_kat.res.dep.kat_dep import KatDep

from k8_kat.res.config_map.kat_map import KatMap

from k8_kat.res.base.kat_res import KatRes
from wiz.core.wiz_globals import wiz_app


class Decorator:
  def __init__(self, kind, res_instance):
    self.kind = kind
    self.res_instance = res_instance

  @classmethod
  def matches(cls, kind):
    return KatRes.find_res_class(kind) is not None

  def name(self) -> str:
    return self.res_instance.metadata.name

  def status(self) -> str:
    return 'positive'

  def extras(self) -> Dict:
    return {}

  def updated_at(self):
    return None

  def short_desc(self):
    annotations = self.res_instance.metadata.annotations
    return (annotations or {}).get('short-desc')

  def serialize(self) -> Dict:
    return dict(
      kind=self.kind,
      name=self.name(),
      short_desc=self.short_desc() or "No metadata provided",
      status=self.status(),
      extras=self.extras(),
      updated_at=self.updated_at()
    )


class KatDecorator(Decorator):
  @property
  def katified(self) -> KatRes:
    kat_class = KatRes.find_res_class(self.kind)
    return kat_class(self.res_instance)

  def status(self) -> str:
    return self.katified.ternary_status()

  def updated_at(self):
    return self.katified.updated_at()


class ConfigMapDecorator(KatDecorator):
  @classmethod
  def matches(cls, kind):
    return kind == 'ConfigMap'

  # noinspection PyTypeChecker
  @property
  def katified(self) -> KatMap:
    return super().katified

  def extras(self) -> Dict:
    extra_data = {}
    if self.name() == 'master':
      extra_data = self.katified.yget('master')
    return {**super().extras(), **extra_data}


class DeploymentDecorator(KatDecorator):
  @classmethod
  def matches(cls, kind):
    return kind == 'Deployment'

  def short_desc(self):
    # noinspection PyTypeChecker
    dep: KatDep = self.katified
    ready = dep.ready_replicas or 0
    pod_state = f"{ready}/{dep.desired_replicas} pods"
    return f"{super().short_desc()} - {pod_state}"

def decorator_classes():
  return [
    ConfigMapDecorator,
    DeploymentDecorator,
    SecretDecorator,
    KatDecorator,
    Decorator
  ]


class SecretDecorator(KatDecorator):
  @classmethod
  def matches(cls, kind):
    return kind == 'Secret'

  def extras(self):
    data = self.res_instance.data or {}
    transform = lambda word: f"<{len(word)} bytes>"
    return {k: transform(v) for k, v in data.items()}


def resolve_kind_loader(kind) -> Optional[Callable]:
  kat_class = KatRes.find_res_class(kind)
  if kat_class:
    if kat_class.__name__  == 'KatPod':
      return lambda ns: [k.raw for k in kat_class.list(ns) if not k.has_parent]
    else:
      return lambda ns: [k.raw for k in kat_class.list(ns)]
  else:
    return None


def resolve_decorator(kind: str) -> Optional[Type[Decorator]]:
  # noinspection PyTypeChecker
  matches = [c for c in decorator_classes() if c.matches(kind)]
  return matches[0] if len(matches) > 0 else None


def serialized_instances(kind_instances: Dict[str, List]) -> List[any]:
  all_decorated = []
  for kind, instances in kind_instances.items():
    decorator = resolve_decorator(kind)
    if decorator:
      all_decorated += [decorator(kind, inst).serialize() for inst in instances]
    else:
      print(f"NO DECORATOR FOR {kind}")
  return all_decorated


def load_kind_instances(kinds) -> Dict[str, List]:
  all_instances = {}
  for kind in kinds:
    loader = resolve_kind_loader(kind)
    if loader:
      all_instances[kind] = loader(wiz_app.ns)
    else:
      print(f"NO LOADER FOR KIND {kind}")
  return all_instances


def glob(kinds: List[str]) -> List[Dict]:
  kind_instances = load_kind_instances(kinds)
  return serialized_instances(kind_instances)

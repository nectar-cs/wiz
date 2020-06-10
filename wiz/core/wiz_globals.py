import json
import os
from json import JSONDecodeError
from typing import Dict, Type, Optional, List

tedi_pod_name = 'tedi'
cache_root = '/tmp'


def category_default() -> Dict[str, any]:
  return dict(
    install_stages=[],
    steps=[],
    fields=[],
    operations=[]
  )


def clear_cache():
  if os.path.exists(f'{cache_root}/hub-app.json'):
    os.remove(f'{cache_root}/hub-app.json')

  if os.path.exists(f'{cache_root}/ns.txt'):
    os.remove(f'{cache_root}/ns.txt')

def persist_ns_and_app(ns, app):
  with open(f'{cache_root}/hub-app.json', 'w') as file:
    file.write(json.dumps(app))

  with open(f'{cache_root}/ns.txt', 'w') as file:
    file.write(ns)


def read_ns_and_app():
  root = '/tmp'
  try:
    with open(f'{root}/hub-app.json', 'r') as file:
      app = json.loads(file.read())
    with open(f'{root}/ns.txt', 'r') as file:
      ns = file.read()
    return [ns, app]
  except (FileNotFoundError, JSONDecodeError):
    return [None, None]


def is_config_match(config: Dict, kind: str, key: str):
  return config['kind'] == kind and config['key'] == key


def is_subclass_match(subclass, kind: str, key: str):
  from wiz.model.base.wiz_model import WizModel
  actual: WizModel = subclass
  return actual.type_key() == kind and actual.key() == key


class WizApp:

  def __init__(self):
    self.configs = []
    self.subclasses = []
    self.providers = []
    self.adapters = []
    self.access_point_delegate = None
    self.ns_overwrite = None

  @property
  def ns(self):
    return self.ns_overwrite or read_ns_and_app()[0]

  @property
  def app(self):
    return read_ns_and_app()[1] or {}

  def add_configs(self, new_configs: List[Dict]):
    self.configs = self.configs + new_configs

  def add_overrides(self, new_overrides):
    self.subclasses += new_overrides

  def add_adapters(self, new_adapters):
    self.adapters += new_adapters

  def add_providers(self, new_providers):
    self.providers += new_providers

  def find_provider(self, adapter_class: Type):
    matches = [c for c in self.providers if c.kind() == adapter_class]
    return matches[0] if len(matches) > 0 else None

  def find_config(self, kind: str, key: str):
    matches = [c for c in self.configs if is_config_match(c, kind, key)]
    return matches[0] if len(matches) else None

  def configs_of_kind(self, kind: str):
    return [c for c in self.configs if c['kind'] == kind]

  def find_subclass(self, kind: str, key: str) -> Optional[Type]:
    matches = [c for c in self.subclasses if is_subclass_match(c, kind, key)]
    return matches[0] if len(matches) else None

  def clear(self):
    self.configs = []
    self.subclasses = []


wiz_app = WizApp()

import json
import os
from json import JSONDecodeError
from typing import Dict, Type, Optional

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

class WizGlobals:

  def __init__(self):
    self.configs = category_default()
    self.subclasses = category_default()
    self.access_point_delegate = None
    self.ns_overwrite = None

  @property
  def ns(self):
    return self.ns_overwrite or read_ns_and_app()[0]

  @property
  def app(self):
    return read_ns_and_app()[1] or {}

  def set_configs(self, **kwargs):
    self.configs = {**category_default(), **kwargs}

  def set_subclasses(self, **kwargs):
    self.subclasses = {**category_default(), **kwargs}

  def find_config(self, category, key: str):
    candidates = self.configs[category]
    matches = [config for config in candidates if config['key'] == key]
    return matches[0] if len(matches) else None

  def find_subclass(self, category, key: str) -> Optional[Type]:
    if key:
      candidates = self.subclasses[category]
      matches = [subclass for subclass in candidates if subclass.key() == key]
      return matches[0] if len(matches) else None
    else:
      return None

  def clear(self):
    self.configs = category_default()
    self.subclasses = category_default()


wiz_globals = WizGlobals()

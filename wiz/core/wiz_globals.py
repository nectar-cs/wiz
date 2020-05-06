import json
import os
from json import JSONDecodeError
from typing import Dict

from k8_kat.auth.kube_broker import broker

from wiz.core import utils

tedi_pod_name = 'tedi'
cache_root = '/tmp'

def validate_custom_classes(classes):
  for concern_class in classes:
    if not concern_class.key():
      raise RuntimeError('Concern key must provide a key()')

  keys = [c.key() for c in classes]
  duplicates = set([x for x in keys if keys.count(x) > 1])
  if duplicates:
    raise RuntimeError(f'Duplicate keys found: {duplicates}')


def category_default() -> Dict[str, any]:
  return dict(concerns=[], steps=[], fields=[])


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
    self.ns_overwrite = None

  @property
  def ns(self):
    return self.ns_overwrite or read_ns_and_app()[0]

  @property
  def app(self):
    return read_ns_and_app()[1]

  def set_configs(self, **kwargs):
    self.configs = {**category_default(), **kwargs}

  def set_subclasses(self, **kwargs):
    self.subclasses = {**category_default(), **kwargs}

  def find_config(self, category, key: str):
    candidates = self.configs[category]
    matches = [config for config in candidates if config['key'] == key]
    return matches[0] if len(matches) else None

  def find_subclass(self, category, key: str):
    candidates = self.subclasses[category]
    matches = [config for config in candidates if config.key() == key]
    return matches[0] if len(matches) else None

  def clear(self):
    self.configs = category_default()
    self.subclasses = category_default()


wiz_globals = WizGlobals()

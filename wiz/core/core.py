import os

from k8_kat.res.config_map.kat_map import KatMap

def namespace():
  return os.environ.get('NAMESPACE', 'moz')

def master_map():
  return KatMap.find(namespace(), 'master')


import os
from typing import Tuple

from k8_kat.res.config_map.kat_map import KatMap
from wiz.core import utils


def namespace():
  return os.environ.get('NAMESPACE', 'moz')

def master_map():
  return KatMap.find(namespace(), 'master')

def commit_values(assignments: [Tuple[str, any]]):
  config = master_map().json('master')
  for assignment in assignments:
    fqdk_array = assignment[0].split('.')
    value = assignment[1]
    utils.deep_set(config, fqdk_array, value)
  master_map().set_json('master', master_map)

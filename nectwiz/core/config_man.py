import base64
import json
import os
from typing import Optional, Dict

from k8_kat.res.config_map.kat_map import KatMap
from k8_kat.res.secret.kat_secret import KatSecret

from nectwiz.core import utils
from nectwiz.core.types import TamDict

cmap_name = 'master'
install_uuid_path = '/var/install_uuid'
tam_config_key = 'tam'
tam_vars_key = 'manifest_variables'


def master_cmap() -> KatMap:
  """
  Returns the ConfigMap.
  :return: ConfigMap.
  """
  from nectwiz.core.wiz_app import wiz_app
  return KatMap.find(cmap_name, wiz_app.ns())


def read_cmap_dict(outer_key: str) -> Dict:
  cmap = master_cmap()
  return cmap.jget(outer_key, {}) if cmap else {}


def patch_cmap(outer_key: str, value: any):
  config_map = master_cmap()
  config_map.raw.data[outer_key] = value
  config_map.touch(save=True)


def patch_cmap_with_dict(outer_key: str, value: Dict):
  patch_cmap(outer_key, json.dumps(value))


def read_ns() -> Optional[str]:
  return os.environ.get('NAMESPACE')


def read_tam() -> TamDict:
  return read_cmap_dict(tam_config_key)


def read_tam_vars() -> Dict:
  return read_cmap_dict(tam_vars_key)


def read_tam_var(deep_key: str) -> Optional[str]:
  """
  Deep-gets the value specified as deep_key from the ConfigMap.
  :param deep_key: key in the following format: level1.level2.level3, where levels
  refer to keys at various depths of the dict, from most shallow to deepest.
  :return: value behind deep key.
  """
  return utils.deep_get(read_tam_vars(), deep_key.split('.'))


def read_install_uuid(ns):
  if utils.is_dev():
    secret = KatSecret.find('master', ns) if ns else None
    if secret:
      raw_enc = secret.raw.data.get('install_uuid')
      raw_enc_bytes = bytes(raw_enc, 'utf-8')
      return base64.b64decode(raw_enc_bytes).decode()
    return None
  else:
    try:
      with open(install_uuid_path, 'r') as file:
        return file.read()
    except FileNotFoundError:
      return None


def commit_tam_vars(assignments: Dict[str, any]):
  """
  Updates the ConfigMap with the new assignments. Saves it.
  :param assignments: assigns to be inserted.
  """
  tam_vars = read_tam_vars()
  for assignment in list(assignments.items()):
    deep_key_as_list = assignment[0].split('.')  # fully qualified hash key
    value = assignment[1]
    utils.deep_set(tam_vars, deep_key_as_list, value)

  patch_cmap_with_dict(tam_vars_key, tam_vars)

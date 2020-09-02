import base64

import json
import os
from typing import Optional, Dict, List, Tuple

from k8_kat.res.config_map.kat_map import KatMap
from k8_kat.res.secret.kat_secret import KatSecret
from k8_kat.utils.main.utils import deep_merge

from nectwiz.core import utils
from nectwiz.core.types import TamDict

cmap_name = 'master'
install_uuid_path = '/var/install_uuid'
tam_config_key = 'tam'
tam_vars_key = 'manifest_variables'
tam_defaults_key = 'manifest_defaults'
update_checked_at_key = 'update_checked_at'


def master_cmap() -> Optional[KatMap]:
  """
  Returns the ConfigMap.
  :return: ConfigMap.
  """
  from nectwiz.core.wiz_app import wiz_app
  if wiz_app.ns():
    return KatMap.find(cmap_name, wiz_app.ns())
  else:
    return None


def read_cmap_dict(outer_key: str) -> Dict:
  cmap = master_cmap()
  return cmap.jget(outer_key, {}) if cmap else {}


def read_cmap_primitive(flat_key: str):
  cmap = master_cmap()
  return cmap.data.get(flat_key) if cmap else None


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


def write_tam(new_tam: TamDict):
  patch_cmap_with_dict(tam_config_key, new_tam)


def read_tam_vars() -> Dict:
  return read_cmap_dict(tam_vars_key)


def write_tam_var_defaults(assigns: Dict):
  patch_cmap_with_dict(tam_defaults_key, assigns)


def read_tam_var_defaults() -> Dict:
  return read_cmap_dict(tam_defaults_key)


def read_last_update_checked() -> str:
  return read_cmap_primitive(update_checked_at_key)


def write_last_update_checked(new_value):
  return patch_cmap(update_checked_at_key, new_value)


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


def commit_keyed_tam_assigns(assignments: List[Tuple[str, any]]):
  commit_tam_assigns(utils.keyed2dict(assignments))


def commit_tam_assigns(assignments: Dict[str, any]):
  merged = deep_merge(read_tam_vars(), assignments)
  patch_cmap_with_dict(tam_vars_key, merged)

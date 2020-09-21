import base64
import json
from typing import Optional, Dict, List, Tuple

from k8kat.auth.kube_broker import broker
from k8kat.res.config_map.kat_map import KatMap
from k8kat.res.secret.kat_secret import KatSecret
from k8kat.utils.main.utils import deep_merge

from nectwiz.core.core import utils
from nectwiz.core.core.types import TamDict

cmap_name = 'master'
install_uuid_path = '/etc/sec/install_uuid'
tam_config_key = 'tam'
prefs_config_key = 'prefs'
tam_vars_key = 'manifest_variables'
tam_defaults_key = 'manifest_defaults'
update_checked_at_key = 'update_checked_at'
ns_path = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
dev_ns_path = '/tmp/nectwiz-dev-ns'


class ConfigMan:
  def __init__(self):
    self._ns: Optional[str] = None
    self._tam: Optional[TamDict] = None
    self._install_uuid: Optional[str] = None
    self._tam_defaults: Optional[Dict] = None
    self._tam_vars: Optional[Dict] = None
    self._prefs: Optional[Dict] = None

  def ns(self, force_reload=False):
    if force_reload or utils.is_worker() or not self._ns:
      self._ns = read_ns()
    return self._ns

  def prefs(self, force_reload=False) -> TamDict:
    if force_reload or utils.is_worker() or not self._prefs:
      self._prefs = self.read_prefs()
    return self._prefs

  def tam(self, force_reload=False) -> TamDict:
    if force_reload or utils.is_worker() or not self._tam:
      self._tam = self.read_tam()
    return self._tam

  def tam_defaults(self, force_reload=False) -> Dict:
    if force_reload or utils.is_worker() or not self._tam_defaults:
      self._tam_defaults = self.read_mfst_defaults()
    return self._tam_defaults

  def mfst_vars(self, force_reload=False) -> Dict:
    if force_reload or utils.is_worker() or not self._tam_vars:
      self._tam_vars = self.read_mfst_vars()
    return self._tam_vars

  def install_uuid(self, force_reload=False) -> str:
    if self.ns() and (utils.is_worker() or force_reload or not self.install_uuid):
      self._install_uuid = self.read_install_uuid()
    return self._install_uuid

  def master_cmap(self) -> Optional[KatMap]:
    if config_man.ns():
      return KatMap.find(cmap_name, self.ns())
    else:
      return None

  # noinspection PyTypedDict
  def resolvers(self) -> Dict:
    return dict(
      manifest_variables=lambda n: self.read_tam_var(n),
      tam_config=lambda n: self.tam().get(n)
    )

  def read_cmap_dict(self, outer_key: str) -> Dict:
    cmap = self.master_cmap()
    return cmap.jget(outer_key, {}) if cmap else {}

  def read_cmap_primitive(self, flat_key: str):
    cmap = self.master_cmap()
    return cmap.data.get(flat_key) if cmap else None

  def patch_cmap(self, outer_key: str, value: any):
    config_map = self.master_cmap()
    config_map.raw.data[outer_key] = value
    config_map.touch(save=True)

  def patch_cmap_with_dict(self, outer_key: str, value: Dict):
    self.patch_cmap(outer_key, json.dumps(value))

  def read_tam(self) -> TamDict:
    return self.read_cmap_dict(tam_config_key)

  def read_prefs(self) -> TamDict:
    return self.read_cmap_dict(prefs_config_key)

  def write_tam(self, new_tam: TamDict):
    self.patch_cmap_with_dict(tam_config_key, new_tam)
    self._tam = None

  def patch_tam(self, partial_tam: TamDict):
    new_tam = {**self.tam(True), **partial_tam}
    self.write_tam(new_tam)

  def read_mfst_vars(self) -> Dict:
    return self.read_cmap_dict(tam_vars_key)

  def patch_mfst_defaults(self, assigns: Dict):
    new_defaults = {**self.read_mfst_defaults(), **assigns}
    self.write_mfst_defaults(new_defaults)

  def write_mfst_defaults(self, assigns: Dict):
    self.patch_cmap_with_dict(tam_defaults_key, assigns)
    self._tam_defaults = None

  def read_mfst_defaults(self) -> Dict:
    return self.read_cmap_dict(tam_defaults_key)

  def read_last_update_checked(self) -> str:
    return self.read_cmap_primitive(update_checked_at_key)

  def write_last_update_checked(self, new_value):
    return self.patch_cmap(update_checked_at_key, new_value)

  def read_tam_var(self, deep_key: str) -> Optional[str]:
    """
    Deep-gets the value specified as deep_key from the ConfigMap.
    :param deep_key: key in the following format: level1.level2.level3, where levels
    refer to keys at various depths of the dict, from most shallow to deepest.
    :return: value behind deep key.
    """
    return utils.deep_get(self.read_mfst_vars(), deep_key.split('.'))

  def read_install_uuid(self):
    if utils.is_dev():
      secret = KatSecret.find('master', self.ns()) if self.ns() else None
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

  def commit_keyed_mfst_vars(self, assignments: List[Tuple[str, any]]):
    self.commit_mfst_vars(utils.keyed2dict(assignments))

  def commit_mfst_vars(self, assignments: Dict[str, any]):
    merged = deep_merge(self.read_mfst_vars(), assignments)
    self.patch_cmap_with_dict(tam_vars_key, merged)


config_man = ConfigMan()


def read_ns() -> Optional[str]:
  path = None
  if broker.is_in_cluster_auth():
    path = ns_path
  elif utils.is_dev():
    path = dev_ns_path
  if path:
    with open(path, 'r') as file:
      return file.read()
  else:
    return None


def coerce_ns(new_ns):
  config_man._ns = new_ns
  config_man._tam = None
  config_man._install_uuid = None
  config_man._tam_defaults = None
  config_man._tam_vars = None
  if utils.is_dev():
    with open(dev_ns_path, 'w') as file:
      file.write(new_ns)

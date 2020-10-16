import base64
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Callable

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
key_last_updated = 'last_updated'
tam_vars_key = 'manifest_variables'
tam_defaults_key = 'manifest_defaults'
update_checked_at_key = 'update_checked_at'
ns_path = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
dev_ns_path = '/tmp/nectwiz-dev-ns'
iso8601_time_fmt = '%Y-%m-%d %H:%M:%S.%f'


class ConfigMan:
  def __init__(self):
    self._ns: Optional[str] = None
    self._tam: Optional[TamDict] = None
    self._install_uuid: Optional[str] = None
    self._tam_defaults: Optional[Dict] = None
    self._manifest_defaults: Optional[Dict] = None
    self._tam_vars: Optional[Dict] = None
    self._prefs: Optional[Dict] = None
    self._last_updated: Optional[datetime] = None

  def ns(self, force_reload=False):
    if force_reload or utils.is_worker() or not self._ns:
      self._ns = read_ns()
    return self._ns

  def prefs(self, force_reload=False) -> Dict:
    if force_reload or utils.is_worker() or not self._prefs:
      self._prefs = self.read_prefs()
    return self._prefs

  def flat_prefs(self, force_reload=False) -> Dict:
    return utils.dict2flat(self.prefs(force_reload))

  def tam(self, force_reload=False) -> TamDict:
    if force_reload or utils.is_worker() or not self._tam:
      self._tam = self.read_tam()
    return self._tam

  def tam_defaults(self, force_reload=False) -> Dict:
    if force_reload or utils.is_worker() or not self._tam_defaults:
      self._tam_defaults = self.read_manifest_defaults()
    return self._tam_defaults

  def manifest_variables(self, force_reload=False) -> Dict:
    if force_reload or utils.is_worker() or not self._tam_vars:
      self._tam_vars = self.read_manifest_vars()
    return self._tam_vars

  def flat_manifest_vars(self, force_reload=False) -> Dict:
    return utils.dict2flat(self.manifest_variables(force_reload))

  def last_updated(self, force_reload=False) -> datetime:
    if not self._last_updated or force_reload:
      raw = self.read_config_map_primitive(key_last_updated)
      self._last_updated = datetime.strptime(raw, iso8601_time_fmt)
    return self._last_updated or distant_past_timestamp()

  def manifest_var(self, deep_key: str, reload=False) -> Optional[str]:
    """
    Deep-gets the value specified as deep_key from the ConfigMap.
    :param deep_key: key in the following format: level1.level2.level3, where levels
    refer to keys at various depths of the dict, from most shallow to deepest.
    :param reload: force reload
    :return: value behind deep key.
    """
    return utils.deep_get2(self.manifest_variables(reload), deep_key)

  def manifest_defaults(self, force_reload=True):
    if force_reload or utils.is_worker() or not self._manifest_defaults:
      self._manifest_defaults = self.read_manifest_defaults()
    return self._manifest_defaults

  def install_uuid(self, force_reload=False) -> str:
    if self.ns() and (utils.is_worker() or force_reload or not self.install_uuid):
      self._install_uuid = self.read_install_uuid()
    return self._install_uuid

  def master_config_map(self) -> Optional[KatMap]:
    if config_man.ns():
      return KatMap.find(cmap_name, self.ns())
    else:
      return None

  # noinspection PyTypedDict
  def resolvers(self) -> Dict[str, Callable]:
    def app_cont(n: str) -> str:
      return dict(
        install_uuid=self.install_uuid(),
        ns=self.ns()
      )[n]

    return dict(
      manifest_variables=lambda n: self.manifest_var(n),
      tam_config=lambda n: self.tam().get(n),
      prefs=lambda n: self.prefs().get(n),
      app=app_cont
    )

  def serialize(self):
    config_map = self.master_config_map()
    return config_map.raw.data if config_map else {}

  def read_config_map_dict(self, outer_key: str) -> Dict:
    config_map = self.master_config_map()
    return config_map.jget(outer_key, {}) if config_map else {}

  def read_config_map_primitive(self, flat_key: str) -> any:
    config_map = self.master_config_map()
    return config_map.data.get(flat_key) if config_map else None

  def patch_config_map(self, outer_key: str, value: any):
    config_map = self.master_config_map()
    config_map.raw.data[outer_key] = value
    config_map.touch(save=True)

  def set_last_updated(self, timestamp: datetime):
    self.patch_config_map(key_last_updated, str(timestamp))
    self._last_updated = None

  def patch_cmap_with_dict(self, outer_key: str, value: Dict):
    self.patch_config_map(outer_key, json.dumps(value))

  def read_tam(self) -> TamDict:
    return self.read_config_map_dict(tam_config_key)

  def read_prefs(self) -> TamDict:
    return self.read_config_map_dict(prefs_config_key)

  def write_tam(self, new_tam: TamDict):
    self.patch_cmap_with_dict(tam_config_key, new_tam)
    self._tam = None

  def patch_tam(self, partial_tam: TamDict):
    new_tam = {**self.tam(True), **partial_tam}
    self.write_tam(new_tam)

  def read_manifest_vars(self) -> Dict:
    return self.read_config_map_dict(tam_vars_key)

  def patch_manifest_defaults(self, assigns: Dict):
    new_defaults = {**self.read_manifest_defaults(), **assigns}
    self.write_manifest_defaults(new_defaults)

  def write_manifest_defaults(self, assigns: Dict):
    self.patch_cmap_with_dict(tam_defaults_key, assigns)
    self._tam_defaults = None

  def read_manifest_defaults(self) -> Dict:
    return self.read_config_map_dict(tam_defaults_key)

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

  def patch_keyed_manifest_vars(self, assignments: List[Tuple[str, any]]):
    self.patch_manifest_vars(utils.keyed2dict(assignments))

  def patch_manifest_vars(self, assignments: Dict[str, any]):
    merged = deep_merge(self.read_manifest_vars(), assignments)
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
  config_man._last_updated = None
  if utils.is_dev():
    with open(dev_ns_path, 'w') as file:
      file.write(new_ns)


def distant_past_timestamp() -> datetime:
  date_time_str = '2000-01-01 00:00:00.000000'
  fmt = '%Y-%m-%d %H:%M:%S.%f'
  return datetime.strptime(date_time_str, fmt)

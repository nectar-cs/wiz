import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Callable

from k8kat.auth.kube_broker import broker
from k8kat.res.config_map.kat_map import KatMap
from k8kat.utils.main.utils import deep_merge

from nectwiz.core.core import utils
from nectwiz.core.core.types import TamDict, WizDict

cmap_name = 'master'
install_uuid_path = '/etc/sec/install_uuid'
tam_config_key = 'tam'
wiz_config_key = 'wiz'
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
    self._master_cmap: Optional[KatMap] = None

  def ns(self, force_reload=False):
    if force_reload or utils.is_worker() or not self._ns:
      self._ns = read_ns()
    return self._ns

  def read_master_config_map(self, force_reload=False) -> Optional[KatMap]:
    if self.ns():
      if force_reload or utils.is_worker() or not self._master_cmap:
        self._master_cmap = KatMap.find(cmap_name, self.ns())
      if not self._master_cmap:
        print("[nectwiz::read_master_config_map] fatal: cmap is nil")
      return self._master_cmap
    else:
      print("[nectwiz::read_master_config_map] fatal: ns is nil")
      return None

  def read_dict(self, outer_key: str, force_reload=False) -> Dict:
    config_map = self.read_master_config_map(force_reload)
    return config_map.jget(outer_key, {}) if config_map else {}

  def read_primitive(self, flat_key: str, force_reload=False) -> any:
    config_map = self.read_master_config_map(force_reload)
    return config_map.data.get(flat_key) if config_map else None

  def patch_config_map(self, outer_key: str, value: any):
    config_map = self.read_master_config_map()
    config_map.raw.data[outer_key] = value
    config_map.touch(save=True)

  def patch_cmap_with_dict(self, outer_key: str, value: Dict):
    self.patch_config_map(outer_key, json.dumps(value))

  def prefs(self, force_reload=False) -> Dict:
    return self.read_dict(prefs_config_key, force_reload)

  def flat_prefs(self, force_reload=False) -> Dict:
    return utils.dict2flat(self.prefs(force_reload))

  def tam(self, force_reload=False) -> TamDict:
    return self.read_dict(tam_config_key, force_reload)

  def wiz(self, force_reload=False) -> WizDict:
    return self.read_dict(wiz_config_key, force_reload)

  def manifest_defaults(self, force_reload=False) -> Dict:
    return self.read_dict(tam_defaults_key, force_reload)

  def manifest_vars(self, force_reload=False) -> Dict:
    return self.read_dict(tam_vars_key, force_reload)

  def flat_manifest_vars(self, force_reload=False) -> Dict:
    return utils.dict2flat(self.manifest_vars(force_reload))

  def last_updated(self, force_reload=False) -> datetime:
    return self.read_primitive(key_last_updated, force_reload)

  def manifest_var(self, deep_key: str, reload=False) -> Optional[str]:
    return utils.deep_get2(self.manifest_vars(reload), deep_key)

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
    config_map = self.read_master_config_map()
    return config_map.raw.data if config_map else {}

  def patch_keyed_manifest_vars(self, assignments: List[Tuple[str, any]]):
    self.patch_manifest_vars(utils.keyed2dict(assignments))

  def patch_manifest_vars(self, assignments: Dict[str, any]):
    merged = deep_merge(self.manifest_vars(), assignments)
    self.patch_cmap_with_dict(tam_vars_key, merged)

  def write_last_synced(self, timestamp: datetime):
    self.patch_config_map(key_last_updated, str(timestamp))
    self._master_cmap = None

  def write_tam(self, new_tam: TamDict):
    self.patch_cmap_with_dict(tam_config_key, new_tam)
    self._master_cmap = None

  def patch_tam(self, partial_tam: TamDict):
    new_tam = {**self.tam(True), **partial_tam}
    self.write_tam(new_tam)

  def write_manifest_defaults(self, assigns: Dict):
    self.patch_cmap_with_dict(tam_defaults_key, assigns)
    self._master_cmap = None

  def patch_manifest_defaults(self, assigns: Dict):
    new_defaults = {**self.manifest_defaults(), **assigns}
    self.write_manifest_defaults(new_defaults)

  def install_uuid(self):
    if utils.is_prod() or broker.is_in_cluster_auth():
      try:
        with open(install_uuid_path, 'r') as file:
          return file.read()
      except FileNotFoundError:
        print(f"[nectwiz::config_man::install_uuid] {install_uuid_path} fnf")
        return None
    else:
      return self.prefs().get('install_uuid')


config_man = ConfigMan()


def read_ns() -> Optional[str]:
  path = None
  if broker.is_in_cluster_auth():
    path = ns_path
  elif utils.is_local_dev_server():
    path = dev_ns_path

  if path:
    with open(path, 'r') as file:
      return file.read()
  else:
    print("[nectwiz::configmap] ULTRA-FATAL no way to read ns")
    return None


def coerce_ns(new_ns):
  config_man._ns = new_ns
  config_man._tam = None
  config_man._install_uuid = None
  config_man._tam_defaults = None
  config_man._tam_vars = None
  config_man._last_updated = None
  if utils.is_local_dev_server():
    with open(dev_ns_path, 'w') as file:
      file.write(new_ns)


def distant_past_timestamp() -> datetime:
  date_time_str = '2000-01-01 00:00:00.000000'
  fmt = '%Y-%m-%d %H:%M:%S.%f'
  return datetime.strptime(date_time_str, fmt)

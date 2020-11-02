import json
import traceback
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Callable

from k8kat.res.config_map.kat_map import KatMap
from k8kat.utils.main.utils import deep_merge

from nectwiz.core.core import utils
from nectwiz.core.core.types import TamDict, WizDict

cmap_path = 'master_config'
cmap_name = 'master'
is_training_key = 'is_dev'
app_id_key = 'app_id'
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

  def ns(self, force_reload=False):
    if force_reload or utils.is_worker() or not self._ns:
      self._ns = read_ns()
    return self._ns

  def load_master_cmap(self) -> Optional[KatMap]:
    if self.ns():
      cmap = KatMap.find(cmap_name, self.ns())
      if not cmap:
        print("[nectwiz::read_master_config_map] fatal: cmap is nil")
      return cmap
    else:
      print("[nectwiz::read_master_config_map] fatal: ns is nil")
      return None

  def read_entry(self, key: str) -> any:
    if utils.is_in_cluster():
      with open(cmap_path, 'r') as file:
        return file.read()
    else:
      cmap = self.load_master_cmap()
      return cmap.raw.data.get(key) if cmap else None

  def read_dict(self, outer_key: str) -> Dict:
    raw_val = self.read_entry(outer_key) or '{}'
    return json.loads(raw_val)

  def patch_master_cmap(self, outer_key: str, value: any):
    config_map = self.load_master_cmap()
    config_map.raw.data[outer_key] = value
    config_map.touch(save=True)

  def patch_cmap_with_dict(self, outer_key: str, value: Dict):
    self.patch_master_cmap(outer_key, json.dumps(value))

  def app_id(self) -> str:
    return self.read_entry(app_id_key)

  def prefs(self) -> Dict:
    return self.read_dict(prefs_config_key)

  def flat_prefs(self) -> Dict:
    return utils.dict2flat(self.prefs())

  def tam(self) -> TamDict:
    return self.read_dict(tam_config_key)

  def wiz(self) -> WizDict:
    return self.read_dict(wiz_config_key)

  def manifest_defaults(self) -> Dict:
    return self.read_dict(tam_defaults_key)

  def manifest_vars(self) -> Dict:
    return self.read_dict(tam_vars_key)

  def flat_manifest_vars(self) -> Dict:
    return utils.dict2flat(self.manifest_vars())

  def last_updated(self) -> datetime:
    return self.read_entry(key_last_updated)

  def manifest_var(self, deep_key: str) -> Optional[str]:
    return utils.deep_get2(self.manifest_vars(), deep_key)

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
    config_map = self.load_master_cmap()
    return config_map.raw.data if config_map else {}

  def patch_keyed_manifest_vars(self, assignments: List[Tuple[str, any]]):
    self.patch_manifest_vars(utils.keyed2dict(assignments))

  def patch_manifest_vars(self, assignments: Dict[str, any]):
    merged = deep_merge(self.manifest_vars(), assignments)
    self.patch_cmap_with_dict(tam_vars_key, merged)

  def write_last_synced(self, timestamp: datetime):
    self.patch_master_cmap(key_last_updated, str(timestamp))

  def write_tam(self, new_tam: TamDict):
    self.patch_cmap_with_dict(tam_config_key, new_tam)

  def patch_tam(self, partial_tam: TamDict):
    new_tam = {**self.tam(), **partial_tam}
    self.write_tam(new_tam)

  def write_manifest_defaults(self, assigns: Dict):
    self.patch_cmap_with_dict(tam_defaults_key, assigns)

  def is_training_mode(self) -> bool:
    raw_val = self.read_entry(is_training_key)
    return raw_val in ['True', 'true', True]

  def is_real_deployment(self) -> bool:
    return not self.is_training_mode()

  def patch_manifest_defaults(self, assigns: Dict):
    new_defaults = {**self.manifest_defaults(), **assigns}
    self.write_manifest_defaults(new_defaults)

  def install_uuid(self) -> Optional[str]:
    if self.is_training_mode():
      print("[nectwiz:config_man:install_uuid] illegal req in training mode")
      return None

    if utils.is_in_cluster():
      try:
        with open(install_uuid_path, 'r') as file:
          return file.read()
      except FileNotFoundError:
        print(f"[nectwiz:config_man:install_uuid] {install_uuid_path} fnf")
        return None
    else:
      return self.read_entry('install_uuid')


config_man = ConfigMan()


def read_ns() -> Optional[str]:
  path = ns_path if utils.is_in_cluster() else dev_ns_path
  try:
    with open(path, 'r') as file:
      value = file.read()
      if not value:
        print(f"[nectwiz::configmap] FATAL ns empty at {path}")
      return file.read()
  except FileNotFoundError:
    print(f"[nectwiz::configmap] FATAL read failed")
    print(traceback.format_exc())
    return None


def coerce_ns(new_ns):
  config_man._ns = new_ns
  if utils.is_out_of_cluster():
    with open(dev_ns_path, 'w') as file:
      file.write(new_ns)
  else:
    print(f"[nectwiz::configman] illegal ns coerce!")


def distant_past_timestamp() -> datetime:
  date_time_str = '2000-01-01 00:00:00.000000'
  fmt = '%Y-%m-%d %H:%M:%S.%f'
  return datetime.strptime(date_time_str, fmt)

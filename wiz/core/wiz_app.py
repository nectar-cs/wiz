import base64
import os
from typing import Dict, Type, Optional, List

from k8_kat.res.secret.kat_secret import KatSecret

from wiz.core import utils

tami_pod_name = 'tami'
cache_root = '/tmp'
install_uuid_path = '/var/install_uuid'
dev_install_uuid_path = '/tmp/install_uuid'


def is_config_match(config: Dict, kind: str, key: str):
  """
  Finds the WizModel object definition inside of the passed config that matches
  the passed kind and key.
  :param config: vendor-provided app configuration, parsed from YAML to a dict.
  :param kind: desired kind to be matched with, eg Operation or Stage.
  :param key: desired key to be matched with, eg hub.backend.secrets.key_base.
  :return:
  """
  return config['kind'] == kind and config['key'] == key


def is_subclass_match(subclass, kind: str, key: str):
  """
  Checks if the passed subclass instance matches the passed kind and key.
  :param subclass: instance of a vendor defined subclass.
  :param kind: desired kind to be matched with, eg Operation or Stage.
  :param key: desired key to be matched with, eg hub.backend.secrets.key_base.
  :return: True if both kind and key match, else False.
  """
  from wiz.model.base.wiz_model import WizModel
  actual: Type[WizModel] = subclass
  return actual.type_key() == kind and actual.covers_key(key)


def default_configs() -> List[Dict]:
  """
  Gets the pre-built configs, converting from YAMLs to dicts.
  :return: dictionary containing pre-built configs.
  """
  pwd = os.path.join(os.path.dirname(__file__))
  return utils.yamls_in_dir(f"{pwd}/../model/pre_built")


def read_install_uuid_secret(ns):
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


class WizApp:

  def __init__(self):
    self.configs: List[Dict] = default_configs()
    self.subclasses: List[Type] = []
    self.providers = []
    self.adapters = []
    self.app_name: Optional[str] = None
    self.ns: Optional[str] = None
    self.install_uuid: Optional[str] = None
    self.tami_name: Optional[str] = None
    self.tami_args: Optional[str] = None

  def reload_install_uuid(self):
    if self.ns and not self.install_uuid:
      self.install_uuid = read_install_uuid_secret(self.ns)

  def reload_tami_name(self):
    from wiz.core import tami_client
    self.tami_name = tami_client.read_tami_name()

  def add_configs(self, new_configs: List[Dict]):
    """
    Appends new configs to the list of existing ones.
    :param new_configs: list of new configs.
    """
    self.configs = self.configs + new_configs

  def add_overrides(self, new_overrides:List):
    """
    Appends new overrides to the list of existing ones.
    :param new_overrides: list of new overrides.
    """
    self.subclasses += new_overrides

  def add_adapters(self, new_adapters:List):
    """
    Appends new adapters to the list of existing ones.
    :param new_adapters: list of new adapters.
    """
    self.adapters += new_adapters

  def add_providers(self, new_providers):
    """
    Appends new providers to the list of existing ones.
    :param new_providers: list of new providers.
    """
    self.providers += new_providers

  def find_provider(self, adapter_class: Type):
    """
    Finds the provider with the matching adapter class among providers list.
    :param adapter_class: desired adapter class.
    :return: matched provider or None if not found.
    """
    matches = [c for c in self.providers if c.kind() == adapter_class]
    return matches[0] if len(matches) > 0 else None

  def find_adapter_subclass(self, superclass: Type, else_super=False):
    """
    Finds the adapter with the matching superclass among the adapters list.
    :param superclass: desired superclass.
    :param else_super: True or False parameter that dictates whether to return
    the superclass itself, if adapter not found.
    :return: matched adapter or superclass / None if not found.
    """
    matches = [c for c in self.adapters if issubclass(c, superclass)]
    backup = superclass if else_super else None
    return matches[0] if len(matches) > 0 else backup

  def find_config(self, kind: str, key: str):
    """
    Finds the default config that matches the passed kind and key.
    :param kind: desired kind to be matched with, eg Operation or Stage.
    :param key: desired key to be matched with, eg hub.backend.secrets.key_base.
    :return: config dict if found, else None.
    """
    matches = [c for c in self.configs if is_config_match(c, kind, key)]
    return matches[0] if len(matches) else None

  def configs_of_kind(self, kind: str):
    """
    Selects parts of config that match the provided kind.
    :param kind: desired kind, eg Operation, Stage, Step, Predicate.
    :return: List of operations of desired kind.
    """
    return [c for c in self.configs if c['kind'] == kind]

  def find_subclass(self, kind: str, key: str) -> Optional[Type]:
    """
    Finds the subclass instance that matches the passed kind and key, if such exists.
    :param kind: desired kind to be matched with, eg Operation or Stage.
    :param key: desired key to be matched with, eg hub.backend.secrets.key_base.
    :return: subclass instance if found, else None.
    """
    predicate = lambda klass: is_subclass_match(klass, kind, key)
    return next((c for c in self.subclasses if predicate(c)), None)

  def clear(self):
    """
    Resets configs and clears out subclasses.
    """
    self.configs = default_configs()
    self.subclasses = []


wiz_app = WizApp()

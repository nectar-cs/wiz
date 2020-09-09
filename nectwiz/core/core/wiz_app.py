import os
from typing import Dict, Type, Optional, List

from nectwiz.core.core import utils
from nectwiz.core.core.types import TamDict

tami_pod_name = 'tami'
cache_root = '/tmp'


def is_config_match(config: Dict, kind: str, _id: str):
  """
  Finds the WizModel object definition inside of the passed config that matches
  the passed kind and key.
  :param config: vendor-provided app configuration, parsed from YAML to a dict.
  :param kind: desired kind to be matched with, eg Operation or Stage.
  :param _id: desired key to be matched with, eg hub.backend.secrets.key_base.
  :return:
  """
  return config['kind'] == kind and config['id'] == _id


def is_subclass_match(subclass, kind: str, _id: str):
  """
  Checks if the passed subclass instance matches the passed kind and key.
  :param subclass: instance of a vendor defined subclass.
  :param kind: desired kind to be matched with, eg Operation or Stage.
  :param _id: desired key to be matched with, eg hub.backend.secrets.key_base.
  :return: True if both kind and key match, else False.
  """
  from nectwiz.model.base.wiz_model import WizModel
  actual: Type[WizModel] = subclass
  return actual.type_key() == kind and actual.covers_key(_id)


def default_configs() -> List[Dict]:
  """
  Gets the pre-built configs, converting from YAMLs to dicts.
  :return: dictionary containing pre-built configs.
  """
  pwd = os.path.join(os.path.dirname(__file__))
  return utils.yamls_in_dir(f"{pwd}/../../model/pre_built")


class WizApp:

  def __init__(self):
    self.configs: List[Dict] = default_configs()
    self.subclasses: List[Type] = []
    self.tam_client_override = None
    self.providers = []
    self.adapters = []

    self._ns: Optional[str] = None
    self._tam: Optional[TamDict] = None
    self._install_uuid: Optional[str] = None
    self._tam_defaults: Optional[Dict] = None
    self._tam_vars: Optional[Dict] = None
    
  def ns(self, force_reload=False):
    if force_reload or not self._ns:
      from nectwiz.core.core import config_man
      self._ns = config_man.read_ns()
    return self._ns

  def tam(self, force_reload=False) -> TamDict:
    if force_reload or not self._tam:
      from nectwiz.core.core import config_man
      self._tam = config_man.read_tam()
    return self._tam

  def tam_defaults(self, force_reload=False) -> Dict:
    if force_reload or not self._tam_defaults:
      from nectwiz.core.core import config_man
      self._tam_defaults = config_man.read_tam_var_defaults()
    return self._tam_defaults

  def tam_vars(self, force_reload=False) -> Dict:
    if force_reload or not self._tam_vars:
      from nectwiz.core.core import config_man
      self._tam_vars = config_man.read_tam_vars()
    return self._tam_vars

  def change_tam_version(self, new_tam_version: str):
    from nectwiz.core.core import config_man
    updated_tam = { **wiz_app.tam(), 'ver': new_tam_version }
    config_man.write_tam(updated_tam)
    self._tam = config_man.read_tam()

  def install_uuid(self, force_reload=False) -> str:
    if self.ns() and (force_reload or not self.install_uuid):
      from nectwiz.core.core import config_man
      self._install_uuid = config_man.read_install_uuid(self.ns())
    return self._install_uuid

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

  def find_subclass(self, kind: str, _id: str) -> Optional[Type]:
    """
    Finds the subclass instance that matches the passed kind and key, if such exists.
    :param kind: desired kind to be matched with, eg Operation or Stage.
    :param _id: desired key to be matched with, eg hub.backend.secrets.key_base.
    :return: subclass instance if found, else None.
    """
    predicate = lambda klass: is_subclass_match(klass, kind, _id)
    return next((c for c in self.subclasses if predicate(c)), None)

  def clear(self, restore_defaults=True):
    """
    Resets configs and clears out subclasses.
    """
    self.configs = default_configs() if restore_defaults else []
    self.subclasses = []


wiz_app = WizApp()
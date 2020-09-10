import os
from typing import Dict, Type, Optional, List

from nectwiz.core.core import utils
from nectwiz.core.core.types import TamDict

tami_pod_name = 'tami'
cache_root = '/tmp'


def default_configs() -> List[Dict]:
  """
  Gets the pre-built configs, converting from YAMLs to dicts.
  :return: dictionary containing pre-built configs.
  """
  pwd = os.path.join(os.path.dirname(__file__))
  return utils.yamls_in_dir(f"{pwd}/../../model/pre_built")




class WizApp:

  def __init__(self):
    self.configs: List[Dict] = []
    self.subclasses: List[Type] = []
    self.tam_client_override = None
    self.providers = []
    self.adapters = []
    self.jobs_backend = 'rq'

    self.clear()
    
  def uses_rq(self):
    return self.jobs_backend == 'rq'

  def uses_sync(self):
    return self.jobs_backend == 'sync'

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

  def clear(self, restore_defaults=True):
    """
    Resets configs and clears out subclasses.
    """
    from nectwiz.model.pre_built.cmd_exec_action import CmdExecAction
    self.configs = default_configs() if restore_defaults else []
    self.subclasses = [CmdExecAction]


wiz_app = WizApp()

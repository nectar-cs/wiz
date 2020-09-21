from typing import Optional, List, TypeVar

from nectwiz.core.core import config_man, utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.utils import dict2keyed
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.variables.generic_variable import GenericVariable

T = TypeVar('T', bound='ManifestVariable')

class ManifestVariable(GenericVariable):
  def __init__(self, config):
    super().__init__(config)
    self.mode: str = config.get('mode', 'internal')
    self.release_overridable: bool = config.get('release_overridable', False)

  def default_value(self) -> str:
    hardcoded = super().default_value()
    if hardcoded:
      return hardcoded
    return config_man.tam_defaults().get(self.id())

  def is_safe_to_set(self) -> bool:
    return self.mode == 'public'

  def read_crt_value(self, force_reload=False) -> Optional[str]:
    root = config_man.mfst_vars(force_reload)
    return utils.deep_get(root, self.id().split('.'))

  def commit(self, value: str):
    config_man.commit_keyed_mfst_vars([(self.id(), value)])
    if self.is_safe_to_set():
      tam_client().apply(rules=None, inlines=None)

  def operations(self):
    from nectwiz.model.operations.operation import Operation
    return self.load_children('operations', Operation)

  @classmethod
  def all_vars(cls) -> List[T]:
    raw = config_man.mfst_vars(force_reload=True)
    committed_vars = dict2keyed(raw)
    models = cls.inflate_all()
    pres = lambda k: len([cv for cv in models if cv.id() == k]) > 0
    for committed_var in committed_vars:
      key = committed_var[0]
      if not pres(key):
        models.append(ManifestVariable(dict(id=key)))
    return models

  @classmethod
  def release_dpdt_vars(cls) -> List[T]:
    matcher = lambda cv: cv.release_overridable
    return list(filter(matcher, ManifestVariable.inflate_all()))

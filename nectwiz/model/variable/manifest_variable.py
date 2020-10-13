from typing import Optional, List, TypeVar

from nectwiz.core.core.types import PredEval

from nectwiz.core.core import config_man, utils, hub_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.utils import dict2keyed
from nectwiz.model.variable.generic_variable import GenericVariable


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
    else:
      defaults = config_man.manifest_defaults()
      return utils.deep_get2(defaults, self.id())

  def is_safe_to_set(self) -> bool:
    return self.mode == 'public'

  def read_crt_value(self, force_reload=False) -> Optional[str]:
    root = config_man.flat_manifest_vars(force_reload)
    return root.get(self.id())

  def is_currently_valid(self, force_reload=False) -> bool:
    self.read_crt_value(force_reload)
    if self.is_defined() and len(self.validators()) > 0:
      crt_val = self.read_crt_value()
      context = dict(resolvers=config_man.resolvers())
      pred_eval: PredEval = self.validate(crt_val, context)
      return pred_eval['met']
    else:
      return True

  def is_defined(self) -> bool:
    root = config_man.flat_manifest_vars()
    return self.id() in root.keys()

  @classmethod
  def all_vars(cls) -> List[T]:
    raw = config_man.manifest_variables(force_reload=True)
    committed_vars = dict2keyed(raw)
    models = cls.inflate_all()
    pres = lambda k: len([cv for cv in models if cv.id() == k]) > 0
    for committed_var in committed_vars:
      key = committed_var[0]
      if not pres(key):
        models.append(cls.synthesize_var_model(key))
    return models

  @classmethod
  def release_dpdt_vars(cls) -> List[T]:
    matcher = lambda cv: cv.release_overridable
    return list(filter(matcher, ManifestVariable.inflate_all()))

  @classmethod
  def inject_server_defaults(cls) -> bool:
    install_uuid = config_man.install_uuid(force_reload=True)
    if install_uuid:
      route = f'/installs/{install_uuid}/injections'
      resp = hub_client.get(route)
      if resp.status_code < 300:
        injections = resp.json().get('data')
        if injections:
          config_man.commit_mfst_vars(injections)
          return True
    return False

  # noinspection PyBroadException
  @classmethod
  def find_or_synthesize(cls, key):
    try:
      return cls.inflate(key)
    except:
      return cls.synthesize_var_model(key)

  @staticmethod
  def synthesize_var_model(key: str):
    return ManifestVariable.inflate(dict(
      id=key,
      mode='unlisted',
      title=f'Undocumented Variable {key}',
      info=f'Undocumented Variable {key}'
    ))

from typing import Optional, List, TypeVar

from werkzeug.utils import cached_property

from nectwiz.core.core import config_man, utils, hub_api_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.utils import dict2keyed
from nectwiz.model.variable.generic_variable import GenericVariable

T = TypeVar('T', bound='ManifestVariable')


class ManifestVariable(GenericVariable):

  RELEASE_OVERRIDE_KEY = 'release_overridable'
  MODE_KEY = 'mode'
  TAGS_KEY = 'tags'

  @cached_property
  def mode(self):
    return self.get_prop(self.MODE_KEY, 'internal')

  @cached_property
  def release_overridable(self):
    return self.get_prop(self.RELEASE_OVERRIDE_KEY, False)

  @cached_property
  def tags(self):
    return self.get_prop(self.TAGS_KEY, [])

  def default_value(self, reload=True) -> str:
    hardcoded = super().default_value()
    if hardcoded:
      return hardcoded
    else:
      defaults = config_man.manifest_defaults(reload)
      return utils.deep_get2(defaults, self.id())

  def is_safe_to_set(self) -> bool:
    return self.mode == 'public'

  def current_value(self, reload=True) -> Optional[str]:
    return config_man.manifest_var(self.id(), reload)

  def current_or_default_value(self):
    return self.current_value() or self.default_value

  def is_currently_valid(self) -> bool:
    root = config_man.flat_manifest_vars()
    is_defined = self.id() in root.keys()
    crt_val = root.get(self.id())
    return self.validate(crt_val)['met'] if is_defined else True

  @classmethod
  def all_vars(cls) -> List[T]:
    raw = config_man.manifest_vars()
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
    install_uuid = config_man.install_uuid()
    if install_uuid:
      route = f'/installs/{install_uuid}/injections'
      resp = hub_api_client.get(route)
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

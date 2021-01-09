from typing import Optional, List, TypeVar

from werkzeug.utils import cached_property

from nectwiz.core.core import config_man, utils, hub_api_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.utils import dict2keyed
from nectwiz.model.variable.generic_variable import GenericVariable

T = TypeVar('T', bound='ManifestVariable')


class ManifestVariable(GenericVariable):

  RELEASE_OVERRIDE_KEY = 'publisher_overridable'
  MODE_KEY = 'mode'
  TAGS_KEY = 'tags'

  @cached_property
  def mode(self):
    return self.get_prop(self.MODE_KEY, 'internal')

  @cached_property
  def is_publisher_overridable(self):
    return self.get_prop(self.RELEASE_OVERRIDE_KEY, False)

  @cached_property
  def tags(self):
    return self.get_prop(self.TAGS_KEY, [])

  @cached_property
  def default_value(self) -> str:
    hardcoded = super().default_value
    if hardcoded:
      return hardcoded
    else:
      defaults = config_man.manifest_defaults()
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
  def publisher_overridable_vars(cls) -> List[T]:
    matcher = lambda cv: cv.is_publisher_overridable
    return list(filter(matcher, ManifestVariable.inflate_all()))

  @staticmethod
  def inject_server_defaults() -> bool:
    route = f'/installs/injections'
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
  def find_or_synthesize(cls, manifest_variable_id) -> T:
    try:
      return cls.inflate(manifest_variable_id)
    except:
      return cls.synthesize_var_model(manifest_variable_id)

  @staticmethod
  def synthesize_var_model(key: str):
    return ManifestVariable.inflate({
      'id': key,
      ManifestVariable.MODE_KEY: 'unlisted',
      ManifestVariable.TITLE_KEY: f'Undocumented Variable {key}',
      ManifestVariable.INFO_KEY: f'Undocumented Variable {key}'
    })

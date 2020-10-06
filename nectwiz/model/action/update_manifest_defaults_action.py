from typing import Dict

from nectwiz.core.core import utils
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateDict
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.core.telem.updates_man import updated_release_tam
from nectwiz.model.action.action_observer import Observer
from nectwiz.model.variables.manifest_variable import ManifestVariable


class UpdateManifestDefaultsActionPart:

  @staticmethod
  def progress_items():
    return [
      dict(
        id='update_defaults',
        status='idle',
        title='Update Defaults',
        info='Write new manifest defaults',
        sub_items=[]
      )
    ]

  @classmethod
  def perform(cls, observer: Observer, update_dict: UpdateDict):
    update_type = update_dict.get('type')
    if update_type in ['release', 'update']:
      if update_type == 'release':
        cls.perform_release(update_dict)
      elif update_type == 'update':
        cls.perform_injection_update(update_dict)
      cls.on_mfst_vars_committed(observer)
    else:
      observer.process_error(
        fatal=True,
        event_type='update_defaults',
        code='unrecognized-update-type',
        update_type=update_dict.get('type'),
      )

  @classmethod
  def perform_release(cls, update_dict: UpdateDict):
    config_man.patch_tam(updated_release_tam(update_dict))
    new_manifest_defaults = tam_client().load_manifest_defaults()
    overwritten_vars = compute_overwritten_vars(new_manifest_defaults)
    config_man.patch_keyed_manifest_vars(overwritten_vars)
    config_man.patch_manifest_defaults(new_manifest_defaults)

  @classmethod
  def perform_injection_update(cls, update_dict: UpdateDict):
    keyed_or_nested_asgs: Dict = update_dict.get('injections', {})
    keyed = utils.dict2keyed(keyed_or_nested_asgs)
    nested = utils.keyed2dict(keyed)
    config_man.patch_manifest_defaults(nested)
    config_man.patch_manifest_vars(nested)
    return tam_client().apply([])

  @classmethod
  def on_mfst_vars_committed(cls, observer: Observer):
    observer.set_item_status('update_defaults', 'positive')

def compute_overwritten_vars(manifest_defaults: Dict):
  target_var_ids = [cv.id() for cv in ManifestVariable.release_dpdt_vars()]
  new_keyed_defaults = utils.dict2keyed(manifest_defaults)
  return [e for e in new_keyed_defaults if e[0] in target_var_ids]

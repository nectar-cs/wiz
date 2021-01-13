from datetime import datetime
from typing import Dict, List, Optional

from nectwiz.core.core import hub_api_client
from nectwiz.core.core.config_man import config_man
from nectwiz.core.core.types import UpdateDict
from nectwiz.core.core.utils import deep_merge
from nectwiz.core.tam.tam_provider import tam_client
from nectwiz.model.adapters.mock_update \
  import MockUpdate, next_mock_update_id
from nectwiz.model.hook.hook import Hook

TYPE_RELEASE = 'release'
TYPE_UPDATE = 'update'


def fetch_next_update() -> Optional[UpdateDict]:
  config_man.write_last_update_checked(str(datetime.now()))
  return None


def fetch_update(update_id: str) -> Optional[UpdateDict]:
  if config_man.is_real_deployment():
    resp = hub_api_client.get(f'/app_updates/{update_id}')
    if resp.ok:
      return resp.json()['bundle']
    else:
      print(f"[nectwiz::updates_man] err requesting update {resp.status_code}")
  else:
    model = MockUpdate.inflate(update_id)
    return model.as_bundle()


def next_available() -> Optional[UpdateDict]:
  if config_man.is_real_deployment():
    resp = hub_api_client.get(f'/app_updates/available')
    data = resp.json() if resp.status_code < 205 else None
    return data['bundle'] if data else None
  else:
    model = MockUpdate.inflate(next_mock_update_id)
    return model.as_bundle()


def _gen_injection_telem(keys: List[str]):
  all_vars = config_man.manifest_vars()
  return {k: all_vars[k] for k in keys}


def find_hooks(timing: str, update: UpdateDict) -> List[Hook]:
  return Hook.by_trigger(
    event='software-update',
    timing=timing,
    **update
  )


def preview(update_dict: UpdateDict) -> Dict:
  old_defaults = config_man.manifest_defaults()
  old_manifest = tam_client().template_manifest_std()

  new_tam = updated_release_tam(update_dict)
  new_tam_client = tam_client(tam=new_tam)

  new_defaults = new_tam_client.load_default_values()
  new_manifest_vars = deep_merge(new_defaults, config_man.manifest_vars())
  new_manifest = new_tam_client.template_manifest(new_manifest_vars)

  return dict(
    defaults=dict(
      old=old_defaults,
      new=new_defaults
    ),
    manifest=dict(
      old=old_manifest,
      new=new_manifest
    )
  )


def commit_new_tam(update_dict: UpdateDict):
  new_tam = updated_release_tam(update_dict)
  config_man.patch_tam(new_tam)


def commit_new_defaults(update_dict: UpdateDict):
  new_tam = updated_release_tam(update_dict)
  new_defaults = tam_client(tam=new_tam).load_default_values()
  config_man.patch_manifest_defaults(new_defaults)


def updated_release_tam(update: UpdateDict) -> Dict:
  tam = dict(version=update['version'])
  if update.get('tam_type'):
    tam['type'] = update.get('tam_type')
  if update.get('tam_uri'):
    tam['uri'] = update.get('tam_uri')
  return {**config_man.tam(), **tam}
